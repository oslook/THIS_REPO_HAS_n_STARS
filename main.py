#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import time
import json
import requests
import copy

headers = {
    "User-Agent": "Awesome-Octocat-App"
}

def forks():
    query = '''
    query ($login: String!, $repo: String!) {
        repositoryOwner(login: $login) {
            repository(name: $repo) {
                forks(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
                    edges {
                    starredAt
                    node {
                        name
                        createdAt
                        nameWithOwner
                        owner {
                            ... on User {
                            name
                            createdAt
                            avatarUrl(size: 64)
                            login
                            url
                            }
                        }
                    }
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    
                }
            }
        }
    }
    '''

def get_stars(login, repo_info):
    query = '''
    query ($login: String!, $repo: String!) {
    repositoryOwner(login: $login) {
        repository(name: $repo) {
        stargazerCount
        stargazers(first: 100, orderBy: {field: STARRED_AT, direction: DESC}) {
            edges {
            starredAt
            node {
            name
            createdAt
            avatarUrl(size: 64)
            login
            url
            }
            }
            pageInfo {
            endCursor
            hasNextPage
            }
        }
        }
    }
    }
    '''

    queryAfter = '''
    query ($login: String!, $repo: String!, $after String!) {
    repositoryOwner(login: $login) {
        repository(name: $repo) {
        stargazerCount
        stargazers(first: 100, orderBy: {field: STARRED_AT, direction: DESC}, after: $after) {
            edges {
            starredAt
            node {
            name
            createdAt
            avatarUrl(size: 64)
            login
            url
            }
            }
            pageInfo {
            endCursor
            hasNextPage
            }
        }
        }
    }
    }
    '''

    param = {
        "login": login,
        "repo": repo_info['name'],
    }

    stars = []
    try:
        while True:
            res = requests.post('https://api.github.com/graphql',
                                headers=headers, json={"query": query, "variables": param})
            t = json.loads(res.text)
            if "errors" in t:
                print("get stars errors:", t)
                break
            stars += t['data']['repositoryOwner']['repository']['stargazers']['edges']

            # next
            if not t['data']['repositoryOwner']['repository']['stargazers']['pageInfo']['hasNextPage']:
                break
            query=queryAfter
            param['after']=t['data']['repositoryOwner']['repository']['stargazers']['pageInfo']['endCursor']
            print(param)
    except Exception as e:
        print("get stars", e)
        # {'data': None, 'errors': [{'message': 'Something went wrong while executing your query. This may be the result of a timeout, or it could be a GitHub bug. Please include `A192:7CFA:EB2D34:1B4927F:611B5598` when reporting this issue.'}]}
    return stars


def update(id, name):
    query = '''
    mutation ($repositoryId: ID!, $repoName: String!) {
    __typename
    updateRepository(input: {repositoryId: $repositoryId, name: $repoName}) {
        repository {
        name
        id
        }
    }
    }
    '''

    param = {
        "repositoryId": id,
        "repoName": name,
    }

    try:
        res = requests.post('https://api.github.com/graphql',
                            headers=headers, json={"query": query, "variables": param})
        t = json.loads(res.text)
        print(t)
        return t['data']
    except Exception as e:
        print("update", e)
        # {'data': None, 'errors': [{'message': 'Something went wrong while executing your query. This may be the result of a timeout, or it could be a GitHub bug. Please include `A192:7CFA:EB2D34:1B4927F:611B5598` when reporting this issue.'}]}
        return None



def get_repo_info(login, repo):
    query = '''
query ($login: String! $repo: String!) {
  repository(name: $repo, owner: $login) {
    id
    name
  }
}
'''
    param = {
        "login": login,
        "repo": repo
    }

    try:
        res = requests.post('https://api.github.com/graphql',
                            headers=headers, json={"query": query, "variables": param})
        t = json.loads(res.text)
        if "errors" in t:
            print("get_repo_info errors:", t)
        print(t)
        return t['data']['repository']
    except Exception as e:
        print("get_repo_id", e)
        # {'data': None, 'errors': [{'message': 'Something went wrong while executing your query. This may be the result of a timeout, or it could be a GitHub bug. Please include `A192:7CFA:EB2D34:1B4927F:611B5598` when reporting this issue.'}]}
        return None

def readme(stars):
    with open("README_en.md", 'w') as f:
        f.write("# THIS REPO HAS %d STARS ⭐️\n\n[【English】](./README_en.md) [【中文】](./README.md)\n\n" % (len(stars)))
        if stars:
            f.write("[%s](%s) helped me count the %dnd star, thank you!\n\n" % (stars[0]['node']['login'], stars[0]['node']['url'], len(stars)))
            f.write("## Stars\n\n")
            f.write('| Stars | Avatar | starredAt |\n')
            f.write('| -----: |-----: | -----: |\n')
            for n in stars:
                i = n['node']
                f.write("| [%s](%s) | <img src=\"%s\" alt=\"drawing\" width=\"64\"/> | %s |\n" % (i['login'], i['url'], i['avatarUrl'], n['starredAt']))
        f.write('\n## Contribs \n<a><img src="https://contrib.rocks/image?repo=oslook/THIS_REPO_HAS_%d_STARS&max=1000&columns=16" width="720"/></a>\n' % (len(stars)))
        f.write("## Want to contribute?\n\nClicking the star will trigger the commit which includes the clicker's name to the contributors list. So CLICK THE STAR!")
    with open("README.md", 'w') as f:
        f.write("# 这个仓库有 %d个 星标 ⭐️\n\n[【English】](./README_en.md) [【中文】](./README.md)\n\n" % (len(stars)))
        if stars:
            f.write("感谢 [%s](%s) 帮我做了第 %d 个星标!\n\n" % (stars[0]['node']['login'], stars[0]['node']['url'], len(stars)))
            f.write("## Stars\n\n")
            f.write('| 用户 | 头像 | 星标时间 |\n')
            f.write('| -----: |-----: | -----: |\n')
            for n in stars:
                i = n['node']
                f.write("| [%s](%s) | <img src=\"%s\" alt=\"drawing\" width=\"64\"/> | %s |\n" % (i['login'], i['url'], i['avatarUrl'], n['starredAt']))
        f.write('\n## 贡献者\n<a><img src="https://contrib.rocks/image?repo=oslook/THIS_REPO_HAS_%d_STARS&max=1000&columns=16" width="720"/> </a>\n' % (len(stars)))
        f.write("## 你想试试吗?\n\n. 请点击上面的 star 按钮!")
    with open("/tmp/user.txt", 'w') as f:
        if stars:
            f.write("%s %d" % (stars[0]['node']['login'], len(stars)))
    
if __name__ == "__main__":
    # args > 1 for processing
    if len(sys.argv) > 2:
        token = sys.argv[1]
        login = sys.argv[2].split("/")[0]
        repo = sys.argv[2].split("/")[1]
        if token:
            headers['Authorization'] = 'token ' + token

        start_time = time.time()      
        repo_info = get_repo_info(login, repo)
        print(repo_info)
        if len(sys.argv) > 3:
            count = sys.argv[3]
            update(repo_info['id'], "THIS_REPO_HAS_%s_STARS" % count)
        else:
            stars = get_stars(login, repo_info)
            print("stars", [i['node']['login'] for i in stars])
            readme(stars)

