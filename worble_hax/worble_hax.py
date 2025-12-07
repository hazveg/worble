# SPDX-FileCopyrightText: 2025 Aaron Jäger <aaron.jaeger@bbzsogr.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

SRC = "srcer.txt"

DEFINED_KEYWORD = "def"
CONTAINED_KEYWORD = "con"
NOTDEFINED_KEYWORD = "ndef"

VALID_CHARS = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'ä', 'ö', 'ü' ]

src_str = ""
words = []
info_indices = {}
unigram = {}
fivegram = {}
slotgram = {}

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
    global info_indices
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

        if not def_key in info_indices:
            info_indices[def_key] = []
        if not con_key in info_indices:
            info_indices[con_key] = []

        info_indices[def_key].append(idx)
        info_indices[con_key].append(idx)

    for char in nth_occurence.keys():
        if nth_occurence[char] != 0:
            continue
        
        ndef_key = info_keyname(char, NOTDEFINED_KEYWORD, 0)

        if not ndef_key in info_indices:
            info_indices[ndef_key] = []

        info_indices[ndef_key].append(idx)

def generate_info_indices():
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

    # print(f"total_num_letters: {total_num_letters}")
    for char in VALID_CHARS:
        num_occurences = get_num_occurences_for_char(char)
        char_probability = num_occurences / total_num_letters # unigram is basically relative probability only

        unigram[char] = char_probability

        # print(f"num_occurences for '{char}': {num_occurences}")
        # print(f"probability for '{char}': {round(char_probability, 2)}")

def generate_fivegram():
    global fivegram
    print("TODO: implement fivegram generation")

# this function returns a new string where the character at idx in str 
# was replaced with char.
def replace_char_in_str(str, idx, char):
    tmp = list(str)
    tmp[idx] = char
    res = "".join(tmp)
    return res

# not a fan of using strings as the keys, but with dictionaries this is the 
# only way, with proper structs i'd create a tree structure where two noes 
# share a child node.
def define_slotgram_contexts():
    global slotgram
    global words

    for word in words:
        chars = list(word)

        for slot_idx in range(5):
            # generate context_str and ensure that there are only unique 
            # entries, initialize empty dictionary for each slotgram.
            context_str = replace_char_in_str(word, slot_idx, '_')
            slotgram[context_str] = {}

def generate_slotgram():
    global slotgram
    global words
    
    define_slotgram_contexts()

    total_num_contexts = len(slotgram)
    for context in slotgram.keys():
        slot_idx = context.index('_')
        context_freq = 0
        for char in VALID_CHARS:
            # for now unigram will store absolute freq of char in context
            slotgram[context][char] = 0
            tmp = replace_char_in_str(context, slot_idx, char)

            for word in words:
                if word != tmp:
                    continue

                slotgram[context][char] += 1
                context_freq += 1
        
        # normalize char <-> context weights
        # print(f"before: {slotgram[context_str]}")
        for char in VALID_CHARS:
            slotgram[context][char] /= context_freq
            slotgram[context][char] /= total_num_contexts
        # print(f"after: {slotgram[context_str]}")

def validate_unigram_weights():
    global unigram

    total = 0.0
    for char in unigram.keys():
        total += unigram[char]

    print(total)

def validate_fivegram_weights():
    global fivegram
    print("TODO: implement fivegram")

def validate_slotgram_weights():
    global slotgram

    total = 0.0
    for context in slotgram.keys():
        for char in slotgram[context].keys():
            total += slotgram[context][char]

    print(total)

def init():
    source_words()
    generate_info_indices()
    generate_unigram()
    # validate_unigram_weights()
    # generate_fivegram()
    generate_slotgram()
    # validate_slotgram_weights()

def determine_array_intersection(a, b):
    return list(set(a) & set(b))

def P_unigram(char):
    global unigram
    return unigram[char]

def P_fivegram(char):
    global fivegram
    print("TODO: implement fivegram")
    return 0.0

def P_slotgram(word, slot_idx):
    global slotgram
    char = word[slot_idx]
    context = replace_char_in_str(word, slot_idx, '_')
    return slotgram[context][char]

def determine_word_probability(word):
    probability = 1.0
    chars = list(word)
    
    for char_idx, char in enumerate(chars):
        # we don't need to worry quite yet i think, but moving these numbers 
        # - either at base or at least here - into "log space" would afford 
        # us better numerical stability. the resulting probability we get 
        # from this function ends up in the 10^-[6;9] area. it'd certainly 
        # be more like people usually handle language models
        # probability *= P_unigram(char)
        probability *= P_slotgram(word, char_idx)

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
            applicable_word_indices = info_indices[info]
            continue
        
        curr_info_array = info_indices[info]
        applicable_word_indices = determine_array_intersection(
            applicable_word_indices, curr_info_array)

    return applicable_word_indices

def rank_words(word_indices):
    ranked_words = []
    for index in word_indices:
        word = words[index]
        probability = determine_word_probability(word)
        ranked_words.append((probability, index))

    # lists don't sort implicitely apparently
    # unfortunately there is no reverse order sorting
    ranked_words.sort()
    return ranked_words

# this function returns the INDEX into the global words list
def determine_most_likely_next_word(infos):
    applicable_word_indices = limit_search_area_with_infos(infos)
    ranked_words = rank_words(applicable_word_indices)
    # print(ranked_words)
    # print(words[ranked_words[-1][1]])

    # we only want the most likely word, but maybe we can use the whole list one day?
    most_likely_word_tuple = ranked_words[-1]
    most_likely_word_index = most_likely_word_tuple[1]
    return most_likely_word_index

def main():
    init()
    test = [ "e_ndef_0", "d_def_0" ]
    word_index = determine_most_likely_next_word(test)
    print(words[word_index])

if __name__ == "__main__":
    main()
