# WordFileScan
The function provided has four arguments: </br>
python ScanFiles.py scanned_filepath word_list_filepath output_file_base_name case_sensitive

## @str scanned_filepath
This is the filepath that will be searched through by the script. 
- You can use a local filepath (same directory as ScanFiles.py)
- A file will be searched directly while a directory will have each file within searched, and any subdirectories will call this function recursively.

## @str word_list_filepath
This is the filepath where the list of words that will be searched for is found.
- You can use a local filepath (same directory as ScanFiles.py)
- Distinct words should be delimited by whitespace.

## @str output_file_base_name
This is the name you want for the output file. 
- The file type should be specified ('.txt' or '.csv').
- If a file with the given name already exists, a file with the name and a number added to the end will be created instead (e.g., 'output_1.txt', 'output_2.txt').
- File will be written to same directory as ScanFiles.py

## @bool case_sensitive (Optional)
Whether you want case sensitivity for the words being searched.
- The file contents and the wordlist will both be affected during the search.
- In the output, the words in the wordlist will be written as they were in that file, regardless of case.

## The following are examples of what calling the function would look like:
python ScanFiles.py searchDirectory wordList.txt output.txt </br>
python ScanFiles.py searchDirectory wordListFilePath output.txt True </br>
python ScanFiles.py searchDirectory wordListFilePath output.txt False </br>
python ScanFiles.py searchDirectory wordListFilePath output.csv True 
