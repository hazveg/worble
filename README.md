<!--
SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger@bbzsogr.ch>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# worble

WIP wordle clone + probability and modeling hax

look you know what it is mischa.

## getting started

run `worble_sanitize/generate-wordlist.sh`, copy `srcer.txt` to `worble_hax`.
or just use the file i sent over teams, rename that to `srcer.txt`; same spot.

run `python worble_hax.py` to run whatever the hell `worble_sanitize` will 
become.

## worble_sanitize

- iot implemented in python at all. Mainly bases off of sh scripts.
- if you wanna change something you gotta do it in like wsl or something.

## worble_hax

- implemented in python, should be workable on windows.

### stupid-ass summary

currently only preprocesses whatever bits of information that wordle can give 
you for a selected word and gathers all words that have that rule apply to 
them in arrays. every array is assigned to one bit of information.

btw: a "bit" of information refers not to the definition within information 
theory, but rather just whether a letter lights up yellow or green and its 
index into the word.

### clever-ass example

> in an imagined scenario...

let's say we open with `PLUME`.

wordle tells us...

- that `P` is contained in the word and is in the correct slot => `green P`.
- that `E` is contained in the word, but not in the right slot => `yellow E`.

we shall henceforth define green bits of information as "defined", thus 
abbreviated to `def`. yellow bits of information as "contained"; `con`.

arrays corresponding to the two bits of information have already been 
preprocessed. namely - at least in the current implementation with 
dictionarys - `p_def_0` and `e_con_0`. We determine the intersection of the 
arrays assigned to these keys to get a list of words where the known bits of 
information apply. e.g.

```
PENIS
PEEER
...
```

the next step beyond this point would be to rank these words through letter 
occurence probability. we'll do this... whenever we fucking feel like it ig.

#### comment on key naming scheme

- keys are named after the format defined in `keyname()`.
- i'd drop the dictionary approach the moment we go to a language with 
  competent structs, enums and ptrs. => tree data structure

for definitions '`def`', `idx` denotes the index within the word at which the 
letter is located. i.e. `ä_def_4` means that we got a green `ä` as the fifth 
letter.

for contains '`con`', `idx` denotes the `n`th time this letter appears in a 
word. so in the case of `PEEER` from above - definition: one who pees - it 
would be in an array assigned to the key `e_con_2` (we start the nth 
occurence counter at 0 lol).

### TODO:

- evaluate performance of calculating array intersections, perhaps 
  preprocessing of these is needed too.
- switch model to containing indices into the source word list instead of 
  duping the strings over and fucking over.
- get a ranking system working.

> and probably some other things, but i don't know any webdev lol
