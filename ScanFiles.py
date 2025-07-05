import os
import re
from tqdm import tqdm
import csv
import sys

# Loads words from @file into dictionary WordList (words should be delimited by whitespace)
# keys: words being searched
# values: str array of filespaths and line numbers where each word is found
def LoadWordList(file, case_sensitive):
    with open(file, 'r', encoding='utf-8-sig') as f:
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

def GetAllFiles(path):
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

def ScanFiles(path, wordlist, case_sensitive):
    all_files = GetAllFiles(path) if os.path.isdir(path) else [path]

    for filepath in tqdm(all_files, desc="Scanning files", unit="file"):
        try:
            with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    check_line = line if case_sensitive else line.lower()
                    for word in wordlist:
                        target = word if case_sensitive else word.lower()
                        # Use regex to find exact matches, respecting case sensitivity
                        pattern = re.compile(rf'\b{re.escape(target)}\b' if case_sensitive else rf'\b{re.escape(target)}\b', re.IGNORECASE if not case_sensitive else 0)
                        if pattern.search(line):
                            wordlist[word].append((os.path.relpath(filepath, start=path), i))
        except:
            pass



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
