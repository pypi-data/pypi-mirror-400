import requests
import os
import sys
import argparse

gh_token = os.environ.get('GITHUB_TOKEN')
if not gh_token:
    print("❌ Error: GITHUB_TOKEN is missing.")
    print("Make sure to set it as an env variable or pass it in your workflow via 'env: GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}'")
    sys.exit(1)

gh_headers = {'accept': 'application/vnd.github.v3+json', 'authorization': f'token {gh_token}'}
VALID_STATUS = ['identical', 'ahead']

def fetch_data(url):
    response = requests.get(url, headers=gh_headers)
    if response.status_code not in (200,404):
        print(f"❌ Error: Unable to fetch data from {url}. Status code: {response.status_code}")
        sys.exit(1)
    return response.json()

def compare_with_refs(repo, sha, ref_type):
    refs = fetch_data(f'https://api.github.com/repos/{repo}/{ref_type}')
    for ref in refs:
        ref_name = ref.get('name')
        compare = fetch_data(f'https://api.github.com/repos/{repo}/compare/{sha}...{ref_name}')
        if compare.get('status') in VALID_STATUS:
            return True
    return False

def read_workflows(path='.github/workflows'):
    actions = []
    for file in os.listdir(path):
        if file.endswith(('.yml', '.yaml')):
            with open(os.path.join(path, file)) as f:
                for line in f:
                    if 'uses:' in line and not line.strip().startswith('#'):
                        use = line.split('uses:')[1].strip()
                        if '@' in use:
                            repo, sha = use.split('@')
                            if len(sha.split()[0]) == 40:
                                actions.append((repo, sha.split()[0], file))
    return actions

def run_scan(actions, mode):
    anomalies = []
    for repo, sha, file in actions:
        print(f"Checking repo: {repo}, SHA: {sha}, Workflow file: {file}")
        if mode == 'default':
            default_branch = fetch_data(f'https://api.github.com/repos/{repo}').get('default_branch')
            if not compare_with_refs(repo, sha, f'compare/{sha}...{default_branch}'):
                anomalies.append((repo, sha, file))
        elif mode in ['branches', 'tags']:
            if not compare_with_refs(repo, sha, mode):
                anomalies.append((repo, sha, file))
        else:
            if not (compare_with_refs(repo, sha, 'branches') or compare_with_refs(repo, sha, 'tags')):
                anomalies.append((repo, sha, file))
    return anomalies

def cli():
    parser = argparse.ArgumentParser(description="WTFork: Detect Fork Network exploits.")
    parser.add_argument('--path', type=str, default='.github/workflows', help='Path to the GitHub workflows directory.')
    parser.add_argument('--mode', type=str, choices=['default', 'branches', 'tags', 'all'], default='all',
                        help='Comparison mode: default branch, all branches, all tags, or all of them.')
    args = parser.parse_args()
    actions = read_workflows(args.path)
    anomalies = run_scan(actions, args.mode)
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    if anomalies:
        print(f"\n{RED}{BOLD}🚨 POTENTIAL FORK NETWORK EXPLOITS DETECTED!{RESET}")
        print(f"{RED}The following actions are pinned to SHAs that do NOT exist in their origin repo:{RESET}\n")

        for repo, sha, file in anomalies:
            print(f"  ❌ {BOLD}{repo}{RESET}")
            print(f"     ├── {YELLOW}SHA:{RESET}  {RED}{sha}{RESET}")
            print(f"     └── {YELLOW}File:{RESET} {file}\n")
        sys.exit(1)

    else:
        print(f"\n{GREEN}{BOLD}✅ All pinned actions reference valid commits in their respective repositories.{RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    cli()