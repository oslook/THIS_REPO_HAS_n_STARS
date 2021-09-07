
query='''
query ($login: String!, $repo: String!) {
  repositoryOwner(login: $login) {
    login
    repository(name: $repo) {
      createdAt
      forks(first: 10, orderBy: {field: CREATED_AT, direction: DESC}) {
        nodes {
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
              email
            }
          }
        }
        pageInfo {
          endCursor
          hasNextPage
        }
      }
      stargazerCount
      stargazers(first: 10, orderBy: {field: STARRED_AT, direction: DESC}) {
        nodes {
          name
          createdAt
          avatarUrl(size: 64)
          login
          url
          email
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

param={
  "login": "",
  "repo": "",
}
