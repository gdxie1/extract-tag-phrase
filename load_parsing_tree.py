# coding=utf-8
# chcp 65001
# import csv
import pickle
import argparse
from collections import Counter
from nltk.tree import Tree

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("f_file", type=str)
    # parser.add_argument("e_file", type=str)
    # parser.add_argument("align", type=str)
    
    parser.add_argument("--input", type=str, required=True,)
    parser.add_argument("--output", type=str, required=True,)

    args = parser.parse_args()
    
    sen_tree_list = []
    p_phrase_trees = None
    sen_count = 0
    f_input = open(args.input, mode='r', encoding='utf-8')
    f_output = open(args.output, mode='w', encoding='utf-8')
    while 1:
        count_line = f_input.readline()
        if len(count_line) == 0:
            break
        sen_count += 1
        print(sen_count)
        count = int(count_line)
        # if count == 2:
        #     print(count)
        tree_list = []
        for i in range(count):
            tree_str = ''
            while 1:
                line = f_input.readline()
                if line == '|||\n':
                    break
                tree_str += line
            tree_list.append(Tree.fromstring(tree_str))
    #     sen_tree_list.append(tree_list)
    # for sen_tree in sen_tree_list:
        for sub_tree in tree_list:
            # print(sub_tree)
            f_output.write(str(sub_tree))
            f_output.write('\n|||\n')
        # str_tree = ' '.join(p_parse_trees)
        # f_output.write(str_tree)
        # f_output.write('\n')

        # tree_list.append(p_parse_trees)
    f_input.close()
    f_output.close()
