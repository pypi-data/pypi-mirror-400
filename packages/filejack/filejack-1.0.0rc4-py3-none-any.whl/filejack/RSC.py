import struct

from reedsolo import RSCodec

from values import *


N = 255
NSYM = 32
K = N - NSYM
RSC = RSCodec(NSYM)

HDR_FMT = ">IIH"
HDR_LEN = struct.calcsize(HDR_FMT)

CRC_LEN = 4

MAX_PAYLOAD = K - HDR_LEN - CRC_LEN


def lfsr_bits(n: int, seed: int, taps=(7, 6)) -> list[int]:
	"""
	Simple LFSR bit generator.
	taps are 1-indexed bit positions within the register size (max(taps)).
	"""
	m = max(taps)
	mask = (1 << m) - 1
	reg = seed & mask
	if reg == 0:
		reg = 1  # avoid stuck-at-zero

	out = []
	for _ in range(n):
		# output bit (LSB)
		out.append(reg & 1)

		# feedback = XOR of tap bits
		fb = 0
		for t in taps:
			fb ^= (reg >> (t - 1)) & 1

		# shift right, insert feedback at MSB
		reg = (reg >> 1) | (fb << (m - 1))
		reg &= mask
	return out

def bits_to_steps(bits01: list[int]) -> list[int]:
	return [PSK // 2 if b else 0 for b in bits01]

PREAMBLE_STEPS = bits_to_steps(lfsr_bits(PREAMBLE_SYMS, seed=0x5D, taps=(7, 6)))
SYNCWORD_STEPS = bits_to_steps(lfsr_bits(SYNCWORD_SYMS, seed=0x6B, taps=(7, 6)))