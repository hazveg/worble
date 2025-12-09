# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger06@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from config import *
import sys

words = []
info_model = {}

unigram = {}

trigram_index = {}
trigram_weights = []

slotgram_index = {}
slotgram_weights = []

def source_words():
    # goofy ahh language
    global words

    file = open(SRC, "r")
    words = file.read().split()

def load_info_model(file_lines, start, end):
    global info_model
    
    # janky workaround, but it'll do
    prev_info_keyname = file_lines[start].split()[0]
    info_indices = []
    for line_idx in range(start, end):
        line = file_lines[line_idx]
        line_cols = line.split()

        info_keyname = line_cols[0]
        index = int(line_cols[1])
        if info_keyname != prev_info_keyname:
            info_model[prev_info_keyname] = info_indices
            info_indices = []

        info_indices.append(index)
        prev_info_keyname = info_keyname

def load_unigram(file_lines, start, end):
    global unigram

    for line_idx in range(start, end):
        line = file_lines[line_idx]
        line_cols = line.split()

        char = line_cols[0]
        weight = float(line_cols[1])

        unigram[char] = weight

def load_trigram_index(file_lines, start, end):
    global trigram_index

    for line_idx in range(start, end):
        line = file_lines[line_idx]
        line_cols = line.split()

        tup_0 = int(line_cols[0])
        tup_1 = int(line_cols[1])
        weights_idx = int(line_cols[2])
        
        trigram_index[(tup_0, tup_1)] = weights_idx

def load_trigram_weights(file_lines, start, end):
    global trigram_weights

    context_weights = {}
    for line_idx in range(start, end):
        line = file_lines[line_idx]
        line_cols = line.split()

        char = line_cols[0]
        weight = float(line_cols[1])

        context_weights[char] = weight
        if (len(context_weights) >= len(VALID_CHARS)):
            trigram_weights.append(context_weights)
            context_weights = {}

def load_model(file):
    file = open(file, "r")
    file_str = file.read()
    lines = file_str.split('\n')
    
    header = lines[0]
    header_cols = header.split()
    header_string = header_cols[0]
    directory_start = int(header_cols[1])
    if (header_string != HEADER_STR):
        print(f"Attempted to load model \"{file}\", where version \
              \"{header_string}\" doesn't match configured version \
              \"{HEADER_STR}\"; exiting.", file=sys.stderr)
        sys.exit(1)
    
    # print(f"header_string: {header_string}, directory_start: {directory_start}")
    dir_entries = []
    for directory_entry_idx in range(directory_start, len(lines)):
        dir_entry = lines[directory_entry_idx]
        if (len(dir_entry) == 0):
            continue

        print(dir_entry)
        dir_entries.append(dir_entry)

    for dir_entry in dir_entries:
        dir_entry_cols = dir_entry.split()
        dir_entry_name = dir_entry_cols[0]
        dir_entry_start_line = int(dir_entry_cols[1])
        dir_entry_closing_line = int(dir_entry_cols[2])

        # print(f"dir_entry_name: {dir_entry_name}, dir_entry_start_line: {dir_entry_start_line}, dir_entry_closing_line: {dir_entry_closing_line}")

        match dir_entry_name:
            case "INFO_MODEL":
                load_info_model(lines, dir_entry_start_line, dir_entry_closing_line)
            case "UNIGRAM":
                load_unigram(lines, dir_entry_start_line, dir_entry_closing_line)
            case "TRIGRAM_INDEX":
                load_trigram_index(lines, dir_entry_start_line, dir_entry_closing_line)
            case "TRIGRAM_WEIGHTS":
                load_trigram_weights(lines, dir_entry_start_line, dir_entry_closing_line)
            case _:
                print(f"Invalid lump \"{dir_entry_name}\" found in model \
                      \"{file}\", skipping...")
                continue

def determine_array_intersection(a, b):
    return list(set(a) & set(b))

def info_keyname(char, keyw, idx):
    return f"{char}_{keyw}_{idx}"

def limit_search_area_with_infos(words, infos):
    global info_model

    applicable_word_indices = []
    
    # if no infos are provided, generate a list of indices for the whole word
    # list. 06.12.2025: FUCK I FORGOT TO PUSH THIS FOR THE DEMO
    if len(infos) == 0:
        applicable_word_indices = range(len(words))
        return applicable_word_indices

    for idx, info in enumerate(infos):
        if idx == 0:
            applicable_word_indices = info_model[info]
            continue
        
        curr_info_array = info_model[info]
        applicable_word_indices = determine_array_intersection(
            applicable_word_indices, curr_info_array)

    return applicable_word_indices

def P_unigram(char):
    global unigram
    return unigram[char]

def P_trigram(word_idx, char_idx):
    global trigram_index
    global trigram_weights

    char = words[word_idx][char_idx]
    context_weights_idx = trigram_index[(word_idx, char_idx)]
    return trigram_weights[context_weights_idx][char]

def P_slotgram(word_idx, slot_idx):
    global slotgram_index
    global slotgram_weights
    
    char = words[word_idx][slot_idx]
    context_weights_idx = slotgram_index[(word_idx, slot_idx)]
    return slotgram_weights[context_weights_idx][char]

def determine_word_probability(word_idx):
    probability = 1.0
    chars = list(words[word_idx])
    
    for char_idx, char in enumerate(chars):
        # we don't need to worry quite yet i think, but moving these numbers 
        # - either at base or at least here - into "log space" would afford 
        # us better numerical stability. the resulting probability we get 
        # from this function ends up in the 10^-[6;24] area. it'd certainly 
        # be more like people usually handle language models.
        # probability *= P_unigram(char)
        probability *= P_trigram(word_idx, char_idx)
        # probability *= P_slotgram(word_idx, char_idx)

    return probability

def rank_words(word_indices):
    ranked_words = []
    for word_idx in word_indices:
        probability = determine_word_probability(word_idx)
        ranked_words.append((probability, word_idx))

    # lists don't sort implicitely apparently
    # unfortunately there is no reverse order sorting
    ranked_words.sort()
    
    for rank in ranked_words:
        print(f"{rank}: {rank[1]} = { words[rank[1]] }")

    return ranked_words

# this function returns the INDEX into the global words list
def determine_most_likely_next_word(infos):
    applicable_word_indices = limit_search_area_with_infos(words, infos)
    ranked_words = rank_words(applicable_word_indices)

    # we only want the most likely word, but maybe we can use the whole list one day?
    most_likely_word_tuple = ranked_words[-1]
    most_likely_word_index = most_likely_word_tuple[1]
    return most_likely_word_index

def init():
    global info_model
    global words

    source_words()
    load_model("worble_hax")

def main():
    init()
    print(info_model.keys())
    # test = [ "e_ndef_0", "d_def_0" ]
    test = []
    word_index = determine_most_likely_next_word(test)
    print(words[word_index])

if __name__ == "__main__":
    main()
