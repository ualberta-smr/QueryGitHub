import argparse
from search import Search


def prepare_search(search_string):

    char_list = ["\""]
    for char in search_string:
        if char == "\"" or char == "'":
            char_list.append("\\")
        char_list.append(char)

    char_list.append("\"")

    return "".join(char_list)


def main():
    parser = argparse.ArgumentParser(
        description="GitHub search helper. Program will ask for a input query. "
                    "e.g., 'UnsupportedEncodingException UTf-8 in:file"
                    "language:java' and will replace ' ' with '+'")
    parser.add_argument("--type", "-t",
                        help="How much of the process do you want to run? "
                             "(1) Full "
                             "(2) Only find potential repos "
                             "(3) Search repos for code",
                        type=int,
                        default=1)

    query = input("What is your search query? ")
    query = query.replace(" ", "+")
    search = input("What is the code you are searching for? ")
    search = prepare_search(search)
    pipeline = Search("query_config.ini", query, search)

    run_type = parser.parse_args().type
    if run_type == 1:
        pipeline.find_repos()
        pipeline.find_code_in_repo()
    elif run_type == 2:
        pipeline.find_repos()
    elif run_type == 3:
        pipeline.find_code_in_repo()
    else:
        pipeline.check_search_rate()


main()
