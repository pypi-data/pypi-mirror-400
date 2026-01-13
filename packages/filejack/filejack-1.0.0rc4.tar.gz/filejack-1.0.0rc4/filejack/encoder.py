import struct
import zlib
import numpy as np
import scipy
from scipy.io import wavfile

from conversions import *
from values import *
from RSC import *


file = "bmp"


data = open(f"in.{file}", 'rb').read()

def chunk_bytes(b: bytes):
	for i in range(0, len(b), MAX_PAYLOAD):
		yield b[i:i+MAX_PAYLOAD]

chunks = list(chunk_bytes(data))

frames = []
for seq, payload in enumerate(chunks):
	hdr = struct.pack(HDR_FMT, seq, len(chunks), len(payload))
	crc = zlib.crc32(hdr + payload) & 0xFFFFFFFF
	crc_b = struct.pack('>I', crc)

	frame = hdr + payload + crc_b
	frame += b"\x00" * (K - len(frame))

	codeword = RSC.encode(frame)
	frames.append(codeword)

cursor = 0
all_samples = []
for cw in frames:
	payload_steps = bytes_to_symbols(cw)

	steps = np.concatenate([PREAMBLE_STEPS, SYNCWORD_STEPS, payload_steps % PSK])
	steps = np.array(steps, dtype=np.int32)

	diff = np.cumsum(steps) % PSK
	amp_idx = (payload_steps / PSK).astype(np.int32)

	amplitudes = ASK_LEVELS[amp_idx]

	amplitudes = np.concatenate([np.full(len(PREAMBLE_STEPS), 1.0), np.full(len(SYNCWORD_STEPS), 1.0), amplitudes], dtype=np.float32)

	phase_signal = np.repeat(diff, SAMPLES_PER_SYMBOL)
	amplitudes = np.repeat(amplitudes, SAMPLES_PER_SYMBOL)

	total_samples = len(phase_signal)

	# Optional tiny fade-in to reduce click at frame boundary
	fade_len = 2 * SAMPLES_PER_SYMBOL

	ramp = np.linspace(0.0, 1.0, fade_len, endpoint=False, dtype=np.float32)

	t_in = (np.arange(fade_len, dtype=np.int64) + cursor) / float(SAMPLE_RATE)
	fade_in = float(amplitude) * np.cos(2 * np.pi * (carrier_freq * t_in + phase_signal[0] / PSK)) * ramp
	cursor += fade_len

	t = np.arange(total_samples, dtype=np.int64) + cursor
	t = t / float(SAMPLE_RATE)
	waveform = float(amplitude) * np.cos(2 * np.pi * (carrier_freq * t + phase_signal / PSK)) * amplitudes
	cursor += total_samples

	t_out = (np.arange(fade_len, dtype=np.int64) + cursor) / float(SAMPLE_RATE)
	fade_out = float(amplitude) * np.cos(2 * np.pi * (carrier_freq * t_out + phase_signal[-1] / PSK)) * ramp[::-1]
	cursor += fade_len

	guard = np.zeros(fade_len, dtype=np.float32)
	cursor += fade_len

	waveform = np.concatenate([fade_in, waveform, fade_out, guard])
	# waveform = np.concatenate([waveform, guard])

	all_samples.append(waveform)


waveform = np.concatenate(all_samples)
waveform = np.clip(np.rint(waveform), -32768, 32767).astype(np.int16)

stereo = np.column_stack([waveform, -waveform])
wavfile.write(f"{file}.wav", SAMPLE_RATE, stereo)


print("First sample: ", waveform[0])
print(zlib.crc32(open(f"in.{file}", 'rb').read()))