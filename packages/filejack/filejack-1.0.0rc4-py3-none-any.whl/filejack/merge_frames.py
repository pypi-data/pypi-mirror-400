"""
.fjf files is FileJack Frames file, containing multiple decoded frames with metadata. Can be used to merge results from different decoding attempts.
"""

import struct

FILEJACK_FJF_HEADER = b'FJF0917\nhttps://github.com/Staheos/filejack\n1.0.0'

def merge_frames(total_expected: int, frames_inputs: list[dict[int, bytes | bytearray | list[int]]]):
	frames_output = {}

	for frames_input in frames_inputs:
		for seq, payload in frames_input.items():
			if seq not in frames_output:
				frames_output[seq] = payload
	return frames_output

def save_fjf(total_expected: int, frames: dict[int, bytes | bytearray | list[int]], filename: str):
	with open(filename, 'wb') as f:

		f.write(FILEJACK_FJF_HEADER)
		f.write(struct.pack('>I', total_expected))
		f.write(struct.pack('>I', len(frames)))

		for seq in sorted(frames.keys()):
			payload = frames[seq]
			if isinstance(payload, list):
				payload = bytes(payload)
			payload_len = len(payload)
			f.write(struct.pack('>I', seq))  # Frame sequence number
			f.write(struct.pack('>I', payload_len))  # Payload length
			f.write(payload)  # Payload data

def load_fjf(filename: str) -> tuple[int, dict[int, bytes]]:
	frames = {}
	with open(filename, 'rb') as f:
		# Read header
		header = f.read(len(FILEJACK_FJF_HEADER))
		if header != FILEJACK_FJF_HEADER:
			raise ValueError("Invalid FJF file format")

		total_expected_bytes = f.read(4)
		total_expected = struct.unpack('>I', total_expected_bytes)[0]

		num_frames_bytes = f.read(4)
		num_frames = struct.unpack('>I', num_frames_bytes)[0]

		for _ in range(num_frames):
			seq_bytes = f.read(4)
			payload_len_bytes = f.read(4)
			seq = struct.unpack('>I', seq_bytes)[0]
			payload_len = struct.unpack('>I', payload_len_bytes)[0]
			payload = f.read(payload_len)
			frames[seq] = payload
	return total_expected, frames