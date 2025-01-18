import os
from dotenv import load_dotenv
from github import Github



load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
github = Github(GITHUB_TOKEN)


def fetch_repo_files(repo_name):
    repo = github.get_repo(repo_name)
    contents = repo.get_contents("")
    files = []
    
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "file":
            files.append(file_content)
        elif file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
    
    return files


def extract_code_snippets(files):
    code_snippets = []
    for file in files:
        if file.name.endswith((".py", ".js", ".java", ".jsx", ".json", ".c", ".go", ".ipynb")):  # Adjust extensions as needed
            content = file.decoded_content.decode("utf-8")
            code_snippets.append(content[:5000])  # Limit snippet size to avoid token overflow
    return code_snippets