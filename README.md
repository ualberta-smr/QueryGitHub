# QueryGitHub
A small Python program to easily search GitHub that the web API can not provide

Example of how to run: `python main.py -t 1`

There is one argument that is take in the command line:

--type, -t: Type of query to run

- 1 - This tells the program to search for potential repositories AND check the files in the repository for the given code terms

- 2 - This tells the program to only find potential repositories
          
     This part of the program finds potential repositories that match the query given. The query should follow [GitHub's search syntax](https://help.github.com/en/github/searching-for-information-on-github/understanding-the-search-syntax). The potential repos will be written into a file with the name specified by the `REPO_NAMES_FILE` in `query_config.ini`.

- 3 - This tells the program to only check the files in previously found potential repositories 

     This part of the program queries GitHub using the GitHub search API for code in a given repository. The program loops through all the potential repositories and queries GitHub to search for the given code snippet in the repository. If a file includes the code snippet the url of the file will be written to the file named by the `FILE_NAMES_FILE` in `query_config.ini`.
     
An example the running the program will be:
```
python main.py -t 1
What is your search query? language:php
What is the code you are searching for? !$array $key 
``` 
The output given is not recorded here but you will see a number of "Errors", these are when the program encountered an issue such as reaching the query limit, etc. The program will sleep either for `QUICK_SLEEP` or `ERROR_SLEEP` time (defined in the `query_config.ini`) depending on when the error occurred. Then the program will automatically continue until it reaches the `MAX_` variables also defined in `query_config.ini`.

`TIMESPAN` in `query_config.ini` refers to how many days from the day the program was invoked to look for potential repos that have had a modification within the time span. e.g., with a `TIMESPAN` of 90, the program will only look at repos that have had a commit made in the past 90 days from when the program was invoked.

`TOKEN` in `query_config.ini` is your personal GitHub Token. These can be created [here](https://github.com/settings/tokens)