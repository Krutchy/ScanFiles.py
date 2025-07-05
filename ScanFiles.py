import os
import re
import csv
import sys

# Loads words from @file into dictionary WordList (words should be delimited by whitespace)
# keys: words being searched
# values: str array of filespaths and line numbers where each word is found
def LoadWordList(file, case_sensitive):
    with open(file, 'r') as f:
        words = f.read().split()
        return {word if case_sensitive else word.lower(): [] for word in words}

# Returns filename, unless file with that name already exists, in which case it adds an '_#' to the name
def GetAvailableFilename(base):
    if not os.path.exists(base):
        return base
    name, ext = os.path.splitext(base)
    i = 1
    while os.path.exists(f"{name}_{i}{ext}"):
        i += 1
    # Examples: 'output_1.txt', 'output_2.txt'
    return f"{name}_{i}{ext}"

# Writes resulting @wordList to output file of specified @base_name and type (.txt or .csv)
# Column 1: Word
# Column 2: Filepath where word was found
# Column 3: Line Number in file where word was found
def WriteOutput(base_name, wordList):
    with open(GetAvailableFilename(base_name), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Column Headers
        writer.writerow(['Word', 'Filepath', 'Line Number'])
        # For each word in wordList
        for word, entries in wordList.items():
            if entries:
                writer.writerows([[word, path, line] for path, line in entries])
            else:
                writer.writerow([word, 'N/A', 'N/A'])

# Scans files at @path to populate the @wordList with files where words are found.
def ScanFiles(path, wordlist, case_sensitive):
    # If path is directory:
    if os.path.isdir(path):
        # For each item in directory:
        for item in os.listdir(path):
            # Directories perform recursive calls to search their contents.
            ScanFiles(os.path.join(path, item), wordlist, case_sensitive)
    # If path is file:
    else:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read line by line, starting at line 1
                for i, line in enumerate(f, 1):
                    # Read contents of line
                    check_line = line if case_sensitive else line.lower()
                    for word in wordlist:
                        target = word if case_sensitive else word.lower()
                        if target in check_line:
                            wordlist[word].append((os.path.abspath(path), i))
        except:
            pass # Silently ignore unreadable files


# Run Script
if __name__ == "__main__":
    # Enforce proper function call
    if not (4 <= len(sys.argv) <= 5):
        print("Usage: python ScanFiles.py <scanned_filepath> <word_list_filepath> <output_file_base_name> <case_sensitive (optional)>")
        sys.exit(1)

    # User Supplied Arguments
    scanned_path = sys.argv[1]
    output_file = sys.argv[3]
    case_sensitive = len(sys.argv) == 5 and sys.argv[4].lower() == 'true' # Optional, Default is False
    # Is loaded out of order to factor in case sensitivity
    wordlist = LoadWordList(sys.argv[2], case_sensitive)

    ScanFiles(scanned_path, wordlist, case_sensitive)
    WriteOutput(output_file, wordlist)
