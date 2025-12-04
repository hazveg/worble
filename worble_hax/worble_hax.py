# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger@bbzsogr.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

SRC = "srcer.txt"

DEFINED_KEYWORD = "def"
CONTAINED_KEYWORD = "con"

VALID_CHARS = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'ä', 'ö', 'ü' ]

src_str = ""
words = []
info_indices = {}
unigram = {}

def source_words():
    # goofy ahh language
    global src_str
    global words

    file = open(SRC, "r")

    src_str = file.read()
    words = src_str.split()

def info_keyname(char, keyw, idx):
    return f"{char}_{keyw}_{idx}"

def derive_info(idx, word):
    global info_indices
    nth_occurence = {
        'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0,
        'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0,
        'k': 0, 'l': 0, 'm': 0, 'n': 0, 'o': 0,
        'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0,
        'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0,
        'z': 0, 'ä': 0, 'ö': 0, 'ü': 0,
    }

    chars = list(word)
    for char_idx, char in enumerate(chars):
        def_key = info_keyname(char, DEFINED_KEYWORD, char_idx)
        con_key = info_keyname(char, CONTAINED_KEYWORD, nth_occurence[char])
        nth_occurence[char] += 1

        if not def_key in info_indices:
            info_indices[def_key] = []
        if not con_key in info_indices:
            info_indices[con_key] = []

        info_indices[def_key].append(idx)
        info_indices[con_key].append(idx)

def generate_info_indices():
    for idx, word in enumerate(words):
        derive_info(idx, word)

def get_num_occurences_for_char(char):
    num_occurences = 0
    for src_char in list(src_str):
        if src_char != char:
            continue
        
        num_occurences += 1

    return num_occurences

def generate_unigram():
    global unigram

    total_num_words = len(words)
    # since we can guarantee that all words in the source list are 5 letters 
    # long, we can spare ourselves the headache of counting each char 
    # *individually*.
    total_num_letters = 5 * total_num_words

    # print(f"total_num_letters: {total_num_letters}")
    for char in VALID_CHARS:
        num_occurences = get_num_occurences_for_char(char)
        char_probability = num_occurences / total_num_letters # unigram is basically relative probability only

        unigram[char] = char_probability

        print(f"num_occurences for '{char}': {num_occurences}")
        print(f"probability for '{char}': {round(char_probability, 2)}")

def main():
    source_words()
    generate_info_indices()

    """
    print(list(INFO_INDICES.keys()))

    for idx in INFO_INDICES["x_con_0"]:
        print(WORDS[idx])
    """

    generate_unigram()
    # print(list(unigram.keys()))

if __name__ == "__main__":
    main()
