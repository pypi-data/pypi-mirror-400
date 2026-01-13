from RSC import MAX_PAYLOAD


def reconstruct_data(frames_payload, frames_num) -> bytes:
	data = bytearray()
	for i in range(0, frames_num):
		if i not in frames_payload:
			print(f"Missing frame {i}")
			data.extend(b'\x00' * MAX_PAYLOAD)
			continue
		data.extend(frames_payload[i])
	return bytes(data)