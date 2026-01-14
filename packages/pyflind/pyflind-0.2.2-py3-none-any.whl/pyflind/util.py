
def crc8(val):
    '''Compute a CRC8 on the supplied data buffer.

    Args:
        val: data buffer

    Returns:
        int: crc8 of val
    '''
    # https://gist.github.com/eaydin/768a200c5d68b9bc66e7#file-crc8dallas-py
    crc = 0
    for c in val:
        for i in range(0, 8):
            b = (crc & 1) ^ ((( int(c) & (1 << i))) >> i)
            crc = (crc ^ (b * 0x118)) >> 1
    return crc

def base36_to_int(base36_str):
    '''Convert a base-36 alphanumeric string to integer.

    Args:
        base36_str: alphanumeric base-36 string

    Returns:
        int: value of base36_str
    '''
    char_list = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    val = 0
    power = 0
    for char in reversed(base36_str):
        char_index = char_list.index(char)
        val += char_index * (36 ** power)
        power += 1
    return val

def int_to_base36(val):
    '''Convert an integer to base-36 alphanumeric string.

    Args:
        val: value to convert

    Returns:
        str: alphanumeric base-36 representation of val
    '''
    ret = ""
    char_list = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    while len(ret) < 6:
        ret = char_list[val % 36] + ret
        val //= 36
    return ret

def version_uint32_to_str(version_int):
    '''Convert a version from int to string format.

    Args:
        version_int: raw unsigned 32-bit integer version

    Returns:
        str: human readable string version
    '''
    dirty_ver = (version_int & (0x80000000)) >> 31
    major_ver = (version_int & (0x7C000000)) >> 26
    minor_ver = (version_int & (0x03FC0000)) >> 18
    patch_ver = (version_int & (0x0003FFFF))
    ver_str = 'v' + str(major_ver) + '.' + str(minor_ver) + '.' + str(patch_ver)
    if dirty_ver == 1:
        ver_str += '-dirty'
    return ver_str
