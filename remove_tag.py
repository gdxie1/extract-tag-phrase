# coding=utf-8
# chcp 65001
# import csv
import pickle
import random
import argparse
import re
from alignment import get_alignments, do_alignment

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type=str, required=True,)
    parser.add_argument("--output", type=str, required=True, )

    args = parser.parse_args()

    # read input file
    file_input = open(args.input, mode='rt', encoding="utf-8")
    list_result = []
    for line in file_input:
        search_result = re.search(r'(<[a-zA-Z]+) (.*) (> )', line)
        new_line = re.sub(r'(<[a-zA-Z]+) (.*) (> )', r'\2', line)
        print(new_line)
        list_result.append(new_line)
    file_e = open(args.output, mode='wt', encoding="utf-8")
    print(len(list_result))
    for line in list_result:
        file_e.write(line)
        # file_e.write('\n')
    file_e.close()

