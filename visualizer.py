import os
import subprocess
import xml.etree.ElementTree as ET
from graphviz import Digraph

def parse_config(config_path):
    tree = ET.parse(config_path)
    root = tree.getroot()
    return {
        "visualizerPath": root.find("visualizerPath").text,
        "repositoryPath": root.find("repositoryPath").text,
        "outputFile": root.find("outputFile").text,
        "startDate": root.find("startDate").text,
    }

def get_git_commits(repo_path, start_date):
    command = [
        "git", "-C", repo_path, "log", f"--after={start_date}",
        "--pretty=format:%h|%p|%s"
    ] #git -C <repo_path> log --after=<start_date> --pretty=format:%h|%p|%s

    result = subprocess.run(command, capture_output=True, text=True, check=True)
    commits = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("|")
        commits.append({
            "hash": parts[0],
            "parents": parts[1].split() if parts[1] else [],
            "message": parts[2]
        })
    return commits

def build_graph(commits):
    graph = Digraph(format="png")
    for commit in commits:
        graph.node(commit["hash"], label=commit["message"])
        for parent in commit["parents"]:
            graph.edge(parent, commit["hash"])
    return graph

def save_graph(graph, output_path):
    graph.render(output_path, cleanup=True)

def main(config_path):
    config = parse_config(config_path)
    repo_path = config["repositoryPath"]
    start_date = config["startDate"]
    output_file = config["outputFile"]

    commits = get_git_commits(repo_path, start_date)
    graph = build_graph(commits)
    save_graph(graph, output_file)
    print("Graph dependencies visualization completed successfully.")

if __name__ == "__main__": #python visualizer.py config.xml
    import argparse

    parser = argparse.ArgumentParser(description="Git Dependencies Visualizer")
    parser.add_argument("config", help="Path to the XML configuration file")
    args = parser.parse_args() #args = Namespace(config="config.xml")

    main(args.config)
