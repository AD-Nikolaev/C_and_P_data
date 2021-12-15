def git_rep(person):
    import requests
    import json
    service = f"https://api.github.com/users/{person}/repos"
    req = requests.get(f'{service}')
    data = json.loads(req.text)
    name_reps = [data[n]['name'] for n in range(len(data))]
    return name_reps


print(git_rep(input("Type person : ")))