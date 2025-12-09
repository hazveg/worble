# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger06@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from config import *

src_str = ""
words = []
info_model = {}

unigram = {}

trigram_index = {}
trigram_weights = []

slotgram_index = {}
slotgram_weights = []

def source_corpus():
    # goofy ahh language
    global src_str
    global words

    file = open(CORPUS, "r")
    
    # we need both the string of the file and the words to generate the models
    src_str = file.read()
    words = src_str.split()

def info_keyname(char, keyw, idx):
    return f"{char}_{keyw}_{idx}"

def limit_search_area_with_info(info_model, info):
    if not info in info_model:
        return []

    return info_model[info]

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

def get_num_occurences_for_char(char):
    num_occurences = 0
    for src_char in list(src_str):
        if src_char != char:
            continue
        
        num_occurences += 1

    return num_occurences

# this function returns a new string where the character at idx in str 
# was replaced with char.
def replace_char_in_str(str, idx, char):
    tmp = list(str)
    tmp[idx] = char
    res = "".join(tmp)
    return res

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

"""
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
"""

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
        search_area = limit_search_area_with_info(info_model, info)

        for word_idx in search_area:
            word = words[word_idx]
            if not tmp in word:
                continue

            context_weights[char] += 1
            context_freq += 1
    
    return context_freq

"""
def set_slotgram_context_abs_freqs(context, slot_idx, context_weights):
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
"""

# normalize char weights, not in log space; multiplication still needed!
def normalize_context_weights(context_weights, context_freq):
    for char in VALID_CHARS:
        context_weights[char] = context_weights[char] / context_freq

def generate_info_model():
    global info_model
    global words

    for idx, word in enumerate(words):
        derive_info(idx, word)

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

"""
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

        context_freq = set_slotgram_context_abs_freqs(context, slot_idx, context_weights)
        normalize_context_weights(context_weights, context_freq)
"""

def dump_info_model(file_lines):
    global info_model

    starting_line = len(file_lines)
    for keyname, indices in info_model.items():
        for index in indices:
            file_lines.append(f"{keyname} {index}\n")
    closing_line = len(file_lines)
    return f"INFO_MODEL {starting_line} {closing_line}\n"

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
    dir_entries.append(dump_info_model(file_lines))
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

def init():
    global info_model
    global words

    source_corpus()

def main():
    init()

    generate_info_model()
    generate_unigram()
    generate_trigram()
    # generate_slotgram()

    dump_model()

if __name__ == "__main__":
    main()
