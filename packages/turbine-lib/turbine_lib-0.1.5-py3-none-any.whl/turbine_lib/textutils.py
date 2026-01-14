def to_utf16(x):
    """Convert integer to UTF-16 string"""
    if x == 0:
        return chr(0x30)  # '0' character
    res = ""
    while x > 0:
        res += chr(0x30 + x % 10)  # '0' + digit
        x //= 10
    return res[::-1]  # Reverse string

def from_utf16(num_str):
    """Convert UTF-16 string to integer"""
    res = 0
    for c in num_str:
        res = res * 10 + (ord(c) - 0x30)  # digit - '0'
    return res

def arguments_from_utf16(args_str):
    """Parse arguments from UTF-16 string"""
    if not args_str:
        return ""
    
    parts = args_str.split('-')
    result_parts = []
    for part in parts:
        if part:  # Skip empty parts
            result_parts.append(str(from_utf16(part)))
    
    return '-'.join(result_parts)