def git_rep(person):
    import requests
    import json
    service = f"https://api.github.com/users/{person}/repos"
    req = requests.get(f"{service}")
    if req.ok:
        path = f"{person}_reps.json"
        with open(path, "w") as f:
            json.dump(req.json(), f, indent=2)


git_rep("AD-Nikolaev")