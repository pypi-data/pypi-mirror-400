import subprocess


def get_token(*, domain: str, owner: str, region: str):
    result = subprocess.run(
        [
            "aws",
            "codeartifact",
            "get-authorization-token",
            "--domain",
            domain,
            "--domain-owner",
            owner,
            "--region",
            region,
            "--query",
            "authorizationToken",
            "--output",
            "text",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_url(*, domain: str, owner: str, region: str, repo: str):
    return f"https://{domain}-{owner}.d.codeartifact.{region}.amazonaws.com/pypi/{repo}/simple/"


def get_auth_url(*, domain: str, owner: str, region: str, repo: str) -> str:
    token = get_token(domain=domain, owner=owner, region=region)
    return f"https://aws:{token}@{domain}-{owner}.d.codeartifact.{region}.amazonaws.com/pypi/{repo}/simple/"
