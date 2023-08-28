# import csv for use

from csv import reader, writer
from pandas import read_csv
from typing import Iterable


# add header to csv
def addHeader(header_str: Iterable[str], filename: str):
    dataframe = read_csv(filename, header=None)
    dataframe.to_csv(filename, header=header_str, index=0)


# addHeader(("Number & Names", ))


# row writer
def csv_writer(row: Iterable[str], filename: str):
    # write to filename using the csv writer object
    with open(filename, "a") as csv_f:
        writer_obj = writer(csv_f, delimiter=",")
        writer_obj.writerow(row)
        # csv_f.wrte(row[0])


# rows writer
def csv_rows(rows: Iterable[str], filename: str):
    # write to filename using the csv writer object
    with open(filename, "a") as csv_f:
        # writer_obj = writer(csv_f)
        # writer_obj.writerows(rows)
        csv_f.writelines(rows)


def getAtIndexes(indexes: Iterable[int], line: str) -> Iterable[str]:
    # split at commas and return the str at the indexes
    strings = line.split(",")
    return [strings[i] for i in indexes]


def removeCharactersFromStr(characters: Iterable[str], string: str):
    # remove characters from a split string
    lst = [character for character in string if character not in characters]
    return "".join(lst)


def combineLines(lines: Iterable[str]):
    # remove second line link and combine the two lines
    fline = lines[0].split(",")[:-1]
    return "".join(fline) + lines[1]


def getFnamePhone(line: str) -> Iterable[str]:
    # return fname, phone
    fname, phone = getAtIndexes((2, 7), line)
    phone = removeCharactersFromStr(
        ("(", ")", "-", " "), phone)
    return fname, phone


def handleExceptions(lines: Iterable[str]):
    line = combineLines(lines)
    for city in ("Dallas", "Atlanta", "Los Angeles"):
        if city.lower() in line:
            fname, phone = getFnamePhone(line)
            if len(phone) == 10:
                csv_writer(
                    ",".join((fname, phone, city)) + "\n", "Second.csv")
    else:
        fname, phone = getFnamePhone(line)
        if len(phone) == 10:
            csv_writer(",".join((fname, phone)) + "\n", "First.csv")


def combineCSV(files: Iterable[str]):
    # combine data from different CSV files
    for file in files:
        # open and read the file, save its content to lines
        with open(file, "r") as csvfile:
            lines = csvfile.readlines()
            # open and append data from lines to combinedfiles.csv
            csv_rows(lines, "combinedfiles.csv")


# combineCSV(("2021 combines.csv", "Combine_2021_player_form2021-10-05_10_10_17.csv"))


def CSVwithout(fields: Iterable[str], dist: str):
    # create a new csv file without <fields> in "combinedfiles.csv"
    with open("Combine_2021_player_form2021-10-05_10_10_17.csv", "r") as file:
        reader_obj = reader(file)
        for line in reader_obj:
            searchString = "".join(line)
            for field in fields:
                if field.lower() in searchString.lower():
                    # second file, with Dallas, Los Angeles, Atlanta
                    try:
                        fname, phone, location = line[1], line[6], line[5]
                        phone = removeCharactersFromStr(
                            ("(", "-", ")", " "), phone)
                        if len(phone) == 10:
                            csv_writer((fname, phone, location), "Second1.csv")
                    except IndexError:
                        print("<-", line)
                    break
            # if no break occured
            else:
                # first file, the rest
                try:
                    fname, phone = line[1], line[6]
                    phone = removeCharactersFromStr(
                        ("(", "-", ")", " "), phone)
                    if len(phone) == 10:
                        csv_writer((fname, phone), dist)
                except IndexError:
                    print("->", line)


# CSVwithout(("Dallas", "Atlanta", "Los Angeles"), "First1.csv")
