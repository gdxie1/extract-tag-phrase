# coding=utf-8
# chcp 65001
# import csv
import pickle
import random
import argparse
import re
from alignment import get_alignments, do_alignment

def get_data_from_file(file_name):
    with open(file_name, encoding="utf-8", newline='\n') as file_:
        content = []
        for line in file_:
            # content.append(line.replace(chr(0x1E), '').lower().strip())
            content.append(line.replace('\x1e', '').strip())

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

    parser.add_argument("--ori_sgm", type=str)
    parser.add_argument("--output", type=str)



    # fe_phrases = get_giza_file_content(args.fe_file)
    # ef_phrases = get_giza_file_content(args.ef_file)

    parser.add_argument("--tagged_refs", type=str, nargs="+",
                        help="tagged plain references")
    parser.add_argument("--line_id", type=str, nargs="+",
                        help="tagged refs's line id in sgm file")

    args = parser.parse_args()
    senid = 0


    if len(args.tagged_refs) != len(args.line_id):
        print("refs file number must equal line id file number")
        exit(-1)


    # read sgm file

    file_sgm = open(args.ori_sgm, mode='rt', encoding="utf-8")
    file_sgm_list = []
    for line in file_sgm:
        file_sgm_list.append(line)
    for ref, line_id in zip(args.tagged_refs, args.line_id):
        ref_file = open(ref, mode='rt', encoding='utf-8')
        line_id_file = open(line_id,  mode='rt', encoding='utf-8')
        for l_id, line_text in zip(line_id_file, ref_file):
            ori_text = file_sgm_list[l_id]
            new_text = re.sub(r'<seg id="[0-9]+"> (.*)</seg>', ori_text, line_text)
            print(new_text)
            file_sgm_list[l_id] = new_text
        ref_file.close()
        line_id_file.close()

    file_e = open(args.output, mode='wt', encoding="utf-8")
    for line in file_sgm_list:
        file_e.write(line)
        file_e.write('\n')
    file_e.close()

