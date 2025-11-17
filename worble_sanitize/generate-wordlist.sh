#!/bin/sh

# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger@bbzsogr.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

./dep/acquire-src.sh
./dep/do-heavylifting.sh
./dep/remove-duplicates.sh
