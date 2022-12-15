def decode(coded_nick):
    mc_alphabet = "abcdefghijklmnopqrstuvwxyz1234567890_"
    warp = "abcdefghij".index(coded_nick[-1]) + 1
    nick = ""
    for char in coded_nick[0:len(coded_nick) - 1]:
        char_index = mc_alphabet.index(char) - warp
        if char_index < 0:
            char_index = len(mc_alphabet) + char_index
        nick += mc_alphabet[char_index]
    return nick


if __name__ == "__main__":
    print(decode("ufzq2mnyjkt3e"))
