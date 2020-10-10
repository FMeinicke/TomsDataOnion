#!/usr/bin/env python3
import base64
from typing import Union

def decode(payload: Union[bytes, str]) -> bytes:
    print("Decoding Layer 0...")

    result = base64.a85decode(payload, adobe=True)

    with open("layer1", "wb+") as layer_file:
        layer_file.write(result)

    return result

#%%
if __name__ == "__main__":
    with open('layer0', 'r') as payload_file:
        decode(payload_file.read())
