# coding=utf-8
# chcp 65001

"""
find candidates phrases from parsed sentences which are parsed and stored in a files
then using the giza++'s alignment results to find corresponding phrases in target side
then tagged the found phrase in both source side and target side
"""
import pickle
import random
import argparse
from phrase_extraction import phrase_extraction
from alignment import get_alignments, do_alignment
from nltk.tree import Tree

def get_giza_file_content(file_name):
    file_content = get_data_from_file(file_name)
    return [(file_content[i + 1].split(), file_content[i + 2])
            for i in range(0, len(file_content) - 1, 3)]


def get_data_from_file(file_name):
    with open(file_name, mode='r', encoding="utf-8") as file_:
        content = [line.lower().strip() for line in file_]
    # avoid to be segmented with the Record Seperator
    # content = []
    # with codecs.open(file_name, encoding="utf-8") as file_:
    #     for i, line in enumerate(file_):
    #         new_line = line.lower().strip()
    #         if i % 3 == 0 and new_line[0] == u'#': #every three lines there will be the # line
    #             content.append(new_line)
    #         else:
    #             content[i - 1] += new_line
    return content


def load_sentences(file_name):
    file_content = get_data_from_file(file_name)
    return [sentence.split() for sentence in file_content]


def load_alignment(file_name):
    file_content = get_data_from_file(file_name)
    alignment = []
    for content_item in file_content:
        single_align = content_item.split()
        alignment.append([(pairs.split("-")[0], pairs.split("-")[1]) \
                          for pairs in single_align])

    return alignment


def traverse(t, ph_dict, ph_tag):
    try:
        tag = t.label()
    except AttributeError:
        return
    if tag in ph_tag:
        ph_dict[tag].append(t)  # keep the tree structure
    for subtree in t:
        if type(subtree) == Tree:
            traverse(subtree, ph_dict, ph_tag)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("f_file", type=str)
    # parser.add_argument("e_file", type=str)
    # parser.add_argument("align", type=str)

    parser.add_argument("fe_file", type=str, help="GIZA++'s result. e.g. zh_en.A3.final  en is the target language")
    parser.add_argument("ef_file", type=str, help="GIZA++'s result. e.g. en_zh.A3.final")

    parser.add_argument("f_original_file", type=str, help="original f file")

    # parser.add_argument("fe_output", type=str, help="tagged f result")
    # parser.add_argument("ef_output", type=str, help="tagged e result")

    #parser.add_argument("parser_model_path", type=str)

    args = parser.parse_args()


    fe_phrases = get_giza_file_content(args.fe_file)
    ef_phrases = get_giza_file_content(args.ef_file)

    file_f_ori = open(args.f_original_file, mode='rt', encoding="utf-8")

    senid = 0

    exception_sen = []
    for fe_phrase, ef_phrase in zip(fe_phrases, ef_phrases):
        senid += 1
        print(senid)

        # fe_alignment, ef_alignment = get_alignments(fe_phrase, ef_phrase)
        # # alignment = do_alignment(fe_alignment, ef_alignment,
        #                          len(ef_phrase[0]), len(fe_phrase[0]))

        align_e = ' '.join(ef_phrase[0])
        align_e += '\n'
        # BP, BP_pos = phrase_extraction(fe_phrase[0], ef_phrase[0], alignment)  # fe_phrase[0] 是 e 句子

        line = file_f_ori.readline()
        if align_e != line.lower():
            print("error at line %d" % senid)
            break
