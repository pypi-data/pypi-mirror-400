import queue
import threading
import time
import zlib
from collections import deque
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from statistics import median

from reedsolo import ReedSolomonError
from scipy.signal import hilbert, butter, sosfiltfilt, resample_poly

from scipy.io import wavfile
import soundfile

from conversions import *
from decode_frames import decode_frames
from values import *
from RSC import *
import numpy as np
# import sounddevice as sd


@dataclass
class Chunk:
	stream_id: str
	start_abs: int          # absolute sample index for this source stream
	samples: np.ndarray     # float32

class SourceBuffer:
	def __init__(self, overlap: int):
		self.total = 0
		self.parts = deque()
		self.overlap = overlap

	def append(self, x: np.ndarray):
		x = np.asarray(x, dtype=np.float32)

		self.parts.append(x)
		self.total += len(x)

	def available_abs_end(self) -> int:
		return self.total - 2 * self.overlap

	def pop_slice(self, size) -> np.ndarray:
		abs_start = 0
		abs_end = size + self.overlap * 2

		need = abs_end - abs_start

		if need > self.total:
			raise IndexError("slice not available yet")

		out = np.empty(need, dtype=np.float32)
		w = 0

		while self.parts and w < need:
			if len(self.parts[0]) <= need - w - 2 * self.overlap:
				seg = self.parts.popleft()
				out[w:w+len(seg)] = seg
				w += len(seg)
			else:
				seg = self.parts[0][:need - w]
				out[w:w+len(seg)] = seg
				self.parts[0] = self.parts[0][need - w - 2 * self.overlap:]
				w += len(seg)

		self.total -= need - 2 * self.overlap
		return out


class AsyncDecodeManager:
	def __init__(self, block_sec=3.0, overlap_sec=0.1):
		self.block_samples_len = int(round(SAMPLE_RATE * block_sec))
		self.overlap_samples_len = int(round(SAMPLE_RATE * overlap_sec))
		self.buffer = np.array([], dtype=np.float32)
		self.frames_payload = {}
		self.total_expected = None
		self.lock = threading.Lock()
		self.rsc_error = 0
		self.header_error = 0
		self.crc_error = 0
		self.duplicate_frames = 0

		self.no_lock = 0
		self.rsc_error = 0
		self.header_error = 0
		self.crc_error = 0

		self.buffers: dict[str, SourceBuffer] = {}
		self.next_block_start: dict[str, int] = {}

		self.queue = queue.Queue(maxsize=2000)
		self.executor = ThreadPoolExecutor(max_workers=32)
		self.limit = threading.BoundedSemaphore(32)

		self._stop = threading.Event()
		self._thread = threading.Thread(target=self._run, daemon=True)

		self.max_keep = 5 * self.block_samples_len + 3 * self.overlap_samples_len

	def start(self):

		self._stop = threading.Event()
		self._thread.start()

	def stop(self):
		self._stop.set()
		self._thread.join()
		self.executor.shutdown(wait=True)

	def push_chunk(self, chunk):
		# If you have sources with different fs: resample here to target_fs (not shown)
		self.queue.put(chunk)

	def _ensure_stream(self, stream_id: str):
		if stream_id not in self.buffers:
			self.buffers[stream_id] = SourceBuffer(overlap=self.overlap_samples_len)
			self.next_block_start[stream_id] = 0

	def _run(self):
		while not self._stop.is_set():
			try:
				chunk = self.queue.get(timeout=0.1)
			except queue.Empty:
				time.sleep(0.1)
				continue

			try:
				self._ensure_stream(chunk.stream_id)
				sb = self.buffers[chunk.stream_id]
				sb.append(chunk.samples)
				self._schedule_ready(chunk.stream_id)
			finally:
				self.queue.task_done()

	def _schedule_ready(self, stream_id: str):
		sb = self.buffers[stream_id]
		next = self.next_block_start[stream_id]

		while True:
			start = max(0, next - self.overlap_samples_len)
			end = start + self.block_samples_len + 2 * self.overlap_samples_len

			# start = max(0, next)
			# end = start + self.block_samples_len

			if sb.available_abs_end() < self.block_samples_len:
				break  # not enough samples yet

			rx_block = sb.pop_slice(self.block_samples_len)

			# submit decode job
			# self.limit.acquire()
			fut = self.executor.submit(
				self._decode_one,
				rx_block, stream_id, start, end
			)
			fut.add_done_callback(self._merge_result)

			# advance to next valid block (no overlap in valid regions)
			next += self.block_samples_len
			self.next_block_start[stream_id] = next

	def _decode_one(self, rx_block, stream_id: str, start, end):
		frames_block, total_expected, ok_log, no_lock, rsc_error, header_error, crc_error = decode_frames(
			rx_block, SAMPLE_RATE,
			search_step=SAMPLES_PER_SYMBOL, quick=True
		)
		return (frames_block, total_expected, ok_log, no_lock, rsc_error, header_error, crc_error, stream_id, start, end)

	def _merge_result(self, fut):
		# self.limit.release()
		payloads, total, ok_log, no_lock, rsc_error, header_error, crc_error, stream_id, start, end = fut.result()
		with self.lock:
			if total is not None and self.total_expected is None:
				self.total_expected = total

			for seq, payload in payloads.items():
				self.no_lock += no_lock
				self.rsc_error += rsc_error
				self.header_error += header_error
				self.crc_error += crc_error

				if seq not in self.frames_payload:
					self.frames_payload[seq] = payload
				else:
					self.duplicate_frames += 1

			print(f"\rBlock(Sample): {end // self.block_samples_len}/{self.buffers[stream_id].available_abs_end() // self.block_samples_len}({end}/{self.buffers[stream_id].available_abs_end()})  Frames: {len(self.frames_payload)}(+{self.duplicate_frames})/{self.total_expected}  no_lock: {self.no_lock} rsc_error: {self.rsc_error} header_error: {self.header_error} crc_error: {self.crc_error}", end='')


