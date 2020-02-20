from github import Github
import time
import datetime


class Search:

    def __init__(self, config_file, query):

        self.config = self.read_config(config_file)
        self.query = query
        self.repo_names = set()

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

    def read_repo_names(self):
        with open(self.config["REPO_NAMES_FILE"]) as repo_names:
            for repo in repo_names:
                self.repo_names.add(repo.strip())

    def write_repo_names_to_file(self):
        with open(self.config["REPO_NAMES_FILE"], "w") as repo_names:
            for repo in self.repo_names:
                repo_names.write(repo + "\n")

    def check_search_rate(self):
        search_rate = Github(self.config["TOKEN"]).get_rate_limit().search
        if search_rate.remaining == 0:
            print("You have 0/%i API calls remaining. Reset time: %s"
                  % (search_rate.limit, search_rate.reset))
            raise RuntimeError
        else:
            print("You have %i/%i API calls remaining"
                  % (search_rate.remaining, search_rate.limit))

    def find_repos(self):
        try:
            self.check_search_rate()
            github = Github(self.config["TOKEN"])

            page_count = 0
            while page_count < self.config["MAX_PAGES"]:
                result = github.search_repositories(self.query)
                repo_count = 0
                page = 1
                # Can only read max repos at a time
                while repo_count <= self.config["MAX_REPOS"]:
                    for repo in result.get_page(page):
                        self.repo_names.add(repo.full_name)
                        repo_count += 1
                        page_count += 1
                    page += 1
                self.go_to_sleep("Quick nap before resume",
                                 self.config["QUICK_SLEEP"])
            self.write_repo_names_to_file()
        except:
            self.go_to_sleep(
                "Error: abuse detection mechanism detected.",
                self.config["ERROR_SLEEP"])

    def find_code_in_repo(self):
        try:
            self.check_search_rate()
            self.read_repo_names()
            github = Github(self.config["TOKEN"])

            counter = 0
            for repo in self.repo_names:
                try:
                    query = self.query + " repo:" + repo
                    result = github.search_code(query)

                    if result.totalCount > 0:
                        print(result)

                    counter += 1
                    if counter % 15 == 0:
                        self.go_to_sleep("Quick nap before resume",
                                         self.config["QUICK_SLEEP"])
                except:
                    self.go_to_sleep(
                        "Error: abuse detection mechanism detected.",
                        self.config["ERROR_SLEEP"])
        except:
            self.go_to_sleep(
                "Error: abuse detection mechanism detected.",
                self.config["ERROR_SLEEP"])
