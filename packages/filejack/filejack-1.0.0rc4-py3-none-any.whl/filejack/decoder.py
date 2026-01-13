import threading
import time
import zlib
from fractions import Fraction
from statistics import median

from reedsolo import ReedSolomonError
from scipy.io import wavfile
from scipy.signal import hilbert, butter, sosfiltfilt, resample_poly
import threading as th
from conversions import *
from decode_frames import decode_frames
from reconstruct_data import reconstruct_data
from merge_frames import save_fjf
from values import *
from RSC import *
import numpy as np


frames_payload = {}
total_expected: int | None = None
samples_done = 0
no_lock = 0
rsc_error = 0
header_error = 0
crc_error = 0
limit = threading.BoundedSemaphore(12)
lock = threading.Lock()
fs_block_size = SAMPLE_RATE * 5


file = "7z2"

fs_in, rx = wavfile.read(f"{file}.wav")
rx = rx.astype(np.float32)

assert fs_in == SAMPLE_RATE, f"Expected sample rate {SAMPLE_RATE}, got {fs_in}"

def decode_block(block: np.ndarray):
	try:
		frames_block, total_expected1, okl1, no_lock1, rsc_error1, header_error1, crc_error1 = decode_frames(block, SAMPLE_RATE, search_step=SAMPLES_PER_SYMBOL, quick=True)
		with lock:
			frames_payload.update(frames_block)

			global total_expected
			total_expected = total_expected or total_expected1

			global samples_done
			samples_done += len(block) - int(SAMPLE_RATE * 0.2)

			global no_lock, rsc_error, header_error, crc_error
			no_lock += no_lock1
			rsc_error += rsc_error1
			header_error += header_error1
			crc_error += crc_error1

			print(f"\rBlock(Sample): {samples_done // fs_block_size}/{len(rx) // fs_block_size}({samples_done}/{len(rx)})  Frames: {len(frames_payload)}/{total_expected}  no_lock: {no_lock} rsc_error: {rsc_error} header_error: {header_error} crc_error: {crc_error}", end='')
	except Exception as e:
		print(f"\nError in thread: {e}")
	finally:
		limit.release()

threads: list[threading.Thread] = []

for i in range(0, len(rx), fs_block_size):
	start = max(0, int(i - SAMPLE_RATE * 0.1))
	end = min(len(rx), int(i + fs_block_size + SAMPLE_RATE * 0.1))

	block = rx[start : end]

	thread = threading.Thread(target=decode_block, args=(block,))
	thread.start()
	threads.append(thread)
	limit.acquire()

	threads = [t for t in threads if t.is_alive()]

while len(threads) > 0:
	threads[0].join()
	threads.pop(0)

print()

save_fjf(total_expected, frames_payload, f"{file}.fjf")

data = reconstruct_data(frames_payload, total_expected)

open(f"out.{file}", 'wb').write(data)

print("Total frames expected:", total_expected)
print("Frames received:", len(frames_payload))
print("Output CRC32: ", zlib.crc32(open(f"out.{file}", 'rb').read()))