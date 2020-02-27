from github import Github
import time
import datetime
import re


class Search:

    def __init__(self, config_file, query, search):

        self.config = self.read_config(config_file)
        self.query = query
        self.search = search
        self.repo_names = []
        self.file_names = []

    @staticmethod
    def read_config(config_file):
        config = {}
        with open(config_file, 'r') as file:
            for line in file:
                key, value = line.split("=")
                if key not in config:
                    try:
                        config[key] = int(value)
                    except ValueError:
                        config[key] = value.strip()
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
                self.repo_names.append(repo.strip())

    @staticmethod
    def write_list_to_file(filename, lst):
        with open(filename, "w") as repo_names:
            for repo in lst:
                repo_names.write(repo + "\n")

    def check_search_rate(self):
        search_rate = Github(self.config["TOKEN"]).get_rate_limit().search
        if search_rate.remaining == 0:
            print("You have 0/%i API calls remaining. Reset time: %s"
                  % (search_rate.limit, search_rate.reset.replace(tzinfo=datetime.timezone.utc).astimezone()))
            raise RuntimeError
        else:
            print("You have %i/%i API calls remaining"
                  % (search_rate.remaining, search_rate.limit))

    def find_repos(self):
        try:
            self.check_search_rate()
            github = Github(self.config["TOKEN"])

            potential_repos = set()
            issue_repos = set()
            query = self.query + " pushed:>=" + (datetime.datetime.now() -
                                                 datetime.timedelta(days=self.config["TIME_SPAN"])
                                                 ).strftime("%Y-%m-%d") + " stars:>=5"
            result = github.search_repositories(query)
            if result.totalCount > 0:
                repo_count = 0
                page = 1
                # Can only read in sets of 30 so max is 990 results
                while repo_count < self.config["MAX_RESULTS"]:
                    try:
                        for repo in result.get_page(page):
                            potential_repos.add(repo.full_name)
                            repo_count += 1
                        page += 1
                    except Exception as e:
                        print(e)
                        match = re.match("[0-9]+", str(e))
                        if match.group() == '422':
                            break
                        self.go_to_sleep("Error when retrieving repos", self.config["QUICK_SLEEP"])
                self.go_to_sleep("Quick nap after getting repos, before checking the PRs", self.config["QUICK_SLEEP"])
                # Loop through potential repos and find ones that have closed Pull Requests
                i = 0
                issue_query = "type:pr state:closed"
                potential_repo_list = list(potential_repos)
                while i < len(potential_repos):
                    try:
                        query = issue_query + " repo:" + potential_repo_list[i]
                        result = github.search_issues(query)
                        if result.totalCount > 0:
                            issue_repos.add(potential_repo_list[i])
                        i += 1
                    except Exception as e:
                        print(e)
                        print("%i/%i repos checked" % (i, len(potential_repos)))
                        self.go_to_sleep("Error when checking PRs", self.config["QUICK_SLEEP"])
                self.go_to_sleep("Quick nap after getting repos, before checking the PRs", self.config["QUICK_SLEEP"])
            self.repo_names = list(potential_repos.intersection(issue_repos))
            self.write_list_to_file(self.config["REPO_NAMES_FILE"], self.repo_names)
        except RuntimeError:
            self.go_to_sleep("Error: abuse detection mechanism detected.", self.config["ERROR_SLEEP"])

    def find_code_in_repo(self):
        try:
            self.check_search_rate()
            self.read_repo_names()
            github = Github(self.config["TOKEN"])

            i = 0
            starting_i = 0
            files = set()
            while i < len(self.repo_names):
                query = self.search
                try:
                    # Save the index we started at in case we get an error
                    starting_i = i
                    # Add repo names up to the 256 char limit
                    while len(query) < 256 and i < len(self.repo_names):
                        temp_query = query + " repo:" + self.repo_names[i]
                        if len(temp_query) > 256:
                            break
                        else:
                            query = temp_query
                            i += 1
                    # Search and add the files which contain the code
                    result = github.search_code(query)
                    for contentFile in result:
                        files.add(contentFile.html_url)
                    i += 1
                except Exception as e:
                    print(e)
                    # If we get an error then reset the index
                    i = starting_i
                    print("%i/%i repos analyzed" % (i, len(self.repo_names)))
                    self.go_to_sleep("Error when searching for code", self.config["QUICK_SLEEP"])

            self.file_names = list(files)
            self.write_list_to_file(self.config["FILE_NAMES_FILE"], self.file_names)
        except RuntimeError:
            self.go_to_sleep("Error: abuse detection mechanism detected.", self.config["ERROR_SLEEP"])
