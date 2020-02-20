import argparse
from search import Search


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
    pipeline = Search("query_config.ini", query)

    run_type = parser.parse_args().type
    if run_type == 1:
        pipeline.find_repos()
        pipeline.find_code_in_repo()
    elif run_type == 2:
        pipeline.find_repos()
    else:
        pipeline.find_code_in_repo()


main()
