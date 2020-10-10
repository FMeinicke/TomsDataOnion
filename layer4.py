#!/usr/bin/env python3

import base64
from typing import Union

def bytes_to_int(b: bytearray):
    return int.from_bytes(b, 'big')

def bytes_to_ip(b: bytearray):
    part = []
    for i in range(4):
        part.append(str(b[i]))
    return '.'.join(part)

def verify_checksum(b: bytearray):
    assert len(b) % 2 == 0

    def add_carry_around(w: int):
        return (w & 0xffff) + (w >> 16)

    word_sum = 0
    for i in range(0, len(b), 2):
        word_sum += bytes_to_int(b[i:i+2])
    return add_carry_around(word_sum) == 0xffff

def decode(payload: Union[bytes, str]) -> bytes:
    print("Decoding Layer 4...")

    IP_HEADER_LEN = 20
    UDP_HEADER_LEN = 8

    # constraints
    SOURCE_IP = '10.1.1.10'
    DEST_IP = '10.1.1.200'
    DEST_PORT = 42069

    result = bytearray()
    decoded = base64.a85decode(payload, adobe=True)
    offset = 0
    while offset < len(decoded):
        # IP header
        ip_header = bytearray(decoded[offset:offset+IP_HEADER_LEN])
        offset += IP_HEADER_LEN
        #print("ip_header:", ip_header)

        ip_total_len = bytes_to_int(ip_header[2:4])
        #print("ip_total_len:", ip_total_len)
        ip_header_checksum = bytes_to_int(ip_header[10:12])
        #print("ip_header_checksum:", ip_header_checksum)
        ip_header_checksum_correct = verify_checksum(ip_header)
        #print("checksum correct:", ip_header_checksum_correct)
        source_ip = bytes_to_ip(ip_header[12:16])
        #print("source_ip:", source_ip)
        dest_ip = bytes_to_ip(ip_header[16:20])
        #print("dest_ip:", dest_ip)

        # UDP header
        udp_header = bytearray(decoded[offset:offset+UDP_HEADER_LEN])
        offset += UDP_HEADER_LEN
        #print("udp_header:", udp_header)

        dest_port = bytes_to_int(udp_header[2:4])
        #print("dest_port:", dest_port)
        udp_total_len = bytes_to_int(udp_header[4:6])
        #print("udp_total_len:", udp_total_len)
        assert ip_total_len == udp_total_len + IP_HEADER_LEN
        data_length = udp_total_len - UDP_HEADER_LEN
        #print("data_length:", data_length)
        data = bytearray(decoded[offset:offset+data_length])
        offset += data_length
        #print("data:", data)
        udp_checksum = bytes_to_int(udp_header[6:8])
        #print("udp_checksum:", udp_checksum)
        # RFC 768: UDP pseudo header
        #   0      7 8     15 16    23 24    31
        #  +--------+--------+--------+--------+
        #  |          source address           |
        #  +--------+--------+--------+--------+
        #  |        destination address        |
        #  +--------+--------+--------+--------+
        #  |  zero  |protocol|   UDP length    |
        #  +--------+--------+--------+--------+
        pseudo_header = ip_header[12:20] + bytes(1) + ip_header[9:10] + udp_header[4:6]
        #print("pseudo_header:", format(bytes_to_int(pseudo_header), '096b'))
        # Checksum calculation needs:
        # pseudo header + UDP header + data + padding (to have an even number of bytes)
        udp_checksum_correct = verify_checksum(pseudo_header + udp_header + data + bytes(data_length % 2))
        #print("checksum correct:", udp_checksum_correct)

        # verify packet properties and correct checksums
        if source_ip == SOURCE_IP and \
            dest_ip == DEST_IP and \
            dest_port == DEST_PORT and \
            ip_header_checksum_correct and \
            udp_checksum_correct:
            result += data

    with open("layer5", "wb+") as layer_file:
        layer_file.write(result)

    return result

#%%
if __name__ == "__main__":
    with open('layer4', 'r') as payload_file:
        decode(payload_file.read())
