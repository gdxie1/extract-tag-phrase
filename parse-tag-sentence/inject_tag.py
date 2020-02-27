# coding=utf-8
import argparse
import re
# import codecs

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--result_with_align", type=str, required=True)
    parser.add_argument("--source_with_tag", type=str, required=True)
    parser.add_argument("--output", type=str, required=True, )


#    phrase_tag = ['NP', 'VP','ADJP', 'ADVP', 'CLP',  'CP',
#                  'DNP', 'DP', 'DVP', 'FRAG', 'IP', 'LCP',
#                  'LST', 'PP', 'PRN', 'QP', 'UCP',]
    args = parser.parse_args()
    # read input file

    file_result = open(args.result_with_align, mode='rt', encoding='utf-8')
    file_tag = open(args.source_with_tag, mode='rt', encoding='utf-8')
    line = file_result.readline()
    list_result = []
    while 1:
        if line[:2]=='S-':
            break
        line = file_result.readline()
    lineNO=0
    while line:
        lineS = line
        lineH = file_result.readline()
        # process the translation result
        list_tgt_word = lineH.split()
        list_tgt_word = list_tgt_word[2:]

        lineP = file_result.readline()
        # alignment info
        lineA = file_result.readline()
        list_A_unit = lineA.split()[1:]
        dict_A_src_tgt = {}
        for Au in list_A_unit:
            srcPos, tgtPos = Au.split('-')
            tgtPos = int(tgtPos)
            srcPos = int(srcPos)
            list_tgtPos = dict_A_src_tgt.get(srcPos, [])
            list_tgtPos.append(tgtPos) # one source pos may have multi
            dict_A_src_tgt[srcPos] = list_tgtPos
        line = file_result.readline()
        # read the tagged source
        line_tag = file_tag.readline()
        list_word_tag = line_tag.split()
        if lineNO == 22:
            lineNO = 22
        print(lineNO)
        lineNO += 1

        # find tag and its index
        tag_dict = {}
        list_word = []
        for word in list_word_tag:
            if word[0] != '<' or word == '<unk>' or len(word)<3:
                list_word.append(word)
                continue
            # when <NP> xxx </NP>, then two tags will attach to the same word, so need a list
            if word[0:2] == '</':
                assert len(list_word)>0  # the tag at the beginning of the sentence can't be </xxx>
                tag_info_list = tag_dict.get(len(list_word)-1, [])
                tag_info_list.append((1, word))
                tag_dict[len(list_word)-1] = tag_info_list  # here 1 indicate the right part of the tag
            else:
                tag_info_list = tag_dict.get(len(list_word), [])
                tag_info_list.append((0, word))
                tag_dict[len(list_word)] = tag_info_list
        # start inject the tag to target
        for srcPos, tag_info_list in tag_dict.items():
            for tag_info in tag_info_list:
                tgtPos_list = dict_A_src_tgt.get(srcPos)

                # make sure there is position
                if not tgtPos_list:
                    srcPos_bias = srcPos
                    while not tgtPos_list:
                        srcPos_bias -= 1
                        if srcPos_bias < 0:
                            break
                        tgtPos_tag = dict_A_src_tgt.get(srcPos_bias)
                    srcPos_bias = srcPos
                    while not tgtPos_list:
                        srcPos_bias += 1
                        if srcPos_bias >= len(list_word):
                            break
                        tgtPos_list = dict_A_src_tgt.get(srcPos_bias)

                if not tgtPos_list:
                    continue
                tgtPos = tgtPos_list[-1]

                if tgtPos:
                    if tag_info[0]:
                        list_tgt_word[tgtPos] += (' '+tag_info[1])
                    else:
                        list_tgt_word[tgtPos] = (tag_info[1]+' '+list_tgt_word[tgtPos])
                else:
                    print('can not find corresponding target position for source position of %d' % srcPos)
        list_result.append(' '.join(list_tgt_word))

    file_output = open(args.output, mode='wt', encoding="utf-8")
    print(len(list_result))
    for line in list_result:
        file_output.write(line)
        file_output.write('\n')
    file_output.close()

