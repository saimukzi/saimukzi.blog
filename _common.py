import hashlib
import os
import pathlib

from urllib.parse import urljoin as _urljoin

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

def md5_file(fn):
    with open(fn, 'rb') as fin:
        data = fin.read()
    return hashlib.md5(data).hexdigest()

def is_file_equal(fn1, fn2):
    with open(fn1, 'rb') as fin:
        data1 = fin.read()
    with open(fn2, 'rb') as fin:
        data2 = fin.read()
    return data1 == data2

def to_native_path(path):
    return str(pathlib.PurePath(path))

def to_rel_url(path):
    parts = pathlib.PurePath(path).parts
    return '/'.join(parts)

def native_path_to_posix(npath):
    npath = os.path.abspath(npath)
    return pathlib.Path(npath).as_posix()

def urljoin(*args):
    ret = args[0]
    for i in args[1:]:
        if not ret.endswith('/'):
            ret += '/'
        ret = _urljoin(ret, i)
    return ret
