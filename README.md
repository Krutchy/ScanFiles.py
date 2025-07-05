# WordFileScan
Scans given files for a given list of terms and returns the filepaths and line numbers where every term was found. Terms that are not found in any files only appear once, with the filepath and line number marked 'N/A'.

## Running the Script
You can run the script by opening a terminal in its directory (or specifying the filepath to it) and running:
```
python ScanFiles.py {SCANNED_FILEPATH}
```

It can also take several additional arguments if you don't want to use their defaults:
```
--help
                        Shows script syntax (just in case this readme isn't up to date).
--term_list_filepath {TERM_LIST_FILEPATH}
                        Path to the term list file (default: 'termList.csv')
--output_file_base_name {OUTPUT_FILE_BASE_NAME}
                        Base name for the output file (default: 'output.csv')
--case_sensitive        Enable case-sensitive term matching (default: False)
--overwrite_allowed     Allow overwriting if a file already exists at the specified location (default: False)
```
## Unit Testing
This script has a separate file for unit testing at the same location called 'ScanFilesTest.py', which you can run in the terminal to confirm that everything still works.
