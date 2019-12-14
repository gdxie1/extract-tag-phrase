# coding=utf-8
"""
some functions that help use the giza++'s *A3.final to extract phrase
"""
import re
from collections import defaultdict

def get_phrase_split(phrase):
    phrase_splitted = re.split("(\S+ \(\{[0-9 ]*\}\))", phrase)
    phrase_splitted = [ item.strip() for item in phrase_splitted \
                        if item != " " and item != "" ]
    # phrase_splitted = [ re.match(r"(\S+) (\(\{[0-9 ]*\}\))", item) \
    #                       .group(1, 2) for item in phrase_splitted ]

    new_list = []
    for i, item in enumerate(phrase_splitted):
        # print(i)
        # print(item)
        tt = re.match(r"(\S+) (\(\{[0-9 ]*\}\))", item).group(1, 2)
        new_list.append(tt)
    phrase_splitted = new_list

    phrase_splitted = [ (item[0], int(s)) for item in phrase_splitted \
                        for s in item[1].strip("{()}").split() ]
    return phrase_splitted

def get_alignments(fe_phrase, ef_phrase):
    fe_phrase_splitted = get_phrase_split(fe_phrase[1])
    fe_alignment = []
    for x, y in fe_phrase_splitted:
        if x == u'null' or x == u'NULL':  # 忽略 null
            continue
        fe_alignment.append((y, ef_phrase[0].index(x)+1))
        #fe_alignment = [(y, ef_phrase[0].index(x) + 1) for (x, y) in fe_phrase_splitted]

    ef_alignment = []
    ef_phrase_splitted = get_phrase_split(ef_phrase[1])
    for x, y in ef_phrase_splitted:
        if x == 'null'or x == 'Null' or x == 'NULL':  # 忽略 null
            continue
        ef_alignment.append((y, fe_phrase[0].index(x) + 1))
        #ef_alignment = [(y, fe_phrase[0].index(x) + 1) for (x, y) in ef_phrase_splitted]



    # fe_phrase_splitted = get_phrase_split(fe_phrase[1])
    # fe_alignment = [ (y, ef_phrase[0].index(x)+1) for (x, y) in  fe_phrase_splitted ]
    #
    # ef_phrase_splitted = get_phrase_split(ef_phrase[1])
    #ef_alignment = [ (y, fe_phrase[0].index(x)+1) for (x, y) in  ef_phrase_splitted ]

    return fe_alignment, ef_alignment

def grow_diag(alignment, fe_len, ef_len, aligned, union):
    neighbours = [ (-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1,1), (1,-1), (1,1) ]  # up down left right up-left up-right ...
    prev_len = len(alignment) - 1
    # aligned 中存储的是 intersected 位置
    # repeat until new points appear
    #while prev_len < len(alignment):
    flag = True
    while flag:
        flag = False  # 如果添加了新的点，则flag会设置为True，需要重新扫描一遍，否则就退出循环
        for f in range(1, fe_len+1):
            for e in range(1, ef_len+1):
                if (f, e) in alignment: # 每一个交叉点
                    for neighbour in neighbours:  #
                        neighbour = tuple(i + j for i, j in zip((f, e), neighbour))
                        f_new, e_new = neighbour
                        #if (e_new not in aligned and f_new not in aligned) \  # 原来的，可能有错误
                        if (e_new not in aligned['e'] and f_new not in aligned['f']) \
                        and neighbour in union:
                            alignment.add(neighbour)
                            aligned['e'].add(e_new)
                            aligned['f'].add(f_new)
                            #prev_len += 1
                            flag = True

    return alignment

def final_and(alignment, fe_len, ef_len, aligned, init_align):
     # Add those points are not included in intersection 
     # after checking if can be added

    # import pdb; pdb.set_trace()
    for f_new in range(1, fe_len+1):
        for e_new in range(1, ef_len+1):
            if (e_new not in aligned and f_new not in aligned
                and (f_new, e_new) in init_align):
                alignment.add((f_new, e_new))
                aligned['e'].add(e_new)
                aligned['f'].add(f_new)


def do_alignment(fe_align, ef_align, fe_sent_len, ef_sent_len):
    # fe_align格式开始是反转的，先都转换为 f--e 的格式
    fe_align = [ tuple(reversed(x)) for x in fe_align ]
    alignment = set(ef_align).intersection(set(fe_align))  # will become (2-1) f-e
    union = set(ef_align).union(set(fe_align))

    aligned = defaultdict(set)
    for i, j in alignment:
        aligned['f'].add(i)  # f
        aligned['e'].add(j)  # e

    alignment = grow_diag(alignment, fe_sent_len, ef_sent_len, aligned, union)
    final_and(alignment, fe_sent_len, ef_sent_len, aligned, fe_align)
    final_and(alignment, fe_sent_len, ef_sent_len, aligned, ef_align)

    return sorted(alignment, key=lambda item: item)
