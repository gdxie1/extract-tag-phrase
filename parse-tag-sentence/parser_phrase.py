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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("f_file", type=str)

    args = parser.parse_args()
    
    parser = CoreNLPParser(url='http://localhost:9001')
    print('parser generated!')

    file_f = codecs.open(args.f_file, encoding="utf-8")
    for f_sen in file_f:
        try:
            p_parse_trees = list(parser.parse(parser.tokenize(f_sen)))
        except ValueError:
            print('error line')
            continue
        print(p_parse_trees[0])
