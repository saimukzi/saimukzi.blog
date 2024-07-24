import os

def find_file(dir):
    file_list = []
    for root, _, files in os.walk(dir):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list
