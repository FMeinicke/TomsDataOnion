#!/usr/bin/env python3
import base64
from typing import Union

def decode(payload: Union[bytes, str]) -> bytes:
    print("Decoding Layer 1...")

    FLIP_MASK = 0b01010101
    LAST_DIGIT_MASK = 0b00000001

    result: bytes = b''
    for byte in base64.a85decode(payload, adobe=True):
        ## (1) Flip every second bit
        flipped_byte = byte ^ FLIP_MASK
        # print("flipped_byte:", flipped_byte)
        ## (2) Rotate the bits one position to the right
        last_digit = flipped_byte & LAST_DIGIT_MASK
        rotated_byte = flipped_byte >> 1
        rotated_byte += last_digit
        # print("rotated_byte:", rotated_byte)
        result += rotated_byte.to_bytes(1,'big')

    with open("layer2", "wb+") as layer_file:
        layer_file.write(result)

    return result

#%%
if __name__ == "__main__":
    with open('layer1', 'r') as payload_file:
        decode(payload_file.read())
