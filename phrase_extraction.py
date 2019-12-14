# def phrase_extraction(f_sentence, e_sentence, alignment):
#     A = alignment
#     BP = []
#     for e_start in range(1, len(e_sentence) + 1):
#         for e_end in range(e_start, len(e_sentence) + 1):
#             f_start, f_end = len(f_sentence), 0
#             for (e, f) in A:
#                 e, f = int(e), int(f)
#                 if e_start <= e <= e_end:
#                     f_start = min(f, f_start)
#                     f_end = max(f, f_end)
#             extracted_phrases = extract(f_start, f_end, e_start, e_end,
#                                             f_sentence, e_sentence, A)
#             for phrase in extracted_phrases:
#                 BP.append(phrase)
#
#     return BP

def phrase_extraction(f_sentence, e_sentence, alignment):
    A = alignment
    BP = []
    BP_pos = []
    for e_start in range(1, len(e_sentence) + 1):
        for e_end in range(e_start, len(e_sentence) + 1):
            f_start, f_end = len(f_sentence), 0
            for (e, f) in A:
                e, f = int(e), int(f)
                if e_start <= e <= e_end:
                    f_start = min(f, f_start)
                    f_end = max(f, f_end)
            extracted_phrases, extracted_phrases_pos = extract(f_start, f_end, e_start, e_end,
                                            f_sentence, e_sentence, A)
            BP.extend(extracted_phrases)
            BP_pos.extend(extracted_phrases_pos)
            # for phrase in extracted_phrases:
            #     BP.append(phrase)

    return BP, BP_pos

def is_aligned(A, f_ind, sentence, e_start, e_end):
    f_align = []
    for (e, f) in A:
        e, f = int(e), int(f)
        if f == f_ind:
            f_align.append(e)
    if f_ind < 1 or f_ind > len(sentence):
        return False
    if len(f_align) > 0 and (min(f_align) < e_start or max(f_align) > e_end):
        return False
    return True

def extract(f_start, f_end, e_start, e_end, f_sentence, e_sentence, A):
    if f_end == 0:
        return [], []
    for (e, f) in A:
        e, f = int(e), int(f)
        if (e < e_start or e > e_end) and f_start <= f <= f_end:
            return [], []
    E = []
    E_pos = []

    f_s = f_start
    while True:
        f_e = f_end
        while True:
            e_phrase = " ".join(e_sentence[e_start-1 : e_end])
            f_phrase = " ".join(f_sentence[f_s-1 : f_e])
            E.append((e_phrase, f_phrase))
            E_pos.append(((e_start-1, e_end), (f_s-1, f_e)))
            f_e += 1
            if not is_aligned(A, f_e, f_sentence, e_start, e_end):
                break
        f_s -= 1
        if not is_aligned(A, f_s, f_sentence, e_start, e_end):
            break

    return E, E_pos
#
# def extract(f_start, f_end, e_start, e_end, f_sentence, e_sentence, A):
#     if f_end == 0:
#         return []
#     for (e, f) in A:
#         e, f = int(e), int(f)
#         if (e < e_start or e > e_end) and f_start <= f <= f_end:
#             return []
#     E = []
#
#     f_s = f_start
#     while True:
#         f_e = f_end
#         while True:
#             e_phrase = " ".join(e_sentence[e_start-1 : e_end])
#             f_phrase = " ".join(f_sentence[f_s-1 : f_e])
#             E.append((e_phrase, f_phrase))
#             f_e += 1
#             if not is_aligned(A, f_e, f_sentence, e_start, e_end):
#                 break
#         f_s -= 1
#         if not is_aligned(A, f_s, f_sentence, e_start, e_end):
#             break
#
#     return E