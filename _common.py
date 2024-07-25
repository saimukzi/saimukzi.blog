import hashlib
import os

def find_file(dir):
    file_list = []
    for root, _, files in os.walk(dir):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def read_file(fn, encoding='utf-8'):
    with open(fn, 'rt', encoding=encoding) as fin:
        ret = fin.readlines()
    ret = [i.strip('\n') for i in ret]
    return ret

def md5(text):
    return hashlib.md5(text.encode(encoding='utf-8')).hexdigest()
