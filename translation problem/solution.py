__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"

"""
    accurate in terms of handling all occurences, casing and special characters
"""

from re import split
from time import perf_counter
import os
import psutil


def get_columns(filename):
    """
        read a csv file and yield column contents
        returns a generator
    """

    with open(filename, encoding="utf-8") as csv_file:
        for line in csv_file.readlines():
            # skip empty lines
            if line == "\n":
                continue
            # remove the newline character
            line = line.strip("\n")
            # get the columns
            yield line.split(",")


def handle_case(word: str, rep_str: str):
    """
        test case and format rep_str to match word's case and return it
        returns a str
    """

    if word.istitle():
        # make the replace string title
        return rep_str.title()
    elif word.isupper():
        return rep_str.upper()
    else:
        return rep_str


start = perf_counter()
input_file = open("t8.shakespeare.txt", encoding="utf-8")
output_file = open("output.txt", "a", encoding="utf-8")
results_file = open("words-frequency.csv", "a", encoding="utf-8")
find_words_file = open("find_words.txt", encoding="utf-8")

# create an english-french pair
english_french_words = {columns[0]: columns[1]
                        for columns in get_columns("french_dictionary.csv")}
# initialize the word frequency to zero
word_frequency = {line.strip("\n"): 0 for line in find_words_file.readlines()}

for line in input_file.readlines():
    # split the line to words
    words = line.split()
    for word in words:
        # remove punctuation marks
        word = split("[.,:;!'/\")]", word)[0]
        if word.lower() in word_frequency:
            # make sure the case match
            r = handle_case(word, english_french_words[word.lower()])
            line = line.replace(word, r)
            # increment the word frequency
            word_frequency[word.lower()] += 1
    output_file.write(line)

# add the header first before looping
results_file.write(f"English,French,Frequency\n")
for row in english_french_words.items():
    results_file.write(f"{row[0]},{row[1]},{word_frequency[row[0]]}\n")

# close open files
input_file.close()
output_file.close()
results_file.close()
find_words_file.close()

# get the performance details
time_taken = perf_counter() - start
# memory usage in MBs
memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1048576
print(f"[TIME TAKEN] : {time_taken} seconds")
print(f"[MEMORY USED] : {memory_usage} MB")
