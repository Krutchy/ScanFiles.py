import os
import re
from tqdm import tqdm
import csv
import sys
import ahocorasick
import argparse

def LoadTermList(file, case_sensitive):
    '''
    Args:
        file (str): filepath for list of search terms
        case_sensitive (bool): whether or not terms will be case sensitive

    Returns:
        wordList (dict):
            key (str): term to be searched for in 'ScanFiles'
            value (str): filepath where term is found
            value (int): line number in file where term was found

    Raises:
        FileNotFoundError: if no file exists at the specified filepath
    '''
    if not os.path.isfile(file):                                                    # If no file found at specified location:
        raise FileNotFoundError(f"Term list file not found: '{file}'")              # Raise error, end script.

    with open(file, 'r', encoding='utf-8-sig') as f:                                # utf-8-sig used as certain encodings have hidden characters
        terms = f.read().split()                                                    # File should be delimited by whitespace.
        return {term if case_sensitive else term.lower(): [] for term in terms}

def GetAvailableFilename(base, overwrite_allowed=False):
    '''
    If you don't want to overwrite an existing file, this function ensures that
    repeatedly running this script with the same name for the output will
    instead write the output to the next available name. For example, if
    'output.csv' is taken, then this function will check if 'output_1.csv'
    is also taken, then 'output_2.csv', and so on until a name is found
    that isn't taken.

    Args:
        base (str): base filename provided by function 'WriteOutput'
        overwrite_allowed (bool): whether to overwrite the output file if it already exists. Disallowed by default.

    Returns:
        str: name for output file
    '''
    if (not os.path.exists(base)) or (overwrite_allowed==True): # If file name isn't taken or overwriting is allowed:
        return base                                     # Just return original name for file.
    name, ext = os.path.splitext(base)                  # Separate the filename and extension.
    i = 1
    while os.path.exists(f"{name}_{i}{ext}"):           # Until a name that isn't taken is found:
        i += 1                                          # Increment by 1 to add to basename (e.g., 'output_1.csv")
    return f"{name}_{i}{ext}"                           # Return first available name.

def WriteOutput(base_name, termList, overwrite_allowed=False):
    '''
    Writes output from ScanFiles to a file of the specified name. The
    file extension should be included in the name (.csv) as well.
    See function 'GetAvailableFilename' for details on how output is handled
    when a file of the specifed name already exists.

    Args:
        base_name (str): the name of the file to be written
        termList (dict): words, filepaths, and line numbers as produced by 'ScanFiles'
        overwrite_allowed (bool): whether to overwrite the output file if it already exists. Disallowed by default.
    '''
    with open(GetAvailableFilename(base_name, overwrite_allowed), 'w', newline='', encoding='utf-8') as f: # Opens file of given name to write output to.
        writer = csv.writer(f)                                                          # Write output in CSV format.
        writer.writerow(['Word', 'Filepath', 'Line Number'])                            # Write column headers.
        for term, entries in termList.items():                                          # For each term in termList:
            if entries:                                                                 # If term was found in any files:
                writer.writerows([[term, path, line] for path, line in entries])        # Write each filepath and line number where term was found.
            else:                                                                       # Otherwise, term wasn't found in any file:
                writer.writerow([term, 'N/A', 'N/A'])                                   # Write 'N/A' to filepath and line number columns.

def GetAllFiles(path):
    '''
    This function primarily exists so tqdm can provide an indication
    of progress during 'ScanFiles' by parsing the files to be scanned
    ahead of time, thereby determining the total amount.

    Args:
        path (str): the filepath to be scanned. Typically, this is a directory/folder.

    Returns:
        files (list): all filepaths being scanned
    '''
    files = []
    for root, _, filenames in os.walk(path):            # Starting from path, for each file (directories are checked recursively for files):
        for filename in filenames:
            files.append(os.path.join(root, filename))  # Add that filepath to 'files'
    return files

