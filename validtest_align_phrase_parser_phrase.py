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
    parser.add_argument("f_input", type=str)  # input zh source file
    parser.add_argument("fe_file", type=str)
    parser.add_argument("ef_file", type=str)

    parser.add_argument("f_output", type=str)
    parser.add_argument("e_output", type=str)

    parser.add_argument('start_line', type=int, default=0)
    parser.add_argument('end_line', type=int, default=-1)  # -1 represents ends
    #parser.add_argument("parser_model_path", type=str)

    args = parser.parse_args()
    
    parser = CoreNLPParser(url='http://localhost:9001')
    print('parser generated!')

    with open(args.f_input, encoding='utf-8') as fin:
        f_line = [line.lower().strip().split() for line in fin]

    fe_phrases = get_giza_file_content(args.fe_file)
    ef_phrases = get_giza_file_content(args.ef_file)


    phrase_tag = ['NP', 'VP','ADJP', 'ADVP', 'CLP',  'CP',
                  'DNP', 'DP', 'DVP', 'FRAG', 'IP', 'LCP',
                  'LST', 'NP', 'PP', 'PRN', 'QP', 'UCP', 'VP']

    labled_phrase_number = 2  # each sentence has about 2 phrase labeled
    tagged_phrase_result = []  # tagged phrases for all corpus
    # to do some statistic for future
    sen_and_tagged_phrases = []
    exception_sen = []
    fe_ef_phrases = list(zip(fe_phrases, ef_phrases))
    file_f = [open(args.f_output+str(id4), mode='w', encoding="utf-8") for id4 in range(4)]
    file_e = [open(args.e_output+str(id4), mode='w', encoding="utf-8") for id4 in range(4)]

    for senid, f_sen in enumerate(f_line):
        print(senid)

        if senid < args.start_line:
            senid += 1
            print("skipped")
            continue
        if senid >= args.end_line and args.end_line != -1:
            break
        # parse zh sentence and select some phrase to tag
        p_phrase_trees = None
        try:
            p_parse_trees = list(parser.parse(parser.tokenize(' '.join(f_sen))))
        except ValueError:
            print('parsing fail')
            exception_sen.append(senid)
            p_parse_trees = [Tree.fromstring('(S (NULL ERROR))')]  # we simply give a dummy tree

        # create a dict to keep all phrase in different categories
        p_phrase_dict = {}
        for tag in phrase_tag:
            p_phrase_dict[tag] = []

        for one_tree in p_parse_trees:
            # print(one_tree)
            traverse(one_tree, p_phrase_dict, phrase_tag)

        # Get all phrase
        p_phrase_list = []  # (phrase, tags like np vp etc)
        for key in p_phrase_dict:
            for subtree in p_phrase_dict[key]:
                p_phrase_list.append((' '.join(subtree.leaves()), key))

        # to select some phrases randomly
        if labled_phrase_number < len(p_phrase_list):
            ph_index = random.sample(range(len(p_phrase_list)), labled_phrase_number)
        else:
            ph_index = random.sample(range(len(p_phrase_list)), int(len(p_phrase_list)/2+0.5))  # at lease there is one

        for id4 in range(4):

            fe_phrase, ef_phrase = fe_ef_phrases[id4*len(f_line) + senid]
            # assert f_sen == ef_phrase[0]
            if f_sen != ef_phrase[0]:
                print(senid, 'not equal')
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

            to_be_labeled = [] # (id in BP, tag type(like NP BP etc))
            for idx in ph_index:
                for pair_i, ph_pair in enumerate(BP):
                    if p_phrase_list[idx][0] == ph_pair[0]:
                        to_be_labeled.append((pair_i, p_phrase_list[idx][1]))

            filtered_to_be_labled = []  # (phrase id in BP, tags like np vp etc)
            # check if there is overlaps
            for BP_idx, ph_tag in to_be_labeled:
                overlap_flag = False
                f_start, f_end = BP_pos[BP_idx][0]
                for idx_fi, _ in filtered_to_be_labled:
                    f_start_fi, f_end_fi = BP_pos[idx_fi][0]
                    # 起始点 或结束点在另外一个 phrase内部 ,有以下几种情况，都要考虑
                    #  [        ]
                    #   [    ]   被比较的短语
                    #     [ ]
                    #     [   ]
                    # [   ]
                    if (f_start >= f_start_fi and f_start < f_end_fi) or \
                            (f_end-1 >= f_start_fi and f_end-1 < f_end_fi) or \
                            (f_start <= f_start_fi and f_end >= f_end_fi):
                        overlap_flag = True
                        break
                if not overlap_flag:
                    filtered_to_be_labled.append((BP_idx, ph_tag))

            tagged_phrase_result.append(filtered_to_be_labled)  # keep each line's tagged phrase to a list in order to output
            sen_and_tagged_phrases.append((len(ef_phrase[0]), len(fe_phrase[0]), len(filtered_to_be_labled)))
            # imbue the tag into the corpus
            # if insertted new item, the index following item will change, we must convert each word item into list
            f_wordlist_list = [[word] for word in ef_phrase[0]]
            e_wordlist_list = [[word] for word in fe_phrase[0]]
            for BP_idx, ph_tag in filtered_to_be_labled:
                f_st, f_end = BP_pos[BP_idx][0]
                e_st, e_end = BP_pos[BP_idx][1]
                f_wordlist_list[f_st].insert(0, '<'+ph_tag)  # insert the <tag
                f_wordlist_list[f_end-1].append('>')           # insert the >
                e_wordlist_list[e_st].insert(0, '<'+ph_tag)  # insert the <tag
                e_wordlist_list[e_end-1].append('>')           # insert the >

            f_wordlist = []
            e_wordlist = []
            for words in f_wordlist_list:
                f_wordlist.extend(words)
            for words in e_wordlist_list:
                e_wordlist.extend(words)
            # print(len(filtered_to_be_labled))
            # print(' '.join(f_wordlist))
            # print(' '.join(e_wordlist))
            file_f[id4].write(' '.join(f_wordlist))
            file_f[id4].write('\n')
            file_e[id4].write(' '.join(e_wordlist))
            file_e[id4].write('\n')
            # for BP_idx, ph_tag in filtered_to_be_labled:
            #     print('<%s %s   %s>' % (ph_tag, BP[BP_idx][0], BP[BP_idx][1], ), end='')
            # print('\n')


    with open('tag_phrase.pkl', 'wb') as f:
        pickle.dump(tagged_phrase_result, f)
    with open('sen_tag_phrase_info.pkl', 'wb') as f:
        pickle.dump(sen_and_tagged_phrases, f)

    ph_cn = None
    for ph_cn in zip(*sen_and_tagged_phrases):
        pass
    total_tagged_phrase = sum(ph_cn)
    ave_tagged = float(total_tagged_phrase)/len(sen_and_tagged_phrases)
    print('total tagged phrases:%d' % total_tagged_phrase)
    print('total sentences:%d' % len(sen_and_tagged_phrases))
    print('average tagged phrase:%f' % ave_tagged)
    print('tags count:%d' % len(phrase_tag))
    print('tags:%r' % phrase_tag)
    print('exception sen:%r' % exception_sen)
    with codecs.open('tagged_info.txt', mode='w', encoding="utf-8") as f:
        f.write('total tagged phrases:%d\n' % total_tagged_phrase)
        f.write('total sentences:%d\n' % len(sen_and_tagged_phrases))
        f.write('average tagged phrase:%f\n' % ave_tagged)
        f.write('tags count:%d\n' % len(phrase_tag))
        f.write('tags:%r\n' % phrase_tag)
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
