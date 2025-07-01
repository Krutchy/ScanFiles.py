# WordFileScan
The function provided has four arguments: </br>
### python ScanFiles.py <str: scanned_filepath> <str: word_list_filepath> <str: output_file_base_name> <bool: case_sensitive (Optional)>

## @str scanned_filepath
This is the filepath that will be searched through by the script. 
- You can use a local filepath (same directory as ScanFiles.py)
- Files will be searched directly.
- Directories will call ScanFiles recursively.

## @str word_list_filepath
This is the filepath containing the file that has the words this script will search for.
- You can use a local filepath (same directory as ScanFiles.py)
- Words should be delimited by whitespace.
- Words are not case sensitive unless that is specified (in later arg).

## @str output_file_base_name
This is the name you want for the output file. 
- The file type should be specified ('.txt' or '.csv').
- If a file with the given name already exists, a file with the name and a number added to the end will be created instead (e.g., 'output_1.txt', 'output_2.txt').
- File will be written to same directory as ScanFiles.py

## @bool case_sensitive (Optional)
Whether you want case sensitivity for the words being searched.
- The file contents and the wordlist will both be affected during the search.

## The following are examples of what calling the function would look like:
python ScanFiles.py searchDirectory wordList.txt output.txt </br>
python ScanFiles.py searchDirectory wordListFilePath output.txt True </br>
python ScanFiles.py searchDirectory wordListFilePath output.txt False </br>
python ScanFiles.py searchDirectory wordListFilePath output.csv True 