def feed_wav(manager: AsyncDecodeManager, stream_id: str, path: str, chunk_size=16000):
	# fs, rx = wavfile.read(path)
	rx, fs = soundfile.read(path, dtype='float32')
	rx = rx.astype(np.float32)
	pos = 0
	while pos < len(rx):
		x = rx[pos:pos+chunk_size]
		manager.push_chunk(Chunk(stream_id=stream_id, start_abs=pos, samples=x))
		pos += len(x)
	manager.push_chunk(Chunk(stream_id, start_abs=pos, samples=np.zeros((manager.block_samples_len + manager.overlap_samples_len,), dtype=np.float32)))


file = "bmp"

# fs_in, rx = wavfile.read(f"{file}.wav")
# rx = rx.astype(np.float32)

# assert fs_in == SAMPLE_RATE, f"Expected sample rate {SAMPLE_RATE}, got {fs_in}"

manager = AsyncDecodeManager()
manager.start()

# sample_pos = 0
# def callback(indata, frames, time_info, status):
# 	if status:
# 		print(status, flush=True)
#
# 	global sample_pos
# 	manager.push_chunk(Chunk(stream_id="mic", start_abs=sample_pos, samples=indata[:, 0].copy()))
# 	sample_pos += indata[:, 0].shape[0]
#
# stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', blocksize=4096, callback=callback)
#
# stream.start()
#
# while True:
# 	time.sleep(1)

feed_wav(manager, "wav", f"{file}.wav")
print("read wav")
# feed_wav(manager, "wav1", f"{file}1.wav")

manager.queue.join()
manager.stop()

exit(0)

frames_payload = {}
no_lock = 0
rsc_error = 0
header_error = 0
crc_error = 0


fs_block_size = SAMPLE_RATE * 5

for i in range(0, len(rx), fs_block_size):
	start = max(0, int(i - fs_block_size * 0.1))
	end = min(len(rx), int(i + fs_block_size * 1.1))

	block = rx[start : end]
	frames_block, total_expected, okl1, no_lock1, rsc_error1, header_error1, crc_error1 = decode_frames(block, SAMPLE_RATE, search_step=SAMPLES_PER_SYMBOL, quick=True)
	frames_payload.update(frames_block)
	no_lock += no_lock1
	rsc_error += rsc_error1
	header_error += header_error1
	crc_error += crc_error1
	print(f"\rBlock(Sample): {end // fs_block_size}/{len(rx) // fs_block_size}({end}/{len(rx)})  Frames: {len(frames_payload)}/{total_expected}  no_lock: {no_lock} rsc_error: {rsc_error} header_error: {header_error} crc_error: {crc_error}", end='')

print()

for i in range(0, total_expected):
	if i not in frames_payload:
		print(f"Pre missing frame {i}")
		continue

if (len(frames_payload) < 20):
	raise RuntimeError(f"Too few frames decoded in pass1 ({len(okl1)}). Can't estimate drift.")


best = {}
for seq, start, score in okl1:
	if (seq not in best) or (score > best[seq][1]):
		best[seq] = (start, score)

seqs = np.array(sorted(best.keys()), dtype=np.float64)
starts = np.array([best[int(start)][0] for start in seqs], dtype=np.float64)

A = np.vstack([seqs, np.ones_like(seqs)]).T
b_slope, a_off = np.linalg.lstsq(A, starts, rcond=None)[0]

pattern_len = len(np.array(PREAMBLE_STEPS[1:] + SYNCWORD_STEPS, dtype=np.int32))
payload_steps_len = (N * 8) // BITS_PER_SYMBOL
frame_steps = pattern_len + payload_steps_len + 1
frame_samples_expected = frame_steps * SAMPLES_PER_SYMBOL + 72


scale = frame_samples_expected / b_slope
frac = Fraction(scale).limit_denominator(10000)
print("estimated scale:", scale, "resample:", frac.numerator, "/", frac.denominator)

rx2 = resample_poly(rx, frac.numerator, frac.denominator).astype(np.float32)
# fs2 = SAMPLE_RATE * frac.numerator / frac.denominator
# print("effective fs:", fs2)

ok_log = okl1
# frames_payload, total_expected, ok_log = decode_frames(rx2, SAMPLE_RATE)

data = reconstruct_data(frames_payload, total_expected)

open(f"out.{file}", 'wb').write(data)

print("Total frames expected:", total_expected)
print("Frames received:", len(frames_payload))
print("Output CRC32: ", zlib.crc32(open(f"out.{file}", 'rb').read()))
