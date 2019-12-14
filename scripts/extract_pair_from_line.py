# coding=utf-8

import argparse
import re

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type=str, required=True,)
    parser.add_argument("--src_output", type=str, required=True, )
    parser.add_argument("--tgt_output", type=str, required=True, )

    args = parser.parse_args()
    #pattern = re.compile(r'(<[a-zA-Z]+) (\w+) ( > )')
    src_line = []
    tgt_line = []
    # read input file
    file_input = open(args.input, mode='rt', encoding="utf-8")
    list_result = []
    line_no = 0
    for line in file_input:
        line = line[:-1]  # remove the \n
        print(line_no)
        line_no += 1
        src_tgt = line.split('\t')
        src = src_tgt[0]
        tgt = src_tgt[1]
        if len(src) == 0 or len(tgt) == 0:
            print("empty line\n")
            continue
        if src[0] == '\"' and src[-1] == '\"':
            src = src[1:-1]
        if tgt[0] == '\"' and tgt[-1] == '\"':
            tgt = tgt[1:-1]

        if len(src) == 0 or len(tgt) == 0:
            print("empty line\n")
            continue
        # src_line.append(str(line_no)+'\t' + src)
        # tgt_line.append(str(line_no)+'\t' + tgt)
        src_line.append(src)
        tgt_line.append(tgt)

    file_src = open(args.src_output, mode='wt', encoding="utf-8")
    print(len(src_line))
    for line in src_line:
        file_src.write(line)
        file_src.write('\n')
    file_src.close()

    file_tgt = open(args.tgt_output, mode='wt', encoding="utf-8")
    print(len(tgt_line))
    for line in tgt_line:
        file_tgt.write(line)
        file_tgt.write('\n')
    file_tgt.close()
