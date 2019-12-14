# coding=utf-8
# chcp 65001
"""
find the sentences containing prepositional phrase and output the line number
"""
import argparse
from nltk.tree import Tree


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
    
    parser.add_argument("--input", type=str, required=True, help="tree of parsed sentence")
    parser.add_argument("--output", type=str, required=True, help="line number of parsed sentence, start from 0 ")

    args = parser.parse_args()


    sen_tree_list = []
    p_phrase_trees = None
    sen_count = 0
    f_input = open(args.input, mode='rt', encoding='utf-8')
    f_output = open(args.output, mode='wt', encoding='utf-8')
    while 1:
        count_line = f_input.readline()
        if len(count_line) == 0:
            break
        print(sen_count)
        if sen_count == 335:
            a = 1
        count = int(count_line)
        # if count == 2:
        #     print(count)
        tree_list = []
        for i in range(count):
            tree_str = ''
            while 1:
                line = f_input.readline()
                if line == '|||\n' or len(line) == 0:
                    break
                tree_str += line
            tree_list.append(Tree.fromstring(tree_str))
    #     sen_tree_list.append(tree_list)
    # for sen_tree in sen_tree_list:
        phrase_tag = ['LC']
        p_phrase_dict = {"LC": []}

        for one_tree in tree_list:
            # print(one_tree)
            traverse(one_tree, p_phrase_dict, phrase_tag)
        if len(p_phrase_dict["LC"]):
            f_output.write('%d\n' % sen_count)
        sen_count += 1
    f_input.close()
    f_output.close()
