# coding=utf-8
import codecs
import argparse
from nltk.parse import CoreNLPParser
from nltk.tree import Tree

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("f_file", type=str)
    # parser.add_argument("e_file", type=str)
    # parser.add_argument("align", type=str)
    
    parser.add_argument("--input", type=str, required=True,)
    parser.add_argument("--output", type=str, required=True,)

    args = parser.parse_args()
    
    parser = CoreNLPParser(url='http://localhost:9001')
    print('parser generated!')
    exception_sen = []
    tree_list = []
    p_phrase_trees = None
    f_input = open(args.input, mode='rt', encoding='utf-8')

    f_output = codecs.open(args.output, mode='wt', encoding='utf-8')
    # f_output = open(args.output, 'wt')
    for senid, line in enumerate(f_input):
        if senid > 100:
            break
        try:
            p_parse_trees = list(parser.parse(parser.tokenize(line)))
        except ValueError:
            print('parsing fail')
            exception_sen.append(senid)
            p_parse_trees = [Tree.fromstring('(S (NULL ERROR))')]  # we simply give a dummy tree
        f_output.write('%d\n' % len(p_parse_trees))
        for sub_tree in p_parse_trees:
            f_output.write(str(sub_tree))
            f_output.write('\n|||\n')
        # str_tree = ' '.join(p_parse_trees)
        # f_output.write(str_tree)
        # f_output.write('\n')

        # tree_list.append(p_parse_trees)
    f_input.close()
    f_output.close()

    # with open(args.output, 'wb') as f:
    #     pickle.dump(tree_list, f)

    print('exception sen:%r' % exception_sen)
    with open('tagged_info.txt', mode='w', encoding="utf-8") as f:
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

