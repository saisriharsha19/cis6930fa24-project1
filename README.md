# cis6930fa24-project1

# README

# Name: Sai Sri Harsha Guddati
## Assignment Description
In this project, we need to create a data pipeline to develop a system that processes plain text documents, identifying and censoring sensitive information. The system is designed to read all text files that match a specified pattern and apply various redaction techniques to remove names, dates, phone numbers, addresses, and specific concepts.

### Functionality Overview
The command above instructs the program to:

Input: Read all .txt files in the current directory.
Redaction Flags: Censor all names, dates, phone numbers, and addresses.
Concept Redaction: Remove any sentences related to the concept of say "kids." (NOTE: concept can be of any thing)
Output: Save the modified files in the files/ directory, appending .censored to each filename.
Statistics: Print redaction statistics to the standard error stream.

### Parameters
--input: Specifies the glob pattern for files to process. The program should gracefully handle any unreadable files with appropriate error messages.
--output: Defines the directory for saving censored files. Each output file will have the original filename with a .censored extension.

### Censor Flags
The following flags control which types of sensitive information are redacted:

--names: Censors any recognized names, including persons and organizations.
--dates: Removes various date formats, such as "4/9/2025" and "April 9th."
--phones: Censors phone numbers in multiple formats.
--address: Censors physical postal addresses (excluding email addresses).

### Concept Redaction
The --concept flag can be used multiple times to specify themes or ideas for redaction (e.g., --concept prison --concept kids). This flag identifies and censors entire sentences that reference the specified concepts. 

### Statistics
The --stats option allows you to specify where to output the redaction statistics, which includes:

The count and types of censored items.
Summary statistics for each processed file.

## How to Install
To install the required dependencies, ensure you have pipenv installed. Navigate to the project directory and run:

```bash 
pipenv install -e .
```
This will install all the necessary dependencies in an isolated environment.

## How to Run
Run the script from the command line with the following parameters:

```bash 
    pipenv run python redactor.py --input '*.txt' \
                    --names --dates --phones --address \
                    --concept 'something' \
                    --output 'files/' \
                    --stats stderr
```


## Testing
To run the test files in the /tests/ folder

```bash
pipenv run python -m pytest -v
```

The test files are located in the tests/ folder, ensuring that the critical functions work as expected.

## Example Output
After running the code with text file, the following output will be printed as an example of the redatced text:

```python 
    print('''To: ebass@enron.com
    Subject: 81643512 - ████████ Reservation Confirmation Number
    Mime-Version: 1.0
    Content-Type: text/plain; charset=us-ascii
    Content-Transfer-Encoding: 7bit
    X-From: Reservations@████████.com
    X-To: EBASS@ENRON.COM
    X-cc: 
    X-bcc: 
    X-Folder: \Eric_Bass_Nov2001\Notes Folders\All documents
    X-Origin: BASS-E
    X-FileName: ebass.nsf

    ██████████████████
    530 ████████
    █████████, CA  92101
    tel: 619-446-3000
    fax: 619-446-3010''')
```
## Functions Overview
### Main Functions
#### 1. main()
This function serves as the entry point for the application. It uses argparse to handle command-line arguments and initiate the redaction process.

Command-Line Arguments:

--input: Input file pattern (e.g., *.txt). (Required)
--names: Flag to indicate redaction of names (e.g., persons or organizations).
--dates: Flag to indicate redaction of dates and times.
--phones: Flag to indicate redaction of phone numbers.
--address: Flag to indicate redaction of addresses.
--concept: A specific concept whose sentences should be redacted.
--output: Directory where the redacted files will be saved. (Required)
--stats: Specify where to output redaction statistics (stderr or stdout).
#### 2. redact_file(input_file, output_dir, flags, concept)
This function reads the contents of a specified input file, processes the text to redact sensitive information based on the provided flags, and saves the redacted content to the specified output directory. It also returns a statistics dictionary detailing the count of redacted items.

Parameters:

input_file: Path to the input text file.
output_dir: Directory to save the redacted file.
flags: List of redaction flags indicating what to redact.
concept: A specific concept for sentence redaction.
Returns:

