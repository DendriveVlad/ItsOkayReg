from string import ascii_letters, digits
from random import choice, sample

__LETTERS = ascii_letters + digits


def decode_cookie(coded_cookie):
    key = "".join(__LETTERS[__LETTERS.index(i) - 2] for i in coded_cookie[-2:])
    n = 0
    cookie = []
    for letter in coded_cookie[0:-2]:
        new_index = __LETTERS.index(letter) - __LETTERS.index(key[n])
        cookie.append(__LETTERS[new_index if new_index >= 0 else new_index + len(__LETTERS)])
        n -= 1 if n else -1
    return "".join(cookie)


def create_cookie():
    cookie = []
    coded_cookie = []
    key = "".join(sample(__LETTERS, 2))
    for _ in range(6):
        cookie.append(choice(__LETTERS))
    n = 0
    for letter in cookie:
        new_index = __LETTERS.index(letter) + __LETTERS.index(key[n])
        coded_cookie.append(__LETTERS[new_index if new_index < len(__LETTERS) else new_index - len(__LETTERS)])
        n -= 1 if n else -1
    return "".join(cookie) + "".join(sample(__LETTERS, 2)), "".join(coded_cookie) + "".join([__LETTERS[__LETTERS.index(i) + 2 - (len(__LETTERS) if __LETTERS.index(i) + 2 >= len(__LETTERS) else 0)] for i in key])