def BuildAutomaton(terms, case_sensitive):
    '''
    Automatons are a class from Aho-Corasick that resemble tries
    in structure but have invocable methods similar to a dict in Python.
    It's possible to serialize or 'pickle' an automaton so it wouldn't 
    need to be rebuilt each time the script is ran (which might be more 
    performant for larger wordlists) but that isn't done in this script.

    Args:
        terms (str[]): the keys from the termList created by LoadTermList
        case_sensitive (bool): whether or not keys will be cast to lowercase

    Returns:
        termAutomaton (ahocorasick.Automaton): the object holding the terms
    to check for in the file list. This is separate from the termList holding
    the filepaths where each term is found in 'ScanFiles'.
    '''
    termAutomaton = ahocorasick.Automaton()             # Initialized but not actually made into automaton yet.
    for term in terms:                                  # For each term:
        key = term if case_sensitive else term.lower()  # Account for case sensitivity if needed.
        termAutomaton.add_word(key, term)               # Add term to automaton
    termAutomaton.make_automaton()                      # Make into automaton.
    return termAutomaton

def ScanFiles(path, termList, case_sensitive=False):
    '''
    Mutates termList by adding filepaths where each term is found. By
    design, this function does not count terms contained in other terms. 
    For example, if 'token1' and 'token12' are both search terms, a file 
    only containing 'token12' will not be considered to contain 'token1'.
    Each file that is found to contain a term will be returned separately,
    and it isn't checked whether a term appears multiple times in a single
    line.

    Args:
        path (str): filepath of directory to be searched through
        termList (dict):
            key (str): term to be searched for
            value (str): filepath where term is found (if any)
            value (int): line number in filepath where term was found (if any)
        case_sensitive (bool): whether the search will be case_sensitive. Case insensitive by default.
    '''
    all_files = GetAllFiles(path) if os.path.isdir(path) else [path]
    automaton = BuildAutomaton(termList.keys(), case_sensitive)

    for filepath in tqdm(all_files, desc="Scanning files", unit="file"):                            # For each file:
        relpath = os.path.relpath(filepath, start=path)                                             # Return a relative path to the root directory
        try:
            with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:                   # utf-8-sig avoids quirks due to hidden characters at the start of a file in certain encodings
                for i, line in enumerate(f, 1):                                                     # For each line of the file:
                    check_line = line if case_sensitive else line.lower()                           # Account for case sensitivity if needed.
                    found_terms = set()                                                             # Only find each term once per line.
                    for end_idx, original_term in automaton.iter(check_line):                       # For every match found in a line:
                        start_idx = end_idx - len(original_term) + 1                                # Calculate index where match starts.

                        before = check_line[start_idx - 1] if start_idx > 0 else ' '                # If character before match,
                        after = check_line[end_idx + 1] if end_idx + 1 < len(check_line) else ' '   # Or character after match
                        if before.isalnum() or after.isalnum():                                     # Is an alphanumeric string:
                            continue                                                                # Then the match is actually part of a larger word, so we'll skip it.

                        if original_term not in found_terms:                                        # If we haven't found the term in the line yet:
                            termList[original_term].append((relpath, i))                            # Add filepath and line number to termList.
                            found_terms.add(original_term)                                          # Add term to found terms.
        except:
            pass                                                                                    # Quietly ignore unreadable files.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan files for terms and generate output.")
    parser.add_argument("scanned_filepath", help="Path to the file or directory to scan")
    parser.add_argument("--term_list_filepath", default="termList.csv", help="Path to the term list file (default: 'termList.csv')")
    parser.add_argument("--output_file_base_name", default="output.csv", help="Base name for the output file (default: 'output.csv')")
    parser.add_argument("--case_sensitive", action="store_true", help="Enable case-sensitive term matching (default: False)")
    parser.add_argument("--overwrite_allowed", action="store_true", help="Allow overwriting of existing output file (default: False)")

    args = parser.parse_args()

    termList = LoadTermList(args.term_list_filepath, args.case_sensitive)
    ScanFiles(args.scanned_filepath, termList, args.case_sensitive)
    WriteOutput(args.output_file_base_name, termList, args.overwrite_allowed)