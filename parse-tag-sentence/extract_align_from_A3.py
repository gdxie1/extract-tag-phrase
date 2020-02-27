# coding=utf-8
# chcp 65001
import argparse
import re
# import codecs

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type=str, required=True,)
    parser.add_argument("--output", type=str, required=True, )

    args = parser.parse_args()
    pattern = re.compile(r'\(\{ ([\d]+ )*\}\)')
    # pattern = re.compile(r'({ ([\d]+ )*})')
    # read input file
    file_input = open(args.input, mode='rt', encoding="utf-8")
    list_result = []
    while 1:
        line = file_input.readline()
        if not line:
            break;
        line = file_input.readline()
        line = file_input.readline()
        matches = pattern.finditer(line)
        wordStartPos = 0
        list_word_align = []
        for match in matches:
            # print(match)
            span = match.span()
            word = line[wordStartPos:span[0]-1]
            align_unit = line[span[0]:span[1]]
            align_unit = align_unit[2:-2]
            align_unit = align_unit.split()
            list_word_align.append((word, align_unit))
            wordStartPos = span[1]+1
        assert list_word_align[0][0] == 'NULL'
        list_word_align.pop(0)
        list_align_result = []
        for i, word_align_unit in enumerate(list_word_align):
            for tgt_pos in word_align_unit[1]:
                list_align_result.append('%d-%d' % (i, int(tgt_pos)-1))
        list_result.append(' '.join(list_align_result))

    file_result = open(args.output, mode='wt', encoding="utf-8")
    print(len(list_result))
    for line in list_result:
        file_result.write(line)
        file_result.write('\n')
    file_result.close()

