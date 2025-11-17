#!/bin/sh

# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger@bbzsogr.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

INPUTFILE="src.txt"
OUTPUTFILE="srcer.txt"

sort $INPUTFILE | uniq > srcer.txt
