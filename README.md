# FileScan.py
Scans given files for a given list of terms and returns the filepaths and line numbers where every term was found. Terms that are not found in any files only appear once, with the filepath and line number marked 'N/A'.
## Package Requirements
The script uses the following packages:
```
flashtext      # For searching through files for terms in a more performant way
argparse       # For creating the argument syntax and --help flag
csv            # For writing in CSV
os             # For reading/writing files
sys            # For running the script in the terminal
tqdm           # For displaying a progress bar as the script runs
```
If you don't have any of these packages, you can install them by running the following in your terminal:
```
pip install flashtext argparse csv os sys tqdm
```
**Note:** If your system says 'pip' isn't installed or a command, 'pip3' might work instead.
## Running the Script
You can run the script by opening a terminal in its directory (or specifying the filepath to it) and running:
```
python ScanFiles.py {SCANNED_FILEPATH}
```
Where SCANNED_FILEPATH is the file or directory/folder you want to search. Files will be searched directly, while directories (or subdirectories) will instead have their contents searched.

It can also take several additional arguments in any order after SCANNED_FILEPATH:
```
--help                                            Shows script syntax without actually running the script (in case this readme isn't up to date).
--term_list_filepath {TERM_LIST_FILEPATH}         Path to the term list file (default: 'termList.csv')
--output_file_base_name {OUTPUT_FILE_BASE_NAME}   Base name for the output file (default: 'output.csv')
--case_sensitive                                  Enable case-sensitive term matching (default: False)
--overwrite_allowed                               Allow overwriting if a file already exists at the specified location (default: False)
```
These arguments are all optional; any you don't provide will use their specified defaults.

A few extra notes:
- If a file already exists with the name you specified for the output (and you didn't allow overwriting), the resulting file find the first available name with a '_#' at the end to write to instead. For example, if 'output.csv' is taken, the script will check if 'output_1.csv' is taken, then 'output_2.csv', and so on until an available name is found, which will then be the output file's name.
- The terms in the termlist file are assumed to be delimited by whitespace. If the termlist file isn't found at the path you specified (or the default), it will raise an error and exit.
- While searching, the script quietly passes over files it determines to be unreadable.
- Terms are not searched inclusively: searching for '**apple**' would not return lines in a file containing '**apple1**' or '**badapple**'. There is an exception, however, for non-alphanumeric characters (like quotes or parentheses). This is intentional, as it's assumed some terms will be similar and a user likely wouldn't want files returned just because they contained a term that contains another term.
- The script doesn't care if a term appears in any given line more than once.
## Unit Testing
This script has a separate file for unit testing in the same location as the main script. During development, you can confirm that everything works by running:
```python ScanFilesTest.py```
