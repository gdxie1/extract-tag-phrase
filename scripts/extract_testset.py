# coding=utf-8

import argparse
import random

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--src", type=str, required=True,)
    parser.add_argument("--tgt", type=str, required=True,)
    parser.add_argument("--num", type=int, required=True, help="the number of the test sentences")


    args = parser.parse_args()
    src_line = []
    tgt_line = []
    # read input file
    file_src = open(args.src, mode='rt', encoding="utf-8")
    for line in file_src:
        src_line.append(line)

    file_tgt = open(args.tgt, mode='rt', encoding="utf-8")
    for line in file_tgt:
        tgt_line.append(line)
    data_size = len(src_line)
    assert data_size == len(tgt_line)

    file_src.close()
    file_tgt.close()


    # sample_index = random.sample(range(0, data_size), 2000)

    test_line = []
    dev_line = []
    for i in range(args.num):
        line_no = random.randint(0, len(src_line))
        test_line.append((src_line.pop(line_no), tgt_line.pop(line_no)))
        print(len(src_line))

    for i in range(args.num):
        line_no = random.randint(0, len(src_line))
        dev_line.append((src_line.pop(line_no), tgt_line.pop(line_no)))

    assert len(src_line) == len(tgt_line)

    # output the training files
    file_src = open(args.src+"_new", mode='wt', encoding="utf-8")
    file_tgt = open(args.tgt+"_new", mode='wt', encoding="utf-8")

    for line in src_line:
        file_src.write(line)
    for line in tgt_line:
        file_tgt.write(line)

    file_src.close()
    file_tgt.close()

    # output the test files
    file_src = open("test.en", mode='wt', encoding="utf-8")
    file_tgt = open("test.ru", mode='wt', encoding="utf-8")

    for line in test_line:
        file_src.write(line[0])
        file_tgt.write(line[1])

    file_src.close()
    file_tgt.close()

    # output the dev files
    file_src = open("dev.en", mode='wt', encoding="utf-8")
    file_tgt = open("dev.ru", mode='wt', encoding="utf-8")

    for line in dev_line:
        file_src.write(line[0])
        file_tgt.write(line[1])

    file_src.close()
    file_tgt.close()

