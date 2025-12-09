# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger06@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import math

SRC = "srcester.txt"

DEFINED_KEYWORD = "def"
CONTAINED_KEYWORD = "con"
NOTDEFINED_KEYWORD = "ndef"

SLOT_CONTROLCHAR = '_'

HEADER_STR = "WORBLE_HAX_MODEL_0"

VALID_CHARS = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'ä', 'ö', 'ü' ]

src_str = ""
words = []

info_model = {}

unigram = {}

trigram_index = {}
trigram_weights = []

slotgram_index = {}
slotgram_weights = []

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
    global info_model
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

        if not def_key in info_model:
            info_model[def_key] = []
        if not con_key in info_model:
            info_model[con_key] = []

        info_model[def_key].append(idx)
        info_model[con_key].append(idx)

    for char in nth_occurence.keys():
        if nth_occurence[char] != 0:
            continue
        
        ndef_key = info_keyname(char, NOTDEFINED_KEYWORD, 0)

        if not ndef_key in info_model:
            info_model[ndef_key] = []

        info_model[ndef_key].append(idx)

def generate_info_model():
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

    for char in VALID_CHARS:
        num_occurences = get_num_occurences_for_char(char)
        char_probability = num_occurences / total_num_letters # unigram is basically relative probability only

        unigram[char] = char_probability

def define_trigram_contexts():
    global trigram_index
    global words

    required_context_sequence = {}
    context_rover = 0
    for word_idx, word in enumerate(words):
        chars = list(word)
        for char_idx, char in enumerate(chars):
            context_str = ""
            context_len = min(char_idx, 2)
            if context_len != 0:
                context_str = word[char_idx - context_len:char_idx]

            if not context_str in required_context_sequence:
                required_context_sequence[context_str] = context_rover
                context_rover += 1

            context_idx = required_context_sequence[context_str]
            trigram_index[(word_idx, char_idx)] = context_idx
    
    return required_context_sequence

def set_trigram_context_abs_freqs(context, context_weights):
    context_freq = 0
    for char in VALID_CHARS:
        # for now we'll store the absolute frequency
        context_weights[char] = 0
        if len(context) == 0:
            context_weights[char] = unigram[char]
            context_freq = 1
            continue

        tmp = context + char
        # we limit the search area to words that have the context's first 
        # char defined
        info = info_keyname(tmp[0], CONTAINED_KEYWORD, 0)
        search_area = limit_search_area_with_info(info)

        for word_idx in search_area:
            word = words[word_idx]
            if not tmp in word:
                continue

            context_weights[char] += 1
            context_freq += 1
    
    return context_freq

def generate_trigram():
    global trigram_weights
    global words

    required_context_sequence = define_trigram_contexts()
    total_num_contexts = len(required_context_sequence)
    # init each context as a dict uniquely instead of `total_num_contexts` 
    # copies of the same blank dictionary
    trigram_weights = [{} for i in range(total_num_contexts)]
    
    for context, weights_idx in required_context_sequence.items():
        context_weights = trigram_weights[weights_idx]

        context_freq = set_trigram_context_abs_freqs(context, context_weights)
        normalize_context_weights(context_weights, context_freq)

# this function returns a new string where the character at idx in str 
# was replaced with char.
def replace_char_in_str(str, idx, char):
    tmp = list(str)
    tmp[idx] = char
    res = "".join(tmp)
    return res

def define_slotgram_contexts():
    global slotgram_index
    global words

    required_context_sequence = {}
    context_rover = 0
    for word_idx, word in enumerate(words):
        for slot_idx in range(5):
            # generate context_str and ensure that there are only unique 
            # entries, initialize empty dictionary for each slotgram.
            context_str = replace_char_in_str(word, slot_idx, SLOT_CONTROLCHAR)
            
            if not context_str in required_context_sequence:
                required_context_sequence[context_str] = context_rover
                context_rover += 1
        
            context_idx = required_context_sequence[context_str]
            slotgram_index[(word_idx, slot_idx)] = context_idx

    return required_context_sequence

def limit_search_area_with_info(info):
    global info_model
    if not info in info_model:
        return []

    return info_model[info]

def set_context_abs_freqs(context, slot_idx, context_weights):
    context_freq = 0
    for char in VALID_CHARS:
        # for now we'll store the absolute freq
        context_weights[char] = 0
        tmp = replace_char_in_str(context, slot_idx, char)
        # we limit the search area to words that have the context's first 
        # char defined
        info = info_keyname(tmp[0], DEFINED_KEYWORD, 0)
        search_area = limit_search_area_with_info(info)

        for word_idx in search_area:
            word = words[word_idx]
            if word != tmp:
                continue

            context_weights[char] += 1
            context_freq += 1

    return context_freq

