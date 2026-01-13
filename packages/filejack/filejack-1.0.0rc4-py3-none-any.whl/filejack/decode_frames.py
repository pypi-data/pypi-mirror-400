import zlib
import numpy as np
from reedsolo import ReedSolomonError
from scipy.signal import hilbert

from RSC import *
from conversions import *
from values import *


def decode_frames(rx, sample_rate, search_step = 1, quick = False):
	samples_per_symbol = int(round(sample_rate / baud_rate))
	# sos_bp = butter(6, [carrier_freq - baud_rate * 2, carrier_freq + baud_rate * 2], btype='bandpass', fs=sample_rate, output='sos')
	# rx = sosfiltfilt(sos_bp, rx).astype(np.float32)

	pad_len = 2048
	rx_padded = np.pad(rx, (pad_len, pad_len), 'constant')

	analytic_padded = hilbert(rx_padded)

	analytic = analytic_padded[pad_len:-pad_len]

	num_symbols = int(len(rx) // samples_per_symbol)
	n = np.arange(len(rx), dtype=np.int64)
	t = n / sample_rate
	bb = analytic * np.exp(-1j * 2*np.pi * carrier_freq * t)

	# cut = 3500.0
	# sos_lp = butter(6, cut, btype='lowpass', fs=sample_rate, output='sos')
	# bb = sosfiltfilt(sos_lp, bb.real).astype(np.float32) + 1j * sosfiltfilt(sos_lp, bb.imag).astype(np.float32)

	def symbols_from(bb, start_sample, offset, symbols_num):
		start = start_sample + offset
		need = start + symbols_num * samples_per_symbol
		if need > len(bb):
			return None

		symbol = bb[start : start + symbols_num * samples_per_symbol].reshape(symbols_num, samples_per_symbol).sum(axis=1)

		# phase = np.unwrap(np.angle(symbol))
		# phase = np.angle(symbol)
		# diff = np.diff(phase)
		# diff = np.mod(diff, 2 * np.pi)
		# diff = np.round(diff * PSK / 2 / np.pi).astype(np.int32) % PSK

		return symbol

	def steps_from(bb, start_sample, offset, n_symbols):
		symbol = symbols_from(bb, start_sample, offset, n_symbols)

		phase = np.angle(symbol[1:] * np.conj(symbol[:-1]))
		diff = np.rint(np.mod(phase, 2*np.pi) * PSK/(2*np.pi)).astype(np.int32) % PSK

		return diff

	steps_by_offset = [steps_from(bb, 0, offset, (len(bb) - offset) // samples_per_symbol) for offset in range(samples_per_symbol)]

	pattern = np.array(PREAMBLE_STEPS[1:] + SYNCWORD_STEPS, dtype=np.int32)
	pattern_len = len(pattern)

	PAYLOAD_STEPS_LEN = (N * 8) // BITS_PER_SYMBOL

	frames_payload = {}
	total_expected = None
	min_match = int(0.9 * pattern_len)

	no_lock = 0
	rsc_error = 0
	header_error = 0
	crc_error = 0
	ok_log = []

	i = 0
	while i + (pattern_len + PAYLOAD_STEPS_LEN + 1) * samples_per_symbol <= len(bb):
		cands = []
		for offset in range(samples_per_symbol):
			# if i < offset:
			# 	continue

			start = max((i - offset) // samples_per_symbol, 0)
			end = start + (pattern_len + PAYLOAD_STEPS_LEN + 1)
			if end > len(steps_by_offset[offset]):
				continue

			steps =  steps_by_offset[offset][start : end]
			# steps = steps_from(bb, i, offset, pattern_len + PAYLOAD_STEPS_LEN + 1)
			# if steps is None:
			# 	continue

			window = steps[:pattern_len]

			delta = (window - pattern) % PSK
			r = np.bincount(delta, minlength=PSK).argmax()
			score = np.sum(delta == r)

			if score >= min_match:
				cands.append((score, offset, steps, start, r))

		if not cands:
			no_lock += 1
			i += search_step
			continue

		cands.sort(key=lambda x: x[0], reverse=True)
		decoded_ok = False
		for best_score, best_off, best_steps, best_start_idx, rotation in cands:
			# Extract payload steps immediately after pattern
			payload_steps = best_steps[pattern_len:pattern_len + PAYLOAD_STEPS_LEN]
			payload_steps = (payload_steps - rotation) % PSK

			symbols = symbols_from(bb, best_start_idx * samples_per_symbol, best_off, pattern_len + PAYLOAD_STEPS_LEN + 1)

			gain = np.median(abs(symbols[2 : pattern_len + 1])) + 1e-12 	# epsilon - avoid div by zero
			a_hat = abs(symbols[pattern_len + 1: pattern_len + 1 + PAYLOAD_STEPS_LEN]) / gain
			a_hat = np.clip(a_hat, 0.0, 1.0)
			d = np.abs(a_hat[:, None] - ASK_LEVELS[None, :])
			amplitudes = np.argmin(d, axis=1)

			combined = (amplitudes.astype(np.uint8) << PSK_BITS_PER_SYMBOL) | payload_steps.astype(np.uint8)
			cw = symbols_to_bytes(combined)

			# RS decode
			try:
				decoded = RSC.decode(cw)[0]
			except ReedSolomonError:
				# print("\rReed-Solomon decoding failed, skipping unusable frame.")
				# print(f"\rMalformed frame: {seq}/{total}  {payload_len}/{MAX_PAYLOAD}")

				rsc_error += 1
				continue

			try:
				hdr = decoded[:HDR_LEN]
				seq, total, payload_len = struct.unpack(HDR_FMT, hdr)
				payload = decoded[HDR_LEN:HDR_LEN + payload_len]

				if payload_len > MAX_PAYLOAD or (total_expected is not None and (total != total_expected or seq >= total_expected)):
					header_error += 1
					continue

			except struct.error:
				header_error += 1
				continue

			try:
				crc_recv = struct.unpack('>I', decoded[HDR_LEN + payload_len:HDR_LEN + payload_len + CRC_LEN])[0]
			except struct.error:
				print(f"\rFrame CRC unpacking failed: {seq}/{total_expected}")
				print(decoded[HDR_LEN + payload_len:HDR_LEN + payload_len + CRC_LEN])
				crc_error += 1
				continue

			crc_calc = zlib.crc32(hdr + payload) & 0xFFFFFFFF
			if crc_recv != crc_calc:
				print(f"\rCRC mismatch for frame {seq}: received {crc_recv}, calculated {crc_calc}")
				crc_error += 1
				continue

			decoded_ok = True
			break

		if not decoded_ok:
			i += search_step
			continue

		else:
			try:
				frames_payload[seq] = payload
				total_expected = total_expected or total

				frame_steps = pattern_len + PAYLOAD_STEPS_LEN + 1
				frame_samples = frame_steps * samples_per_symbol
				frame_start_sample = best_off + best_start_idx * samples_per_symbol
				extra = 72

				if len(ok_log) >= 2:
					last_seq, last_start = ok_log[-1][0], ok_log[-1][1]

					if last_seq < seq:  # Normal forward progression
						# Calculate actual spacing from last decoded frame
						delta_seq = seq - last_seq
						delta_samples = frame_start_sample - last_start
						actual_spacing = delta_samples / delta_seq  # samples per frame

						# Predict next frame using observed spacing
						expected = frame_start_sample + int(round(actual_spacing))
					else:
						# Fallback to nominal
						expected = frame_start_sample + frame_samples + extra
				else:
					expected = frame_start_sample + frame_samples + extra


				W = 16 * samples_per_symbol  # try 4..8 symbols worth, start with 48 samples

				best_local_score = -1
				best_local_start = None
				best_local_off = None
				best_local_idx = None
				best_local_rot = None

				for cand_start_sample in range(expected - W, expected + W + 1):
					if cand_start_sample < 0:
						continue

					off = cand_start_sample % samples_per_symbol
					start_idx2 = cand_start_sample // samples_per_symbol
					end2 = start_idx2 + (pattern_len + PAYLOAD_STEPS_LEN + 1)

					if end2 > len(steps_by_offset[off]):
						continue

					steps2 = steps_by_offset[off][start_idx2:end2]
					window2 = steps2[:pattern_len]

					delta2 = (window2 - pattern) % PSK
					r2 = np.bincount(delta2, minlength=PSK).argmax()
					score2 = np.sum(delta2 == r2)

					if score2 > best_local_score:
						best_local_score = score2
						best_local_start = cand_start_sample
						best_local_off = off
						best_local_idx = start_idx2
						best_local_rot = r2

				# snap if we found a good preamble near expected
				if best_local_score >= min_match:
					i = best_local_start
				else:
					if quick:
						i = expected
					else:
						i += search_step


				# ok_log.append((seq, frame_start_sample, expected, best_off, best_start_idx, best_score, rotation))
				ok_log.append((seq, frame_start_sample, best_score))

			except ValueError as e:
				print(f"\rFrame parsing failed: {e}")
				i += search_step

	return frames_payload, total_expected, ok_log, no_lock, rsc_error, header_error, crc_error