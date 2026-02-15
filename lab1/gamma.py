class PseudorandomGenerator:
    def __init__(self, seed: int):
        self.seed = seed
        self.a = 1664525
        self.c = 1013904223
        self.m = 2**32
        self.current = seed

    def next(self) -> int:
        self.current = (self.a * self.current + self.c) % self.m
        return self.current

    def next_in_range(self, min_val: int, max_val: int) -> int:
        return min_val + (self.next() % (max_val - min_val + 1))

def key_to_seed(key: str, alphabet: str) -> int:
    base = len(alphabet)
    value = 0

    for char in key:
        index = alphabet.index(char.upper()) + 1
        value = value * base + index

    return value

def _char_to_code(char: str, alphabet: str) -> int:
    char_upper = char.upper()
    if char_upper not in alphabet:
        return -1
    return alphabet.index(char_upper) + 1

def _code_to_char(code: int, alphabet: str, is_upper: bool) -> str:
    index = (code - 1) % len(alphabet)
    char = alphabet[index]
    return char if is_upper else char.lower()

def gamma(text: str, key: str, alphabet: str, mode: str = 'encrypt') -> str:
    if not text or not key:
        return text

    key_clean = key.replace(' ', '').replace('\n', '').replace('\t', '')
    if not key_clean:
        return text

    seed = key_to_seed(key, alphabet)
    prng = PseudorandomGenerator(seed)
    alphabet_size = len(alphabet)
    result = []
    
    for char in text:
        char_code = _char_to_code(char, alphabet)
        if char_code >= 0:
            gamma = prng.next_in_range(1, alphabet_size)
            if mode == 'decrypt':
                new_code = (char_code - gamma) % alphabet_size
            else:
                new_code = (char_code + gamma) % alphabet_size
            if new_code == 0:
                new_code = alphabet_size

            result.append(_code_to_char(new_code, alphabet, char.isupper()))
        else:
            result.append(char)

    return ''.join(result)
