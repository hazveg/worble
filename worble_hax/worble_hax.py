# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger@bbzsogr.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

SRC = "srcer.txt"

DEFINED_KEYWORD = "def"
CONTAINED_KEYWORD = "con"

intel = { }

def keyname(char, keyw, idx):
    return f"{char}_{keyw}_{idx}"

def derive_information(word):
    char_idx = 0
    nth_occurence = {
        'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0,
        'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0,
        'k': 0, 'l': 0, 'm': 0, 'n': 0, 'o': 0,
        'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0,
        'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0,
        'z': 0, 'ä': 0, 'ö': 0, 'ü': 0,
    }

    chars = list(word)
    for char in chars:
        def_key = keyname(char, DEFINED_KEYWORD, char_idx)
        char_idx += 1
        con_key = keyname(char, CONTAINED_KEYWORD, nth_occurence[char])
        nth_occurence[char] += 1

        if not def_key in intel:
            intel[def_key] = []
        if not con_key in intel:
            intel[con_key] = []

        intel[def_key].append(word)
        intel[con_key].append(word)

file = open(SRC, "r")
words = file.read().split()

for word in words:
    derive_information(word)

print(list(intel.keys()))
print(intel["x_con_0"])
