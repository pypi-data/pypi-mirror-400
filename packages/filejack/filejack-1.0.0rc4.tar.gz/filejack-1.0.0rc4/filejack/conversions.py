import numpy as np

from values import *


def bytes_to_symbols(buf: bytes) -> np.ndarray:
	b = np.frombuffer(buf, dtype=np.uint8)
	bits = np.unpackbits(b)
	assert bits.size % BITS_PER_SYMBOL == 0
	bit3 = bits.reshape(-1, BITS_PER_SYMBOL)
	symbols = np.zeros((bit3.shape[0],), dtype=np.int32)
	for i in range(BITS_PER_SYMBOL):
		symbols += bit3[:,i] << (BITS_PER_SYMBOL - 1 - i)
	return symbols.astype(np.int32)


def symbols_to_bytes(symbols: np.ndarray) -> bytes:
	symbols = symbols.astype(np.uint8) % DAPSK
	bits = np.empty(symbols.size * BITS_PER_SYMBOL, dtype=np.uint8)
	for i in range(BITS_PER_SYMBOL):
		bits[i::BITS_PER_SYMBOL] = (symbols >> (BITS_PER_SYMBOL - 1 - i)) & 1
	packed = np.packbits(bits)
	return packed.tobytes()