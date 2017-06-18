import struct
from hashlib import sha256

UNPACK_DATA = {
    'uint32': {'struct_format': 'L', 'bits': 32},
    'bool': {'struct_format': '?', 'bits': 1},
}
DEFAULT_ENDIANNESS = '>'  # Big endian


def unpack(unpack_hash, data_type):
    """Unpacks type data_type from unpack_hash"""
    unpack_data = UNPACK_DATA[data_type]
    data = bytearray(unpack_hash.digest())
    bits = unpack_data['bits']
    struct_format = DEFAULT_ENDIANNESS + unpack_data['struct_format']
    if bits > unpack_hash.digest_size * 8:  # 256 for SHA-256
        needed_hashes = -(-bits // (unpack_hash.digest_size * 8)) - 1  # Ceiling division
        for _ in range(needed_hashes):
            unpack_hash = sha256(unpack_hash.hexdigest())
            data = unpack_hash.digest() + data
    data = data[(-bits // 8):]
    if bits < 8:
        binary_byte = bin(data[0])
        binary_byte = binary_byte[-bits:]
        data[0] = int(binary_byte, 2)
    ret = struct.unpack(struct_format, data)
    if len(ret) == 1:
        return ret[0]
    else:
        return ret


def get_range(range_hash, min_num, max_num, random_type='uint32'):
    max_random_num = 2 ** UNPACK_DATA[random_type]['bits'] - 1
    random_num = unpack(range_hash, random_type)
    range_delta = max_num - min_num
    ret = min_num + int(round(range_delta * random_num / max_random_num))
    # print(range_delta, random_num, max_num)
    return ret


def get_bool_by_chance(bool_hash, chance, accuracy=1000, random_type='uint32'):
    chance_i = get_range(bool_hash, 0, accuracy, random_type)
    if chance_i < int(chance * accuracy):
        return True
    else:
        return False