A dictionary containing statistics on the number of redactions performed.
#### 3. redact_names(doc)
This function takes a spaCy document and redacts recognized names (persons and organizations) by replacing them with a placeholder (█).

Parameters:

doc: A spaCy document object containing the text to process.
Returns:

The modified text with names redacted.
#### 4. redact_dates(doc)
This function redacts recognized dates and times in a given spaCy document.

Parameters:

doc: A spaCy document object containing the text to process.
Returns:

The modified text with dates and times redacted.
#### 5. redact_phones(text)
This function uses a regular expression to find and redact phone numbers in the provided text.

Parameters:

text: The input text string.
Returns:

The modified text with phone numbers redacted.
#### 6. redact_addresses(doc, text)
This function redacts addresses found in the text, including both structured addresses and recognized geographical locations.

Parameters:

doc: A spaCy document object containing the text to process.
text: The input text string.
Returns:

The modified text with addresses redacted.
#### 7. get_synonyms(concept)
This function retrieves synonyms for a specified concept using the WordNet lexical database.

Parameters:

concept: The concept for which synonyms are to be found.
Returns:

A set of synonyms for the given concept.
#### 8. redact_concept(doc, concept)
This function identifies sentences containing a specified concept and redacts those sentences in the provided document.

Parameters:

doc: A spaCy document object containing the text to process.
concept: The concept for which sentences should be redacted.
Returns:

The modified text with sentences redacted and the count of redacted sentences.
### Testing Functions
The testing suite utilizes pytest to validate the functionality of the redaction features.

#### 1. test_redact_file(sample_text_file, output_dir)
This test checks the redact_file function to ensure that it correctly redacts names, dates, phone numbers, addresses, and specific concepts from a sample text file. It verifies the existence of the output file and the accuracy of redaction counts.

#### 2. test_main(sample_text_file, output_dir)
This test simulates command-line execution to verify the correct behavior of the main() function. It checks that the output file is created as expected with the proper redaction.

#### 3. test_redact_names(doc)
This test validates that names are correctly redacted from the text by ensuring that specific names do not appear in the output.

#### 4. test_redact_dates(doc)
This test confirms that dates are correctly redacted from the text by ensuring that specific dates do not appear in the output.

#### 5. test_redact_phones()
This test checks that phone numbers are correctly redacted using a sample text containing a phone number.

#### 6. test_redact_addresses(doc)
This test verifies that addresses are properly redacted from the text.

#### 7. test_redact_concept(doc)
This test ensures that sentences containing a specified concept are redacted and checks the count of redacted sentences.
## Bugs and Assumptions
### Bugs/Issues
#### Dependency on NLTK Downloads:

The code uses nltk.download("wordnet", quiet=True), which requires internet access to download the WordNet corpus. If run in an environment without internet access, it will fail. A better approach would be to check if WordNet is already downloaded.
#### Matcher Pattern Flexibility:

The address matcher pattern (pattern variable) is quite specific (uses regex and a library named pyap). If the format of addresses in the text varies significantly, it may not match some addresses correctly. This may lead to missed redactions.
#### Regex for Phone Numbers:

The regex pattern for phone numbers in redact_phones may not cover all possible phone formats, especially international formats. For example, it might miss formats like "+44 20 1234 5678" (UK) or special characters.

#### Concept Redaction Logic:

In redact_concept, the logic that checks for synonym similarity might not be efficient for large texts or numerous synonyms. It can lead to performance issues or missed redactions if synonym detection fails.
#### Output File Naming:

The output file is named with .censored but does not validate if the output_dir already contains a file with the same name, which could lead to overwriting existing files.

#### Statistics Calculation:

The statistics collected do not differentiate between multiple occurrences of the same entity type (e.g., if "Jane Doe" appears multiple times). This may lead to inaccurate reporting of redacted items.
### Assumptions:

1. I'm assuming that Spacy's entity recognition is able to handle and redact all the Names and Dates

2. The argument parsing assumes that the user will provide the --input and --output parameters. There are no checks for valid input patterns or output directory existence prior to processing.
Assumptions

3. I'm assuming that input files will be in a specific format that can be processed by spaCy without issues. Non-standard text files might cause unexpected errors.
