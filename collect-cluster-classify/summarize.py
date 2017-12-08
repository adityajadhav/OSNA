"""
sumarize.py
"""
import os

files_to_sumarize  = ['cluster_result.txt','classify_result.txt']

def sumarize(file_path):
    result = read_results(file_path)
    with open('summary.txt', 'a') as f:
        for line in result:
            f.write(line)

def read_results(file_path):
    lines = list()
    with open(file_path, 'r') as f:
        for line in f:
            if len(line) > 0:
                lines.append(line)
    return lines

def main():
    for file_path in files_to_sumarize:
        sumarize(file_path)

if __name__ == '__main__':
    main()