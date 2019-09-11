# coding=utf-8
# chcp 65001
"""
add viterbi beam search method to extract phrases.
first calculate the phrase probability then apply beam search
the result show that this method is infeasible
"""
import pickle
import codecs
import argparse
from collections import Counter
from phrase_extraction import phrase_extraction
from alignment import get_alignments, do_alignment
import beam_search
def get_giza_file_content(file_name):
    file_content = get_data_from_file(file_name)
    return [(file_content[i+1].split(), file_content[i+2])
            for i in range(0, len(file_content)-1, 3)]

def get_data_from_file(file_name):
    with codecs.open(file_name, encoding="utf-8") as file_:
        content = [ line.lower().strip() for line in file_ ]
    # avoid to be segmented with the Record Seperator
    # content = []
    # with codecs.open(file_name, encoding="utf-8") as file_:
    #     for i, line in enumerate(file_):
    #         new_line = line.lower().strip()
    #         if i % 3 == 0 and new_line[0] == u'#': #every three lines there will be the # line
    #             content.append(new_line)
    #         else:
    #             content[i - 1] += new_line
    return content

def load_sentences(file_name):
    file_content = get_data_from_file(file_name)
    return [ sentence.split() for sentence in file_content ]

def load_alignment(file_name):
    file_content = get_data_from_file(file_name)
    alignment = []
    for content_item in file_content:
        single_align = content_item.split()
        alignment.append([ (pairs.split("-")[0], pairs.split("-")[1]) \
                            for pairs in single_align ])

    return alignment

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("f_file", type=str)
    # parser.add_argument("e_file", type=str)
    # parser.add_argument("align", type=str)
    parser.add_argument("fe_file", type=str)
    parser.add_argument("ef_file", type=str)
    args = parser.parse_args()

    fe_phrases = get_giza_file_content(args.fe_file)
    ef_phrases = get_giza_file_content(args.ef_file)
    counter_phrase_pair = Counter()
    alignment_list = []
    senid=0
    for fe_phrase, ef_phrase in zip(fe_phrases, ef_phrases):
        # print(senid)
        # if senid==2:
        #     senid =2
        fe_alignment, ef_alignment = get_alignments(fe_phrase, ef_phrase)
        # 例如fe_alignment=(1, 2) 这里 2是f 1是e
        # 原来的由问题，source 和traget混淆了
        # alignment = do_alignment(fe_alignment, ef_alignment,
                                 # len(fe_phrase[0]), len(ef_phrase[0]))
        alignment = do_alignment(fe_alignment, ef_alignment,
                                 len(ef_phrase[0]), len(fe_phrase[0]))

        alignment_list.append(alignment)

        # import pdb; pdb.set_trace()

        #BP = phrase_extraction(ef_phrase[0], fe_phrase[0], alignment)  # fe_phrase[0] 是 e 句子
        # 修改错误
        BP, BP_pos = phrase_extraction(fe_phrase[0],ef_phrase[0], alignment)    # fe_phrase[0] 是 e 句子
        counter_phrase_pair.update(BP)
        senid += 1
        ##############################
        # output the phrase table
        for ix, (pl_phrase, pt_phrase) in enumerate(BP):
            print('%s <=> %s' % (pl_phrase,pt_phrase))
            print(BP_pos[ix])
        print('\n')
        ###############################
    count_list = counter_phrase_pair.values()
    total_count = sum(count_list)  # total of all counts

    phrase_list = list(counter_phrase_pair)
    prob_list = [count/float(total_count) for count in count_list]

    # most_common_ph = counter_phrase_pair.most_common(3)
    # print(total_count)


    phrase_dict = dict(zip(phrase_list, prob_list))
    # print(phrase_dict[(u'政府 官员'), (u'government officials')])
    # print(phrase_dict[(u'玻利维亚'), (u'bolivia')])
    # phrase_dict[(u'玻利维亚'), (u'bolivia')] = 0.9
    phrase_result = []  # segment result
    for id, align in enumerate(alignment_list):
        print(id)
        if id == 1:
            id = 1
        fe_phrase = fe_phrases[id]
        ef_phrase = ef_phrases[id]
        BP, BP_pos = phrase_extraction(fe_phrase[0],ef_phrase[0], align)    # fe_phrase[0] 是 e 句子

        # find each e_start and its count
        phrase_start_pos_counter = Counter()
        for idx, ((e_start, e_end), (f_start, f_end)) in enumerate(BP_pos):
            phrase_start_pos_counter[e_start] += 1
        e_start_list = phrase_start_pos_counter.items()
        accumulated = 0
        # in order to speed search, for a pos in sentence, build a dict to index the start-index and end-index in BP_pos
        # in order to speed search, for a pos in sentence, build a dict to index the start-index and end-index in BP_pos
        e_start_dict = {}
        for e_start, count in e_start_list:
            e_start_dict[e_start] = (accumulated, accumulated+count)
            accumulated += count
        #                                        necessory information to continue the search
        #  phrase, score, e_start, sen_e, sen_f, BP, BP_pos, e_start_dict, phrase_dict, backpointer = None
        #start_hyp = beam_search.Hypothesis(None, None, -1, BP, BP_pos, e_start_dict, phrase_dict, backpointer=None)
        phrase_seg = beam_search.search(fe_phrase[0], ef_phrase[0], BP, BP_pos, e_start_dict, phrase_dict)
        phrase_result.append(phrase_seg)
    with codecs.open('phrase.en', 'w', encoding='utf-8') as f_e:
        with codecs.open('phrase.zh', 'w', encoding='utf-8') as f_f:
            for phrase_seg in phrase_result:
                f_seg=''
                e_seg=''
                for ph_f, ph_e in phrase_seg:
                    f_seg += ph_f
                    f_seg += ' | '
                    e_seg += ph_e
                    e_seg += ' | '
                f_e.write(e_seg)
                f_e.write('\n')
                f_f.write(f_seg)
                f_f.write('\n')

    # with open('phrase.dat', 'wb') as f:
    #     pickle.dump(phrase_result, f, protocol=pickle.HIGHEST_PROTOCOL)


    with open('phrase_prob_list.pkl', 'wb') as f:
        pickle.dump(phrase_dict, f)

    # with codecs.open("phrase_table.txt", mode='w', encoding="utf-8") as f:
    #     for key in phrase_prob:
    #         f.write('%s |   %s  |   %f\n' % (key[0], key[1], phrase_prob[key]))

    with codecs.open("phrase_table.txt", mode='w', encoding="utf-8") as f:
        for i in range(len(phrase_list)):
            f.write('%r | %f\n' % (phrase_list[i], prob_list[i]))
