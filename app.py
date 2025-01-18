import streamlit as st
from github import Github
import pandas as pd
import matplotlib.pyplot as plt
from files import fetch_repo_files, extract_code_snippets
from gemini import generate_ai_description_with_gemini
import os
from dotenv import load_dotenv
from streamlit_agraph import agraph

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
github = Github(GITHUB_TOKEN)

def fetch_repo_details(repo_name):
    repo = github.get_repo(repo_name)
    commits = repo.get_commits()
    description = repo.description
    commit_dates = [commit.commit.author.date for commit in commits]
    
    # Generate AI description with Gemini
    code_snippets = extract_code_snippets(fetch_repo_files(repo_name))  # Fetch and extract code snippets
    ai_description = generate_ai_description_with_gemini(code_snippets)  # AI-generated description
    
    return {
        "name": repo_name,
        "description": description,
        "commit_count": commits.totalCount,
        "commit_dates": commit_dates,
        "ai_description": ai_description,  # Adding AI-generated description
        "code_snippets": code_snippets  # Including code snippets
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

# Create a graph based on code snippets or AI description
def generate_code_graph(code_snippets):
    nodes = []
    edges = []
    
    # Assuming code_snippets contains functions or classes in the repository
    for snippet in code_snippets:
        nodes.append({'id': snippet['function_name'], 'label': snippet['function_name']})
        for related_function in snippet['related_functions']:
            edges.append({'from': snippet['function_name'], 'to': related_function})
    
    return {'nodes': nodes, 'edges': edges}

# Streamlit UI
st.title("GitHub Repository Summarizer")
repo_name = st.text_input("Enter the GitHub Repository (owner/repo):")

if repo_name:
    with st.spinner("Fetching repository details..."):
        try:
            details = fetch_repo_details(repo_name)
            
            # Displaying repository details
            st.write(f"### Repository: {details['name']}")
            st.write(f"**Total Commits:** {details['commit_count']}")
            st.write(f"Repo Description: **{details['description']}**")
            st.write(f"**AI-Generated Description:** {details['ai_description']}")
            
            # Commit activity graph
            st.write("### Commit Activity")
            plot_commit_dates(details['commit_dates'])
            
            # Visualize code snippets graph
            st.write("### Code Snippets Graph")
            code_graph = generate_code_graph(details['code_snippets'])
            agraph(graph=code_graph)
            
        except Exception as e:
            st.error(f"Error fetching repository details: {e}")
