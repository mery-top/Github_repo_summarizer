import streamlit as st
from github import Github
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
github = Github(GITHUB_TOKEN)


def fetch_repo_details(repo_name):
    repo = github.get_repo(repo_name)
    commits = repo.get_commits()
    description = repo.description
    commit_dates = [commit.commit.author.date for commit in commits ]
    
    
    return{
        "name": repo_name,
        "description": description,
        "commit_count": commits.totalCount,
        "commit_dates": commit_dates
    }
    
def plot_commit_dates(commit_dates):
    dates = pd.to_datetime(commit_dates)
    counts = dates.value_counts().sort_index()
    plt.figure(figsize=(10,5))
    plt.plot(counts.index, counts.values, marker='o', label="Commits")
    plt.xlabel("Date")
    plt.ylabel("Number of Commits")
    plt.title("Commit Activity Over Time")
    plt.grid()
    plt.legend()
    st.pyplot(plt)
    
st.title("GitHub Repository Summarizer")
repo_name = st.text_input("Enter the GitHub Repository (owner/repo):")
    
if repo_name:
    with st.spinner("Fetching repository details..."):
        try:
            details = fetch_repo_details(repo_name)
            st.write(f"### Repository: {details['name']}")
            st.write(f"**Description:** {details['description']}")
            st.write(f"**Total Commits:** {details['commit_count']}")
            st.write("### Commit Activity")
            plot_commit_dates(details['commit_dates'])
        except Exception as e:
            st.error(f"Error fetching repository details: {e}")