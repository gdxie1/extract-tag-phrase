# coding=utf-8
# chcp 65001
"""
add viterbi beam search method to extract phrases.
load  phrase probability generated in advance then apply beam search
the result show that this method is infeasible
"""
import pickle
import codecs
import argparse
from phrase_extraction import phrase_extraction
from alignment import get_alignments, do_alignment
import beam_search


def get_giza_file_content(file_name):
    file_content = get_data_from_file(file_name)
    return [(file_content[i + 1].split(), file_content[i + 2])
            for i in range(0, len(file_content) - 1, 3)]


def get_data_from_file(file_name):
    with codecs.open(file_name, encoding="utf-8") as file_:
        content = [line.lower().strip() for line in file_]
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
    return [sentence.split() for sentence in file_content]


def load_alignment(file_name):
    file_content = get_data_from_file(file_name)
    alignment = []
    for content_item in file_content:
        single_align = content_item.split()
        alignment.append([(pairs.split("-")[0], pairs.split("-")[1]) \
                          for pairs in single_align])

    return alignment


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("f_file", type=str)
    # parser.add_argument("e_file", type=str)
    # parser.add_argument("align", type=str)
    parser.add_argument("fe_file", type=str)
    parser.add_argument("ef_file", type=str)
    parser.add_argument("phrase_p", type=str)
    args = parser.parse_args()

    fe_phrases = get_giza_file_content(args.fe_file)
    ef_phrases = get_giza_file_content(args.ef_file)

    # with open('phrase_table/phrase_prob_list.pkl', 'rb') as f:
    with open(args.phrase_p, 'rb') as f:
        phrase_dict = pickle.load(f)

    # phrase_dict = {}
    # line_id = 0
    # with codecs.open(args.phrase_p, mode='r', encoding="utf-8") as f:
    #     for line in f:
    #         ph_f, ph_e, prob = line.split('|')
    #         phrase_dict[(ph_f, ph_e)] = float(prob)
    #         print(line_id)
    #         line_id += 1

    print('phrase table loaded')
    senid = 0
    phrase_result = []  # segment result
    for fe_phrase, ef_phrase in zip(fe_phrases, ef_phrases):
        print(senid)
        # stopline = 1899
        # if senid != stopline:
        #     continue
            # senid = stopline
        fe_alignment, ef_alignment = get_alignments(fe_phrase, ef_phrase)
        alignment = do_alignment(fe_alignment, ef_alignment,
                                 len(ef_phrase[0]), len(fe_phrase[0]))
        # fe_phrase = fe_phrases[id]
        # ef_phrase = ef_phrases[id]
        BP, BP_pos = phrase_extraction(fe_phrase[0], ef_phrase[0], alignment)  # fe_phrase[0] 是 e 句子

        # # find each e_start and its count
        # phrase_start_pos_counter = Counter()
        # for idx, ((e_start, e_end), (f_start, f_end)) in enumerate(BP_pos):
        #     phrase_start_pos_counter[e_start] += 1
        # e_start_list = phrase_start_pos_counter.items()
        # accumulated = 0
        # # in order to speed search, for a pos in sentence, build a dict to index the start-index and end-index in BP_pos
        e_start_dict = {}
        # for e_start, count in e_start_list:
        #     e_start_dict[e_start] = (accumulated, accumulated + count)
        #     accumulated += count
        for idx, ((e_start, e_end), (f_start, f_end)) in enumerate(BP_pos):
            e_pos_list = e_start_dict.get(e_start, [])
            e_pos_list.append(idx)
            e_start_dict[e_start] = e_pos_list

        phrase_seg = beam_search.search(fe_phrase[0], ef_phrase[0], BP, BP_pos, e_start_dict, phrase_dict)
        phrase_result.append(phrase_seg)
        senid+=1
    with codecs.open('phrase.en', 'w', encoding='utf-8') as f_e:
        with codecs.open('phrase.zh', 'w', encoding='utf-8') as f_f:
            for phrase_seg in phrase_result:  # each sentence
                f_seg = ''
                e_seg = ''
                for (ph_f, ph_e), _ in phrase_seg:  # each sentence's phrase list
                    f_seg += ph_f
                    f_seg += ' | '
                    e_seg += ph_e
                    e_seg += ' | '
                f_e.write(e_seg)
                f_e.write('\n')
                f_f.write(f_seg)
                f_f.write('\n')
    with open('phrase.dat', 'wb') as f:
        pickle.dump(phrase_result, f)

