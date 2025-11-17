#!/bin/sh

# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger@bbzsogr.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# this source bases upon the same code that debian's wngerman and wswiss 
# packages do. it includes some pretty fucking stupid words though. so i've 
# elected to not bother with that shit.
# wget https://sourceforge.net/projects/germandict/files/german.7z/download
# 7z e download german.dic
# rm download

# https://github.com/davidak/wortliste
# ^ this thing's gpl licensed btw, fun. ... nvm they're both gpl licensed.
wget https://raw.githubusercontent.com/davidak/wortliste/refs/heads/master/wortliste.txt
