import os
from dotenv import load_dotenv
from github import Github

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
github = Github(GITHUB_TOKEN)

test_repo = "mery-top/AI_Phishing_detector-Model-Train"  # Replace with a public repository
repo = github.get_repo(test_repo)
print(repo.name, repo.description)

