# coding=utf-8
# chcp 65001
"""
extract phrases and probability from the *.A3.final of giza++
"""
#import csv
import pickle
import codecs
import argparse
from collections import Counter
from phrase_extraction import phrase_extraction
from alignment import get_alignments, do_alignment


def get_giza_file_content(file_name):
    file_content = get_data_from_file(file_name)
    return [(file_content[i+1].split(), file_content[i+2])
            for i in range(0, len(file_content)-1, 3)]


def get_data_from_file(file_name):
    with codecs.open(file_name, encoding="utf-8") as file_:
        content = [ line.lower().strip() for line in file_ ]
    return content


def load_sentences(file_name):
    file_content = get_data_from_file(file_name)
    return [ sentence.split() for sentence in file_content ]


def load_alignment(file_name):
    file_content = get_data_from_file(file_name)
    alignment = []
    for content_item in file_content:
        single_align = content_item.split()
        alignment.append([ (pairs.split("-")[0], pairs.split("-")[1]) \
                            for pairs in single_align ])

    return alignment


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("f_file", type=str)
    # parser.add_argument("e_file", type=str)
    # parser.add_argument("align", type=str)
    parser.add_argument("fe_file", type=str)
    parser.add_argument("ef_file", type=str)
    args = parser.parse_args()

    fe_phrases = get_giza_file_content(args.fe_file)
    ef_phrases = get_giza_file_content(args.ef_file)
    counter_phrase_pair = Counter()
    senid = 0
    for fe_phrase, ef_phrase in zip(fe_phrases, ef_phrases):
        print(senid)
        fe_alignment, ef_alignment = get_alignments(fe_phrase, ef_phrase)
        # 例如fe_alignment=(1, 2) 这里 2是f 1是e
        # 原来的由问题，source 和 target混淆了
        # alignment = do_alignment(fe_alignment, ef_alignment, len(fe_phrase[0]), len(ef_phrase[0]))
        alignment = do_alignment(fe_alignment, ef_alignment,
                                 len(ef_phrase[0]), len(fe_phrase[0]))
        # print(alignment)
        # import pdb; pdb.set_trace()
        
        # BP = phrase_extraction(ef_phrase[0], fe_phrase[0], alignment)  # fe_phrase[0] 是 e 句子
        # 修改错误
        BP, _ = phrase_extraction(fe_phrase[0],ef_phrase[0], alignment)    # fe_phrase[0] 是 e 句子
        counter_phrase_pair.update(BP)
        senid+=1

        # for (pl_phrase, pt_phrase) in BP:
        #     print(pl_phrase, "<=>", pt_phrase)
        # print("\n")
    # print(counter_phrase_pair.most_common(3))
    count_list = counter_phrase_pair.values()
    total_count = sum(count_list)  # total of all counts

    #
    phrase_list = list(counter_phrase_pair)
    prob_list = [count/float(total_count) for count in count_list]

    # phrase_prob = dict(counter_phrase_pair)
    # for ph in phrase_list:
    #     phrase_prob[ph] = phrase_prob[ph] / float(total_count)
    most_common_ph = counter_phrase_pair.most_common(3)
    print(total_count)

    for ph, cn in most_common_ph:
        print(cn)
        print(cn/float(total_count))
    phrase_dict = dict(zip(phrase_list,prob_list))
    # for item in phrase_dict.items():
    #    print(item)        
    with open('phrase_prob_list.pkl', 'wb') as f:
        pickle.dump(phrase_dict, f)

    # with codecs.open("phrase_table.txt", mode='w', encoding="utf-8") as f:
    #     for key in phrase_prob:
    #         f.write('%s |   %s  |   %f\n' % (key[0], key[1], phrase_prob[key]))

    with codecs.open("phrase_table.txt", mode='w', encoding="utf-8") as f:
        for i in range(len(phrase_list)):
            f.write('%s | %s | %f\n' % (phrase_list[i][0], phrase_list[i][1], prob_list[i]))
