#!/usr/bin/env python3

import base64
from typing import Union
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
except ImportError:
    print("Please install pycryptdome:")
    print("\t`pip install pycryptdome'")

def bytes_to_int(b: bytearray):
    return int.from_bytes(b, 'big')

def byte_xor(b: bytes, i: int) -> bytes:
    """
    Calculate 'b XOR i'
    """
    return int(bytes_to_int(b) ^ i).to_bytes(len(b), 'big')

def bytes_to_wordlist(bytes: bytes, bytes_per_word: int) -> list:
    res = []
    for i in range(0, len(bytes), bytes_per_word):
        res.append(bytes_to_int(bytes[i:i + bytes_per_word]))
    return res

def word_to_bytes(word: int, bytes_per_word: int = 1) -> bytes:
    return word.to_bytes(bytes_per_word, 'big')

def wordlist_to_bytes(words: list, bytes_per_word: int) -> bytes:
    res = bytes()
    for word in words:
        res += word_to_bytes(word, bytes_per_word)
    return res

def aes_key_unwrap(wrapped_key: bytes, kek: bytes, kek_iv: bytes):
    """
    Unwrap the given key according to RFC 3394 using the given KEK and initialization vector
    """
    # RFC 3394:
    # (1) Initialize variables.
    word_len = 8 # [bytes] (= 64 bit)
    words = bytes_to_wordlist(wrapped_key, word_len)
    # print("words:", words)
    # words[0] = initial value (the `A` in RFC 3394 sec 2.2.2)
    key_len = len(words) - 1 # [bytes]
    cipher = AES.new(kek, AES.MODE_ECB)
    # (2) Compute intermediate values.
    for j in range(5, -1, -1):
        for i in range(key_len, 0, -1):
            t = key_len * j + i
            # temporarily save the value from the XOR in words[0]
            # this will get overwritten later on anyway
            words[0] = words[0] ^ t
            b = cipher.decrypt(wordlist_to_bytes([words[0], words[i]], word_len))
            [words[0], words[i]] = bytes_to_wordlist(b, word_len)

    # (3) Output results.
    if word_to_bytes(words[0], word_len) == kek_iv:
        return wordlist_to_bytes(words[1:], word_len)
    else:
        raise Exception("IV doesn't match up")


def decode(payload: Union[bytes, str]) -> bytes:
    print("Decoding Layer 5...")

    result: bytes = b''
    decoded = base64.a85decode(payload, adobe=True)

    # As per instruction:
    # First 32 bytes: The 256-bit key encrypting key (KEK).
    key_encryption_key = decoded[0:32]
    # Next 8 bytes: The 64-bit initialization vector (IV) for
    # the wrapped key.
    wrapped_key_init_vector = decoded[32:40]
    # Next 40 bytes: The wrapped (encrypted) key. When
    # decrypted, this will become the 256-bit encryption key.
    wrapped_key = decoded[40:80]
    # Next 16 bytes: The 128-bit initialization vector (IV) for
    # the encrypted payload.
    init_vector = decoded[80:96]
    # All remaining bytes: The encrypted payload.
    encrypted = decoded[96:]

    # The first step is to use the KEK and the 64-bit IV to unwrap the wrapped key.
    key = aes_key_unwrap(wrapped_key, key_encryption_key, wrapped_key_init_vector)
    # print("key:", key)

    # The second step is to use the unwrapped key and the 128-bit IV to decrypt the rest of the payload.
    cipher = AES.new(key, AES.MODE_CTR, nonce=b'',initial_value=init_vector)
    result = cipher.decrypt(pad(encrypted, AES.block_size))


    with open("layer6", "wb+") as layer_file:
        layer_file.write(result)

    return result

#%%
if __name__ == "__main__":
    with open('layer5', 'r') as payload_file:
        decode(payload_file.read())
