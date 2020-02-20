from search import Search


def main():
    # query = input("What is your search query? ")
    query = "UnsupportedEncodingException+UTf-8+in:file+language:java"

    pipeline = Search("query_config.ini", query)
    pipeline.find_repos()


main()
