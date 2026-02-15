def vigenere(text: str, key: str, alphabet: str, mode: str = 'encrypt') -> str:
    if not key.strip():
        return text
    
    alphabet_size = len(alphabet)
    key = key.replace(' ', '').upper()
    result = []
    key_index = 0

    for char in text:
        if char.upper() in alphabet:
            shift = alphabet.index(key[key_index % len(key)])
            if mode == 'decrypt':
                shift = -shift
            pos = alphabet.index(char.upper())
            new_char = alphabet[(pos + shift) % alphabet_size]
            result.append(new_char if char.isupper() else new_char.lower())
            key_index += 1
        else:
            result.append(char)
    
    return ''.join(result)
