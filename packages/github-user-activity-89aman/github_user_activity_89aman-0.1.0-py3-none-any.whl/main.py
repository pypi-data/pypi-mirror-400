import requests
import sys

def fetch(uname):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/users/{uname}/events/public"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)


map_eve = {
    "CreateEvent": "Created repository",
    "PushEvent": "Pushed commits to",
    "WatchEvent": "Starred",
    "IssueCommentEvent": "Commented on issue in",
    "PullRequestEvent": "Closed pull request in"
}


def main():
    if len(sys.argv) < 2:
        print("Usage: github-user-activity <username>")
        sys.exit(1)

    uname = sys.argv[1]
    events = fetch(uname)

    for e in events:
        t = e.get("type")
        if t in map_eve:
            print(f"- {map_eve[t]} {e.get('repo', {}).get('name')}")


if __name__ == "__main__":
    main()


[project]
name = "github-user-activity"
version = "0.1.0"
description = "A CLI tool to fetch and display GitHub user activity"
authors = [{name = "Your Name", email = "your@email.com"}]