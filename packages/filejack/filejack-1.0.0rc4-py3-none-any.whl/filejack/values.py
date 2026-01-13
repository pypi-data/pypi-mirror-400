import math
import numpy as np

PSK = 8
PSK_BITS_PER_SYMBOL = int(math.log2(PSK))
assert 2 ** PSK_BITS_PER_SYMBOL == PSK


ASK_RINGS = 1
ASK_BITS_PER_SYMBOL = int(math.log2(ASK_RINGS))
assert 2 ** ASK_BITS_PER_SYMBOL == ASK_RINGS

if ASK_RINGS == 1:
	ASK_LEVELS = np.array([1])
else:
	ASK_LEVELS = np.linspace(0.4, 1.0, ASK_RINGS, dtype=np.float32)


DAPSK = PSK * ASK_RINGS
BITS_PER_SYMBOL = PSK_BITS_PER_SYMBOL + ASK_BITS_PER_SYMBOL


SAMPLE_RATE = 48000
baud_rate = 4000
amplitude = int(32767 * 0.8)
carrier_freq = 12000

SAMPLES_PER_SYMBOL = int(round(SAMPLE_RATE / baud_rate))


PREAMBLE_SYMS = 64
SYNCWORD_SYMS = 32
