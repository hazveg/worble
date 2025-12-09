# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger06@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import re

SRC = "derewo-v-ww-bll-320000g-2012-12-31-1.0.txt"
ENCODING = "latin-1"

def contains_invalid(word):
    return bool(re.search(r'[^a-zäöü]', word))

def main():
    file = open(SRC, "r", encoding=ENCODING)
    content = file.read()

    for line in content.split('\n'):
        columns = line.split()
        if len(columns) == 0:
            continue

        word = columns[0]
        word = word.replace('ß', "ss")
        word = word.lower()

        if contains_invalid(word):
            continue
        if len(word) != 5:
            continue

        print(word)

    file.close()

if __name__ == "__main__":
    main()
