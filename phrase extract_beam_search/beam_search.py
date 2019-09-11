# coding=utf-
"""
a beam search approach using the phrase probability to search an optimistic phrase paris sequences for each
sentence pair
This method is infeasible
"""
from sortedcontainers import SortedListWithKey
import math
class Hypothesis:
    """A (partial) hypothesis

    Args:

        token (unicode): the surface form of this hypothesis
        score (float): the score of this hypothesis (higher is better)
        coverage (list of lists): a representation of the area of the constraints covered by this hypothesis
        constraints (list of lists): the constraints that may be used with this hypothesis
        payload (:obj:): additional data that comes with this hypothesis. Functions may
            require certain data to be present in the payload, such as the previous states, glimpses, etc...
        backpointer (:obj:`ConstraintHypothesis`): a pointer to the hypothesis object which generated this one
        constraint_index (tuple): if this hyp is part of a constraint, the index into `self.constraints` which
            is covered by this hyp `(constraint_idx, token_idx)`
        unfinished_constraint (bool): a flag which indicates whether this hyp is inside an unfinished constraint

    """
    # def __init__(self, alignment, phrase, phrase_pos, phrase_score,
    #              start_e, sen_f, sen_e, index_word_dict_e, backpointer=None):
    #     self.alignment = alignment
    #     self.phrase = phrase
    #     self.phrase_pos = phrase_pos
    #     self.score = phrase_score
    #     self.start_e = start_e
    #     self.sen_f = sen_f
    #     self.sen_e = sen_e
    #     self.index_word_dict_e = index_word_dict_e
    #     self.backpointer = backpointer
    # def __init__(self, phrase, phrase_pos, score, e_start, sen_e, sen_f, BP, BP_pos, e_start_dict,
    #              phrase_dict, backpointer=None):
    def __init__(self, phrase, phrase_pos, score, sen_e, sen_f, e_start_dict,
                 backpointer=None):
        self.phrase = phrase
        self.phrase_pos = phrase_pos
        self.sen_f = sen_f
        self.sen_e = sen_e
        self.e_start_dict = e_start_dict
        self.backpointer = backpointer
        if backpointer:
            self.ori_score_list = backpointer.ori_score_list + [score]  # you can't use append as append will return a null
            self.phrase_count = backpointer.phrase_count+1
            # normalized the score with length of the hyp
            self.score = (backpointer.phrase_count*backpointer.score+score)/self.phrase_count
        else:
            self.ori_score_list = [0]
            self.phrase_count = 0
            self.score = 0
        # self.phrase_dict = phrase_dict
        # self.BP = BP
        # self.BP_pos = BP_pos

    def __str__(self):
        return u'phrase: {}, phrase_pos: {}, sequence: {}, score: {}'.format(
            self.phrase, self.e_start, self.sequence, self.score)

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def sequence(self):
        sequence = []
        current_hyp = self
        while current_hyp.backpointer is not None:
            # as some word may be omitted, so we need to keep the phrase's position information to embed the tags
            sequence.append((current_hyp.phrase, current_hyp.phrase_pos))
            current_hyp = current_hyp.backpointer
        sequence.append(current_hyp.phrase)
        return sequence[::-1]


class Beam(object):

    def __init__(self, size, lower_better=True):
        # are bigger scores better or worse?
        if lower_better:
            self.hypotheses = SortedListWithKey(key=lambda x: x['score'])
        else:
            self.hypotheses = SortedListWithKey(key=lambda x: -x['score'])

        self.size = size

    def add(self, hyp):
        self.hypotheses.add(hyp)
        if len(self.hypotheses) > self.size:
            assert len(self.hypotheses) == self.size + 1
            del self.hypotheses[-1]

    def __len__(self):
        return len(self.hypotheses)

    def __iter__(self):
        for hyp in self.hypotheses:
            yield hyp
def search(sen_e, sen_f, BP, BP_pos, e_start_dict, phrase_dict):
    beam_size = 10
    f_len = len(sen_f)
    start_hyp = Hypothesis(None, ((0, 0), (0, 0)), 0, sen_e, sen_f, e_start_dict)
    stopped_hyp = []  # store all the stopped hyp
    e_start = 0
    started_beam = Beam(beam_size)
    stopped_beam = Beam(beam_size)
    started_beam.add(start_hyp)
    last_beam = started_beam
    # while 1:
    for i in range(1000):
        # print('beam %d' % i)
        new_beam = Beam(beam_size)
        for j, last_hyp in enumerate(last_beam):
            # print('last hyp %d' % j)
            # if i ==3 and j==1:
            #     i = 3
            last_score = last_hyp.score
            new_start = last_hyp.phrase_pos[0][1]

            # here we should avoid the key error; try to
            while 1:
                # 在某条路径上， 有些词可能被跳过去，需要往后查找
                if e_start_dict.get(new_start, None): # if can find the start phrase list at that position
                    break
                else:
                    new_start += 1  # try to find on next position
                    if new_start >= f_len:  # if reached end of the sentence
                        break
                    continue
            if new_start >= f_len:  # if reached end of the sentence
                stopped_beam.add(last_hyp)
                continue

            for id in e_start_dict[new_start]:  # index in the phrase table
                phrase_ef = BP[id]
                score = -math.log(phrase_dict.get(phrase_ef, 0.000000001))
                new_hyp = Hypothesis(phrase_ef, BP_pos[id], score, sen_e, sen_f, e_start_dict, backpointer=last_hyp)
                new_beam.add(new_hyp)
        if not len(new_beam):  # no any hyp can be created
            break
        last_beam = new_beam
    if not stopped_beam:
        return [(u'unk', u'unk')]
    return stopped_beam.hypotheses[0].sequence[1:]  # 开始的 None 去掉
