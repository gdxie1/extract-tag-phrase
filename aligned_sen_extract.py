# coding=utf-8
# chcp 65001
# import csv
"""
extract sentences form giza++'s *.A3.final file
This file is used to verify the aligned result if all the sentences are aligned
"""

import argparse

from alignment import get_alignments


def get_giza_file_content(file_name):
    file_content = get_data_from_file(file_name)
    return [(file_content[i + 1].split(), file_content[i + 2])
            for i in range(0, len(file_content) - 1, 3)]


def get_data_from_file(file_name):
    with open(file_name, encoding="utf-8", newline='\n') as file_:
        content = []
        for line in file_:
            # content.append(line.replace(chr(0x1E), '').lower().strip())
            content.append(line.replace('\x1e', '').strip())

    # content = [line.lower().strip() for line in file_]
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("fe_file", type=str)
    parser.add_argument("ef_file", type=str)

    parser.add_argument("f_output", type=str)
    parser.add_argument("e_output", type=str)

    parser.add_argument('--start_line', type=int, required=False, default=0)
    parser.add_argument('--end_line', type=int, required=False,  default=-1)  # -1 represents ends

    args = parser.parse_args()
    
    fe_phrases = get_giza_file_content(args.fe_file)
    ef_phrases = get_giza_file_content(args.ef_file)


    senid = 0

    file_f = open(args.f_output, mode='w', encoding="utf-8")
    file_e = open(args.e_output, mode='w', encoding="utf-8")
    for fe_phrase, ef_phrase in zip(fe_phrases, ef_phrases):
        print(senid)
        senid += 1
        # stopline = 1899
        # if senid != stopline:
        #     continue
            # senid = stopline
        fe_alignment, ef_alignment = get_alignments(fe_phrase, ef_phrase)
        # fe_phrase[0] 是 e 句子
        f_sen = ' '.join(ef_phrase[0])
        e_sen = ' '.join(fe_phrase[0])
        file_f.write(f_sen)
        file_f.write('\n')
        file_e.write(e_sen)
        file_e.write('\n')
    file_f.close()
    file_e.close()