# normalize char weights, not in log space; multiplication still needed!
def normalize_context_weights(context_weights, context_freq):
    for char in VALID_CHARS:
        context_weights[char] = context_weights[char] / context_freq

def generate_slotgram():
    global slotgram_weights
    global words
    
    required_context_sequence = define_slotgram_contexts()
    total_num_contexts = len(required_context_sequence)
    # init each context as a dict uniquely instead of `total_num_contexts` 
    # copies of the same blank dictionary
    slotgram_weights = [{} for i in range(total_num_contexts)]

    for context, weights_idx in required_context_sequence.items():
        slot_idx = context.index(SLOT_CONTROLCHAR)
        context_weights = slotgram_weights[weights_idx]

        context_freq = set_context_abs_freqs(context, slot_idx, context_weights)
        normalize_context_weights(context_weights, context_freq)

def load_unigram(file_lines, start, end):
    global unigram

    for line_idx in range(start, end + 1):
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
        # wrong version
        return
    
    print(f"header_string: {header_string}, directory_start: {directory_start}")
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

        print(f"dir_entry_name: {dir_entry_name}, dir_entry_start_line: {dir_entry_start_line}, dir_entry_closing_line: {dir_entry_closing_line}")

        match dir_entry_name:
            case "UNIGRAM":
                print("processing unigram")
                load_unigram(lines, dir_entry_start_line, dir_entry_closing_line)
            case "TRIGRAM_INDEX":
                print("processing trigram index")
                load_trigram_index(lines, dir_entry_start_line, dir_entry_closing_line)
            case "TRIGRAM_WEIGHTS":
                print("processing trigram weights")
                load_trigram_weights(lines, dir_entry_start_line, dir_entry_closing_line)
            case _:
                # invalid directory entry
                continue

def init():
    source_words()

    generate_info_model()
    
    load_model("worble_hax")
    # generate_unigram()
    # generate_trigram()
    # generate_slotgram()


def dump_unigram(file_lines):
    global unigram
    
    starting_line = len(file_lines)
    for char, weight in unigram.items():
        file_lines.append(f"{char} {weight}\n")
    closing_line = len(file_lines)
    return f"UNIGRAM {starting_line} {closing_line}\n"

def dump_trigram_index(file_lines):
    global trigram_index
    
    starting_line = len(file_lines)
    for tup, idx in trigram_index.items():
        file_lines.append(f"{tup[0]} {tup[1]} {idx}\n")
    closing_line = len(file_lines)
    return f"TRIGRAM_INDEX {starting_line} {closing_line}\n"

def dump_trigram_weights(file_lines):
    global trigram_weights

    starting_line = len(file_lines)
    for context in trigram_weights:
        for char, weight in context.items():
            file_lines.append(f"{char} {weight}\n")
    closing_line = len(file_lines)
    return f"TRIGRAM_WEIGHTS {starting_line} {closing_line}\n"

def dump_model():
    file_lines = []
    dir_entries = []
    
    # we'll set the header later
    file_lines.append("")
    dir_entries.append(dump_unigram(file_lines))
    dir_entries.append(dump_trigram_index(file_lines))
    dir_entries.append(dump_trigram_weights(file_lines))

    directory_start = len(file_lines)
    file_lines[0] = f"{HEADER_STR} {directory_start}\n"
    for entry in dir_entries:
        file_lines.append(entry)
    
    file_str = ""
    for line in file_lines:
        file_str += line

    print(file_str)

def destroy():
    dump_model()

def determine_array_intersection(a, b):
    return list(set(a) & set(b))

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

def limit_search_area_with_infos(infos):
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

def rank_words(word_indices):
    ranked_words = []
    for word_idx in word_indices:
        probability = determine_word_probability(word_idx)
        ranked_words.append((probability, word_idx))

    # lists don't sort implicitely apparently
    # unfortunately there is no reverse order sorting
    ranked_words.sort()
    
    """
    for rank in ranked_words:
        print(f"{rank}: {rank[1]} = { words[rank[1]] }")
    """

    return ranked_words

# this function returns the INDEX into the global words list
def determine_most_likely_next_word(infos):
    applicable_word_indices = limit_search_area_with_infos(infos)
    ranked_words = rank_words(applicable_word_indices)

    # we only want the most likely word, but maybe we can use the whole list one day?
    most_likely_word_tuple = ranked_words[-1]
    most_likely_word_index = most_likely_word_tuple[1]
    return most_likely_word_index

def main():
    init()
    # test = [ "e_ndef_0", "d_def_0" ]
    test = []
    word_index = determine_most_likely_next_word(test)
    print(words[word_index])
    # destroy()

if __name__ == "__main__":
    main()
