alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g',
            'h', 'i', 'j', 'k', 'l', 'm', 'n',
            'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']

morse = ['.-', '-...', '-.-.', '-..', '.', '..-.', '--.', '....',
         '..', '.---', '-.-', '.-..', '--', '-.', '---', '.--.',
         '--.-', '.-.', '...', '-', '..-', '...-', '.--', '-..-',
         '-.--', '--..']


# noinspection SpellCheckingInspection
def main():
    x: str = input("E-nigma\nC-aeser\nO-TP\nM-orse\n\nEncryption Type: ")
    cipher: str = input("Input: ")

    if x.lower().__eq__('e'):
        enigma(cipher)
    else:
        direct: str = input("E-ncrypt\nD-ecrypt\nDirection: ")
        delta = 1
        if direct.lower().__eq__('d'):
            delta = -1

        if x.lower().__eq__('c'):
            caeser(cipher, delta)
        elif x.lower().__eq__("o"):
            otp(cipher, delta)
        elif x.lower().__eq__('m'):
            morseCode(cipher, delta)
        else:
            exit(0)


def getIndex(letter: str, a) -> int:
    i = int(0)
    for check in a:
        if check.__eq__(letter.lower()):
            break
        i += 1
    return i


def morseCode(cipher: str, direct: int):
    out = ''
    if direct < 0:
        c = cipher.split(' ')
        for s in c:
            idx = getIndex(s, morse)
            out += alphabet[idx]
    else:
        for s in cipher:
            if s.isalpha():
                idx = getIndex(s, alphabet)
                out += morse[idx] + ' '

    print(out)


def otp(cipher: str, direct: int):
    invalid = True
    key = ''
    while invalid:
        key = input('Key: ')
        if len(key) < len(cipher[:].replace(' ', '')):
            print("Key too small")
            continue
        invalid = False

    out = ''
    i = 0
    for l in cipher:
        if l.isalpha():
            inIdx = getIndex(l, alphabet)
            keyIdx = getIndex(key[i], alphabet)
            out += alphabet[(inIdx + (keyIdx * direct)) % 26]
        else:
            out += l

        i += 1

    print(out)


def caeser(cipher: str, direct: int):
    repeat = True

    while repeat:
        x = input("Offset: ")

        if x.isdigit():
            x = int(x)
            out = ''
            for l in cipher:
                if l.isalpha():
                    i = getIndex(l, alphabet)
                    out += alphabet[(i + (x * direct)) % 26]
                else:
                    out += l

            print(out)
        else:
            repeat = False


def enigma(cipher: str):
    x: str = ''
    while x != '~':
        x = input('Switch: ')

        if len(x) != 3:
            if x == "~":
                exit(0)
            else:
                continue
        a = x[0]
        b = x[2]

        if not a.isalpha() or not b.isalpha():
            continue

        n = ''
        for l in cipher:
            if l is a:
                n += b
            elif l is b:
                n += a
            else:
                n += l

        cipher = n
        print(cipher)


main()
