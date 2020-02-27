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
    #pattern = re.compile(r'(<[a-zA-Z]+) (\w+) ( > )')
    # read input file
    file_input = open(args.input, mode='rt', encoding="utf-8")
    list_result = []
    for line in file_input:
        # print(line[:-1])
        # it = re.finditer(r'(<[a-zA-Z]+ )([^>]+)( >)', line)
        # for match in it:
        #     print(match.group())
        new_line = re.sub(r'(<[a-zA-Z]+> )([^>]+)( </[a-zA-Z]+>)', r'\2', line)
        # print(new_line)
        list_result.append(new_line)
    file_e = open(args.output, mode='wt', encoding="utf-8")
    print(len(list_result))
    for line in list_result:
        file_e.write(line)
        # file_e.write('\n')
    file_e.close()

