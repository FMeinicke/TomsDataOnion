#!/usr/bin/env python3
import base64
from typing import Union

def decode(payload: Union[bytes, str]) -> bytes:
    print("Decoding Layer 2...")

    result: bytes = b''
    data_group: str = ''
    i = 0
    for byte in base64.a85decode(payload, adobe=True):
        # print("---")
        # print("byte:",byte)
        first_seven_bits = format(byte, '08b')[:7]
        # print("first_seven_bits:",first_seven_bits)
        parity_bit = byte & 0b00000001
        # print("parity_bit:",parity_bit)
        num_one_bits = first_seven_bits.count('1')
        # print("num_one_bits:",num_one_bits)
        if (num_one_bits % 2) == parity_bit:
            data_group += first_seven_bits
            i += 1
            # print("i:", i)
            if i % 8 == 0:
                # print(data_group)
                for j in range(7):
                    # print("j:", j)
                    data_byte = int(data_group[j*8:(j+1)*8],2)
                    # print("data_group[j*8:(j+1)*8]:",data_group[j*8:(j+1)*8])
                    result += data_byte.to_bytes(1, 'big')
                data_group = str()

    with open("layer3", "wb+") as layer_file:
        layer_file.write(result)

    return result

#%%
if __name__ == "__main__":
    with open('layer2', 'r') as payload_file:
        decode(payload_file.read())
