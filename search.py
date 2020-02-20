from github import Github
import time
import datetime


class Search:

    def __init__(self, config_file, query):

        self.config = self.read_config(config_file)
        self.query = query

    @staticmethod
    def read_config(config_file):
        config = {}
        with open(config_file, 'r') as file:
            for line in file:
                key, value = line.split("=")
                if key not in config:
                    if key == "TOKEN" or key == "REPO_NAMES_FILE":
                        config[key] = value.strip()
                    else:
                        config[key] = int(value)
        return config

    @staticmethod
    def go_to_sleep(message, sleep_duration):

        start_time = datetime.datetime.now()

        print(message,
              "\nSleeping at:", start_time,
              "for: %i seconds" % sleep_duration)

        time.sleep(sleep_duration)

        end_time = datetime.datetime.now()

        print("Woke at: ", end_time)

    def write_repo_names_to_file(self, repos):
        with open(self.config["REPO_NAMES_FILE"]) as repo_names:
            for repo in repos:
                repo_names.write(repo + "\n")

    def find_repos(self):
        try:
            github = Github(self.config["TOKEN"])
            search_rate = github.get_rate_limit().search

            if search_rate.remaining == 0:
                print("You have 0/%i API calls remaining. Reset time: %s"
                      % (search_rate.limit, search_rate.reset))
                raise RuntimeError
            else:
                print("You have %i/%i API calls remaining"
                      % (search_rate.remaining, search_rate.limit))

            repos = set()
            page_count = 0
            while page_count < self.config["MAX_PAGES"]:
                result = github.search_repositories(self.query)
                repo_count = 0
                page = 1
                while repo_count <= self.config["MAX_REPOS"]:
                    for repo in result.get_page(page):
                        repos.add(repo.full_name)
            self.write_repo_names_to_file(repos)
        except:
            self.go_to_sleep(
                "Error: abuse detection mechanism detected.",
                self.config["ERROR_SLEEP"])
