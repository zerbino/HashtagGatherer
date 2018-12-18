# -*- coding: utf-8 -*-

import re
import os
import csv
from functools import reduce

from odf import text, teletype
from odf.opendocument import load

def open_odt(filepath):
    try:
        load(filepath)
    except Exception as e:
        raise e
    return load(filepath)
    
def get_odt_text(odt_object):
    all_paragraphs = odt_object.getElementsByType(text.P)
    if (len(all_paragraphs) == 0):
        return ""
    else :
        return reduce(lambda text,  paragraph: text + "\n" + teletype.extractText(paragraph),  all_paragraphs,  "")

"""
This method returns all the hashtags contained in the string text
"""

def extract_hashtags_from_text(text):
    return re.findall(r"#\S*(?=(?:$|\s))", text, re.MULTILINE)
    
def get_hashtags_from_file(fullfilepath):
    filetext = get_odt_text(open_odt(fullfilepath))
    return extract_hashtags_from_text(filetext)
    
def get_list_of_odts(folder_path):
    odtfiles = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".odt"):
                odtfiles.append(os.path.join(root,  file))
    return odtfiles
    
"""
Takes a hashtag and the full path of the file where it was extracted from
and return it into a dictionary of the form : 
{"hashtag": [hashtag value], "originfile": [file full path]}
"""

def format_dict_hashtag_and_originfile(hashtag,  originfile):
    return {"hashtag": hashtag,  "originfile": originfile}
    
"""
Takes a list of hashtags extracted from the same file and returns a list of dictionary
of a form as returned by format_dict_hashtag_and_originfile method
"""

def hashtag_list_to_dict_list(hashtaglist,  originfile):
    dictlist = []
    for hashtag in hashtaglist:
        dictlist.append(format_dict_hashtag_and_originfile(hashtag,  originfile))
    return dictlist
    
"""
Return the list of all hashtags contained (recursively) in all odt files from a folder, in the form of 
a list of strings if withoriginfile is False, in the form of a list of dictionary if withoriginfile 
is True. The dictionary has 2 properties, one named "hashtag" with a hashtag as a 
value, and one name "originfile" with the full path of the file where the hashtag was
extracted from.
"""

def get_hashtags_in_folder(folder_path,  withoriginfile=False):
    hashtags = []
    for filepath in get_list_of_odts(folder_path):
        hashtags_in_odt = get_hashtags_from_file(filepath)
        if withoriginfile:
            hashtags_in_odt = hashtag_list_to_dict_list(hashtags_in_odt,  filepath)
        hashtags = hashtags + hashtags_in_odt
    return hashtags
    
    
"""
Generates a coma separated csv with all the hashtags contained in all odt files in folderpath 
(recursively), and their corresponding origin file path. The csv file is exported to outputpath, 
which is equal to folderpath by default. The name of the exported file can be precised with 
filename, with no extension (it will be a CSV). To have outputpath = folderpath, you can 
give outputpath the value "="
"""

def generate_csv_of_hastags_with_origin_files(folderpath,  outputpath="=",  filename="hashtags"):
    if outputpath == "=":
        outputpath = folderpath
    hashtags_with_origin_files = get_hashtags_in_folder(folderpath, True)
    with open(os.path.join(outputpath,  filename + ".csv"), 'w', newline='') as csvfile:
        fieldnames = ["hashtag",  "originfile"]
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writeheader()
        csvwriter.writerows(hashtags_with_origin_files)
