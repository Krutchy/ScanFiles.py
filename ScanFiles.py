import argparse                         # https://docs.python.org/3/library/argparse.html    # License: 
import csv                              # https://docs.python.org/3/library/csv.html         # License: 
from flashtext import KeywordProcessor  # https://flashtext.readthedocs.io/en/latest/        # License: MIT
import os                               # https://docs.python.org/3/library/os.html          # License: 
import sys                              # https://docs.python.org/3/library/sys.html         # License: 
from tqdm import tqdm                   # https://github.com/tqdm/tqdm                       # License: MIT

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

def BuildKeywordProcessor(terms, case_sensitive):
    '''
    Builds keyword processor using 'flashtext' package. Flashtext
    has its own algorithm that extracts keywords from a string argument
    using the function 'extract_keywords(str)' to return a list.

    Args:
        terms (str[]): the keys from the termList dict
        case_sensitive (bool): whether or not the terms will be cast to lowercase

    Returns:
        kp (KeywordProcessor): class containing terms to be searched for in 'ScanFiles'
    '''
    kp = KeywordProcessor(case_sensitive=case_sensitive)
    for term in terms:
        kp.add_keyword(term)
    return kp

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
    keyword_processor = BuildKeywordProcessor(termList.keys(), case_sensitive)

    for filepath in tqdm(all_files, desc="Scanning files", unit="file"):                            # For each file:
        relpath = os.path.relpath(filepath, start=path)                                             # Return a relative path to the root directory
        try:
            with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:                   # utf-8-sig avoids quirks due to hidden characters at the start of a file in certain encodings
                for i, line in enumerate(f, 1):                                                     # For each line of the file:
                    check_line = line if case_sensitive else line.lower()                           # Account for case sensitivity if needed.
                    found_terms = set(keyword_processor.extract_keywords(check_line))               # Get a set of all terms found in the line.
                    for original_term in found_terms:                                               # For each term found:
                        termList[original_term].append((relpath, i))                                # Add that term to found terms.
        except:
            pass                                                                                    # Quietly ignore unreadable files.

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
        return base                                             # Just return original name for file.
    name, ext = os.path.splitext(base)                          # Separate the filename and extension.
    i = 1
    while os.path.exists(f"{name}_{i}{ext}"):                   # Until a name that isn't taken is found:
        i += 1                                                  # Increment by 1 to add to basename (e.g., 'output_1.csv")
    return f"{name}_{i}{ext}"                                   # Return first available name.

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
    with open(GetAvailableFilename(base_name, overwrite_allowed), 'w', newline='', encoding='utf-8') as f:  # Opens file of given name to write output to.
        writer = csv.writer(f)                                                                              # Write output in CSV format.
        writer.writerow(['Word', 'Filepath', 'Line Number'])                                                # Write column headers.
        for term, entries in termList.items():                                                              # For each term in termList:
            if entries:                                                                                     # If term was found in any files:
                writer.writerows([[term, path, line] for path, line in entries])                            # Write each filepath and line number where term was found.
            else:                                                                                           # Otherwise, term wasn't found in any file:
                writer.writerow([term, 'N/A', 'N/A'])                                                       # Write 'N/A' to filepath and line number columns.


# Running the script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan files for terms and generate output.")
    parser.add_argument("scanned_filepath", help="Path to the file or directory to scan")
    parser.add_argument("--term_list_filepath", default="termList.csv", help="Path to the term list file (default: 'termList.csv')")
    parser.add_argument("--output_file_base_name", default="output.csv", help="Base name for the output file (default: 'output.csv')")
    parser.add_argument("--case_sensitive", action="store_true", help="Enable case-sensitive term matching (default: False)")
    parser.add_argument("--overwrite_allowed", action="store_true", help="Allow overwriting if a file already exists at the specified location (default: False)")

    args = parser.parse_args()
    try:
        termList = LoadTermList(args.term_list_filepath, args.case_sensitive)
        ScanFiles(args.scanned_filepath, termList, args.case_sensitive)
        WriteOutput(args.output_file_base_name, termList, args.overwrite_allowed)
    except KeyboardInterrupt: # Usually Ctrl+C
        print("\nScan stopped by user. Exiting script.")
        sys.exit(0)