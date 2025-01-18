import os
import re
import streamlit as st
from dotenv import load_dotenv
from github import Github
from streamlit_agraph import agraph, Node, Edge, Config
from gemini import generate_ai_description_with_gemini
import pandas as pd
import plotly.figure_factory as ff
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
github = Github(GITHUB_TOKEN)

# Fetch repository files
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

# Extract code snippets from the files
def extract_code_snippets(files):
    code_snippets = []
    for file in files:
        if file.name.endswith((".py", ".js", ".java", ".jsx", ".json", ".c", ".go", ".ipynb")):  # Adjust extensions as needed
            content = file.decoded_content.decode("utf-8")
            code_snippets.append(content[:5000])  # Limit snippet size to avoid token overflow
    return code_snippets

# Extract function names using regex (customize for different languages)
def extract_function_names(code):
    function_names = []
    
    # Regex patterns for various language functions
    patterns = [
        r"def (\w+)\(",  # Python function definition
        r"function (\w+)\(",  # JavaScript function definition
        r"public\s+[\w<>\[\]]+\s+(\w+)\(",  # Java function definition
        r"(\w+)\s*=\s*function\s*\(",  # JS anonymous function
        r"func (\w+)\(",  # Go function definition
        r"fun (\w+)\(",  # Kotlin function definition
        r"fun (\w+)\s*\(",  # Dart function definition
        r"^\s*def\s+(\w+)\s*\(",  # Python function definition (indented code in Jupyter)
        r"(\w+)\s*\(\)\s*{",  # JSX function definition (React function component)
        r"const\s+(\w+)\s*=\s*\(\)\s*=>\s*{",  # JSX arrow function definition (React)
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, code)
        function_names.extend(matches)
    
    return function_names

# Generate graph from code snippets
def generate_code_graph(code_snippets):
    nodes = []
    edges = []
    
    for snippet in code_snippets:
        function_names = extract_function_names(snippet)  # Extract function names
        
        for function in function_names:
            nodes.append(Node(id=function, label=function))  # Add each function as a node
        
        # Example logic to generate edges (if you have related functions, you can customize this)
        for i in range(len(function_names)-1):
            edges.append(Edge(source=function_names[i], target=function_names[i+1]))  # Create an edge between functions
    
    return nodes, edges

# Function to fetch repo details and commit data
def fetch_repo_details(repo_name):
    repo = github.get_repo(repo_name)
    commits = repo.get_commits()
    description = repo.description
    commit_dates = [commit.commit.author.date for commit in commits]
    
    return {
        "name": repo_name,
        "description": description,
        "commit_count": commits.totalCount,
        "commit_dates": commit_dates,
        "ai_description": ai_description,  # Adding AI-generated description
        "code_snippets": code_snippets  # Including code snippets
    }

# Plot commit activity
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def plot_commit_dates(commit_dates):
    # Convert commit dates to pandas datetime format
    dates = pd.to_datetime(commit_dates)
    
    # Count the number of commits per day
    counts = dates.value_counts().sort_index()
    
    # Prepare data for the plot
    days = counts.index.strftime('%Y-%m-%d').to_list()  # Format dates as strings
    commits_per_day = counts.values.tolist()

    # Create a bar plot using Plotly
    fig = go.Figure()

    # Add bar trace for commits per day
    fig.add_trace(go.Bar(
        x=days,
        y=commits_per_day,
        name="Commits",
        marker_color='blue'
    ))

    # Update layout to improve appearance
    fig.update_layout(
        title="Commit Activity Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Commits",
        showlegend=False,
        xaxis_tickangle=45,
        barmode='group'
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Streamlit UI
st.title("GitHub Repository Summarizer")
repo_name = st.text_input("Enter the GitHub Repository (owner/repo):")

if repo_name:
    with st.spinner("Fetching repository details..."):
        try:
            # Fetch repo details and extract code snippets
            files = fetch_repo_files(repo_name)
            code_snippets = extract_code_snippets(files)  # Extract code snippets from files
            ai_description = generate_ai_description_with_gemini(code_snippets)  # AI-generated description
            details = fetch_repo_details(repo_name)  # Get repo details including commits
            
            # Displaying repository details
            st.write(f"### Repository: {details['name']}")
            st.write(f"**Total Commits:** {details['commit_count']}")
            
            # Visualize code snippets graph
            st.write("### Code Snippets Graph")
            nodes, edges = generate_code_graph(code_snippets)  # Generate graph from code snippets
            
            # Define the configuration for rendering the graph
            config = Config(
                        width=750,
                        height=950,
                        directed=True,
                        physics=True,
                        hierarchical=False,
                        nodes={
                            "font": {
                                "color": "white"  # Set node font color to white
                            }
                        },
                        edges={
                            "font": {
                                "color": "white"  # Set edge font color to white
                            }
                        }
                    )

            
            # Display the graph in Streamlit
            agraph(nodes=nodes, edges=edges, config=config)
            
            st.write("### Code Description")
            st.write(f"{details['ai_description']}")
            
            # Commit activity graph
            st.write("### Commit Activity")
            plot_commit_dates(details['commit_dates'])
            
            
            
        except Exception as e:
            st.error(f"Error fetching repository details: {e}")
