# coding=utf-8
# chcp 65001
"""
This is the original script to extract phrase from *.A3.final
https://github.com/maciejbiesek/smt-phrase-extraction
"""
import codecs
import argparse
from phrase_extraction import phrase_extraction
from alignment import get_alignments, do_alignment

def get_giza_file_content(file_name):
    file_content = get_data_from_file(file_name)
    return [(file_content[i+1].split(), file_content[i+2])
            for i in range(0, len(file_content), 3)]

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

    for fe_phrase, ef_phrase in zip(fe_phrases, ef_phrases):
        fe_alignment, ef_alignment = get_alignments(fe_phrase, ef_phrase)
        # 例如fe_alignment=(1, 2) 这里 2是f 1是e
        # 原来的由问题，source 和traget混淆了
        # alignment = do_alignment(fe_alignment, ef_alignment,
                                 # len(fe_phrase[0]), len(ef_phrase[0]))
        alignment = do_alignment(fe_alignment, ef_alignment,
                                 len(ef_phrase[0]), len(fe_phrase[0]))
        print(alignment)
        # import pdb; pdb.set_trace()
        
        BP = phrase_extraction(ef_phrase[0], fe_phrase[0], alignment)  # fe_phrase[0] 是 e 句子
        # 修改错误
        #BP = phrase_extraction(ef_phrase[0],fe_phrase[0], alignment)

        for (pl_phrase, pt_phrase) in BP:
            print(pl_phrase, "<=>", pt_phrase)
        print("\n")
