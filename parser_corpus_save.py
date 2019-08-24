# coding=utf-8
# chcp 65001
# import csv
import pickle
import random
import codecs
import argparse
from collections import Counter
from phrase_extraction import phrase_extraction
from alignment import get_alignments, do_alignment
from nltk.parse import CoreNLPParser
from nltk.tree import Tree

from nltk.tag.stanford import StanfordPOSTagger
def get_giza_file_content(file_name):
    file_content = get_data_from_file(file_name)
    return [(file_content[i + 1].split(), file_content[i + 2])
            for i in range(0, len(file_content) - 1, 3)]


def get_data_from_file(file_name):
    with codecs.open(file_name, encoding="utf-8") as file_:
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
    
    parser.add_argument("--input", type=str, required=True,)
    parser.add_argument("--output", type=str, required=True,)

    args = parser.parse_args()
    
    parser = CoreNLPParser(url='http://localhost:9001')
    print('parser generated!')
    exception_sen = []
    tree_list = []
    p_phrase_trees = None
    f_input = codecs.open(args.input, 'rt', 'utf-8')

    # f_output = codecs.open(args.output, 'rt', 'utf-8')
    f_output = open(args.output, 'wb')
    for senid, line in enumerate(f_input):
        if senid > 10:
            break
        try:
            p_parse_trees = list(parser.parse(parser.tokenize(line)))
        except ValueError:
            print('parsing fail')
            exception_sen.append(senid)
            p_parse_trees = [Tree.fromstring('(S (NULL ERROR))')]  # we simply give a dummy tree

        pickle.dump(tree_list, f_output)
        # str_tree = ' '.join(p_parse_trees)
        # f_output.write(str_tree)
        # f_output.write('\n')

        # tree_list.append(p_parse_trees)
    f_input.close()
    f_output.close()

    # with open(args.output, 'wb') as f:
    #     pickle.dump(tree_list, f)

    print('exception sen:%r' % exception_sen)
    with codecs.open('tagged_info.txt', mode='w', encoding="utf-8") as f:
        f.write('exception sen:%r\n' % exception_sen)


# ADJP adjective phrase
# ADVP adverbial phrase headed by AD (adverb)
# CLP classifier phrase
# CP clause headed by C (complementizer)
# DNP phrase formed by “XP + DEG”
# DP determiner phrase
# DVP phrase formed by “XP + DEV”
# FRAG fragment
# IP simple clause headed by I (INFL)
# LCP phrase formed by “XP + LC”
# LST list marker
# NP noun phrase
# PP preposition phrase
# PRN parenthetical
# QP quantifier phrase
# UCP unidentical coordination phrase
# VP verb phrase

        #list(parser.raw_parse("the quick brown fox jumps over the lazy dog"))
        # [Tree('ROOT', [Tree('NP', [Tree('NP', [Tree('DT', ['the']), Tree('JJ', ['quick']), Tree('JJ', ['brown']), Tree('NN', ['fox'])]), Tree('NP', [Tree('NP', [Tree('NNS', ['jumps'])]), Tree('PP', [Tree('IN', ['over']), Tree('NP', [Tree('DT', ['the']), Tree('JJ', ['lazy']), Tree('NN', ['dog'])])])])])])]
        # phrase_result.append(phrase_seg)

