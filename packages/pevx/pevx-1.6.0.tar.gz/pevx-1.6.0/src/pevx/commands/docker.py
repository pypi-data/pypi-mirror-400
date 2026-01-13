import os
import subprocess
from pathlib import Path

import click


@click.command("docker", context_settings={"ignore_unknown_options": True})
@click.option("--secret-id", default="aws_credentials", show_default=True)
@click.option(
    "--output",
    default="/tmp/.aws/credentials",
    help="Path to write credentials file.",
    show_default=True,
)
@click.option("--aws-access-key-id", default=None, show_default=False)
@click.option("--aws-secret-access-key", default=None, show_default=False)
@click.option("--aws-session-token", default=None, show_default=False)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def docker_proxy(
    secret_id: str,
    output: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: str,
    args: list[str],
):
    """
    Proxy any docker commands by mounting aws credentials.
    """
    env = os.environ.copy()
    aws_access_key_id = aws_access_key_id or env["AWS_ACCESS_KEY_ID"]
    aws_secret_access_key = aws_secret_access_key or env["AWS_SECRET_ACCESS_KEY"]
    aws_session_token = aws_session_token or env["AWS_SESSION_TOKEN"]

    if not aws_access_key_id or not aws_secret_access_key:
        raise click.ClickException("AWS Credentials are not set from neither environment nor args")
    else:
        env["AWS_ACCESS_KEY_ID"] = aws_access_key_id
        env["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key
        env["AWS_SESSION_TOKEN"] = aws_session_token

    # Ensure directory exists
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)

    content = [
        "[default]",
        f"aws_access_key_id={aws_access_key_id}",
        f"aws_secret_access_key={aws_secret_access_key}",
    ]
    if aws_session_token:
        content.append(f"aws_session_token={aws_session_token}")

    path.write_text("\n".join(content) + "\n")
    click.echo(f"=== Wrote AWS credentials to {output} ===")

    # Execute docker command with secret
    env["DOCKER_BUILDKIT"] = "1"
    docker_cmd = ["docker"] + list(args) + ["--secret", f"id={secret_id},src={output}"]
    subprocess.run(docker_cmd, check=True, env=env)

    # Remove the AWS credentials directory
    path.unlink(missing_ok=True)
    click.echo(f"=== Removed {output} ===")
