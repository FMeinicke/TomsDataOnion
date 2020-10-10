#!/usr/bin/env python3

import base64
from typing import Union

def decode(payload: Union[bytes, str]) -> bytes:
    print("Decoding Layer 3...")

    KEY = bytearray([0x6C, 0x24, 0x84, 0x8E, 0x42, 0x19, 0xA8, 0xE1,
                    0xC5, 0xDB, 0x57, 0x65, 0xB9, 0xC6, 0x14, 0x9E,
                    0xA5, 0x19, 0x35, 0x96, 0x3B, 0x39, 0x7F, 0xA5,
                    0x65, 0xD1, 0xFE, 0x01, 0x85, 0x7D, 0xD9, 0x4C])
    KEY_LEN = 32

    result = bytearray()
    i = 0
    for byte in base64.a85decode(payload, adobe=True):
        # print("byte:", byte)
        result.append(byte ^ KEY[i % KEY_LEN])
        i += 1

    with open("layer4", "wb+") as layer_file:
        layer_file.write(result)

    return result

#%%
if __name__ == "__main__":
    with open('layer3', 'r') as payload_file:
        decode(payload_file.read())

