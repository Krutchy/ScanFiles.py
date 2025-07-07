import argparse                                                     # https://docs.python.org/3/library/argparse.html           # License: Python Software Foundation (Version 2)
import csv                                                          # https://docs.python.org/3/library/csv.html                # License: Python Software Foundation (Version 2)
from concurrent.futures import ThreadPoolExecutor, as_completed     # https://docs.python.org/3/library/concurrent.futures.html # License: Python Software Foundation (Version 2)
from flashtext import KeywordProcessor                              # https://flashtext.readthedocs.io/en/latest/               # License: MIT
import os                                                           # https://docs.python.org/3/library/os.html                 # License: Python Software Foundation (Version 2)
import sys                                                          # https://docs.python.org/3/library/sys.html                # License: Python Software Foundation (Version 2)
from tqdm import tqdm                                               # https://github.com/tqdm/tqdm                              # License: MIT

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

def process_file(filepath, root_path, keyword_processor, case_sensitive):
    '''
    Scans a single file and returns a dictionary of found terms and their locations.

    Args:
        filepath (str): path to file to be scanned
        root_path (str): root directory to compute relative paths
        keyword_processor (KeywordProcessor): initialized processor
        case_sensitive (bool): flag for case sensitivity

    Returns:
        dict: { term: [(relative_filepath, line_number), ...], ... }
    '''
    term_hits = {}                                                                  # Initialize dict for hits
    try:
        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:       # Opened in utf-8-sig as some file encodings have hidden characters at the beginning.
            for i, line in enumerate(f, 1):                                         # For each line in the file:
                check_line = line if case_sensitive else line.lower()               # Account for case sensitivity (if desired).
                found_terms = set(keyword_processor.extract_keywords(check_line))   # Extract found terms from line into a set.
                if found_terms:                                                     # If any terms were found:
                    relpath = os.path.relpath(filepath, start=root_path)            # Get the relative path for the file.
                    for term in found_terms:                                        # For each found term:
                        term_hits.setdefault(term, []).append((relpath, i))         # Add the filepath and line number to that term's key in term_hits.
    except:
        pass                                                                        # Quietly ignore unreadable files.
    return term_hits

def ScanFiles(path, termList, case_sensitive=False):
    '''
    Scans all files under the path using a thread pool, updating termList in-place.

    Args:
        path (str): directory or file to scan
        termList (dict): maps each term to a list of (filepath, line number)
        case_sensitive (bool): case-sensitive matching toggle
    '''
    all_files = GetAllFiles(path) if os.path.isdir(path) else [path]
    keyword_processor = BuildKeywordProcessor(termList.keys(), case_sensitive)

    with ThreadPoolExecutor() as executor:                                                                  # Scans multiple files in parallel.
        futures = [
            executor.submit(process_file, filepath, path, keyword_processor, case_sensitive)                # Submit request to thread pool
            for filepath in all_files                                                                       # For each file
        ]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Scanning files", unit="file"):  # As scanning finishes for each file:
            result = future.result()                                                                        # Get the file's results.
            for term, hits in result.items():                                                               # For each term found:
                termList[term].extend(hits)                                                                 # Add the results to the final termList.

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