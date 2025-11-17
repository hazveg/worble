# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger@bbzsogr.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import re

SRC = "wortliste.txt"
ENCODING = "utf-8"

def contains_invalid(word):
    return bool(re.search(r'[^a-zäöü]', word))

def main():
    file = open(SRC, "r", encoding=ENCODING)
    content = file.read()

    for line in content.split():
        line = line.replace('ß', "ss")
        line = line.lower()

        if contains_invalid(line):
            continue
        if len(line) != 5:
            continue

        print(line)

    file.close()

if __name__ == "__main__":
    main()
