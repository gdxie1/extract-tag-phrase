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
    
    parser.add_argument("fe_file", type=str)
    parser.add_argument("ef_file", type=str)

    #parser.add_argument("seg_model_path", type=str)
    #parser.add_argument("parser_model_path", type=str)

    args = parser.parse_args()
    
    parser = CoreNLPParser(url='http://localhost:9001')
    print('parser generated!')

    fe_phrases = get_giza_file_content(args.fe_file)
    ef_phrases = get_giza_file_content(args.ef_file)


    senid = 0
    phrase_tag = ['NP', 'VP','ADJP', 'ADVP', 'CLP',  'CP',
                  'DNP', 'DP', 'DVP', 'FRAG', 'IP', 'LCP',
                  'LST', 'NP', 'PP', 'PRN', 'QP', 'UCP', 'VP']

    phrase_result = []  # segment result
    labled_phrase_number = 2  # each sentence has about 2 phrase labeled
    for fe_phrase, ef_phrase in zip(fe_phrases, ef_phrases):
        print(senid)
        # stopline = 1899
        # if senid != stopline:
        #     continue
            # senid = stopline
        fe_alignment, ef_alignment = get_alignments(fe_phrase, ef_phrase)
        alignment = do_alignment(fe_alignment, ef_alignment,
                                 len(ef_phrase[0]), len(fe_phrase[0]))
        # fe_phrase = fe_phrases[id]
        # ef_phrase = ef_phrases[id]
        BP, BP_pos = phrase_extraction(fe_phrase[0], ef_phrase[0], alignment)  # fe_phrase[0] 是 e 句子
        f_sen = ' '.join(ef_phrase[0])
        p_parse_trees = list(parser.parse(parser.tokenize(f_sen)))
        
        # create a dict to keep all phrase in different categories
        p_phrase_dict = {} 
        for tag in phrase_tag:
            p_phrase_dict[tag] = []

        for one_tree in p_parse_trees:
            # print(one_tree)
            traverse(one_tree, p_phrase_dict, phrase_tag)

        # Get all phrase
        p_phrase_list = []
        for key in p_phrase_dict:
            for subtree in p_phrase_dict[key]:
                p_phrase_list.append(' '.join(subtree.leaves()))

        if labled_phrase_number < len(p_phrase_list):
            ph_index = random.sample(range(len(p_phrase_list)), labled_phrase_number)
        else:
            ph_index = random.sample(range(len(p_phrase_list)), int(len(p_phrase_list)/2+0.5))  # at lease there is one
        #align_ph_f = zip(*BP)[0]
        to_be_labeled = []
        for idx in ph_index:
            for pair_i, ph_pair in enumerate(BP):
                if p_phrase_list[idx] == ph_pair[0]:
                    to_be_labeled.append(pair_i)

        filtered_to_be_labled = []
        # check if there is overlaps
        for idx in to_be_labeled:
            overlap_flag = False
            f_start, f_end = BP_pos[idx][0]
            for idx_fi in filtered_to_be_labled:
                f_start_fi, f_end_fi = BP_pos[idx_fi][0]
                # 起始点 或结束点在另外一个 phrase内部
                if (f_start >= f_start_fi and f_start < f_end_fi) or (f_end >= f_start_fi and f_end < f_end_fi):
                    overlap_flag = True
                    break
            if not overlap_flag:
                filtered_to_be_labled.append(idx)
        for idx in filtered_to_be_labled:
            print('<%s   %s>' % BP[idx], end='')
        print('\n')


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
        senid+=1

    # with codecs.open('phrase.en', 'w', encoding='utf-8') as f_e:
    #     with codecs.open('phrase.zh', 'w', encoding='utf-8') as f_f:
    #         for phrase_seg in phrase_result:  # each sentence
    #             f_seg = ''
    #             e_seg = ''
    #             for (ph_f, ph_e), _ in phrase_seg:  # each sentence's phrase list
    #                 f_seg += ph_f
    #                 f_seg += ' | '
    #                 e_seg += ph_e
    #                 e_seg += ' | '
    #             f_e.write(e_seg)
    #             f_e.write('\n')
    #             f_f.write(f_seg)
    #             f_f.write('\n')
    # with open('phrase.dat', 'wb') as f:
    #     pickle.dump(phrase_result, f)

