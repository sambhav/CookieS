import json
import logging
import os
import shlex
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from functools import lru_cache, partial
from io import StringIO
from pathlib import Path
from subprocess import PIPE, STDOUT, CalledProcessError
from typing import Any, Dict, List, Optional, Union

import requests
from cookiecutter.environment import StrictEnvironment
from cookiecutter.generate import apply_overwrites_to_context
from cookiecutter.main import cookiecutter
from cookiecutter.prompt import render_variable
from cryptography.fernet import Fernet
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from github import Github, GithubException
from pydantic import BaseModel

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# APPLICATION CONSTANTS
# Remote name for the Github repository to be create.
# Note: We don't use origin to avoid clashes if the cookiecutter
# itself sets up some git configs.
CC_ORIGIN = "cc-origin"
GITHUB_URL = "github.com"
GITHUB_API_URL = "https://api.github.com"


# USER CONFIG
# Github API host name. Useful for GHE usage.
HOST_NAME = os.environ.get("WEB_CC_GITHUB_HOST_NAME", "")
# Github base url. Useful for GHE usage.
BASE_URL = os.environ.get("WEB_CC_GITHUB_BASE_URL", GITHUB_URL)
# See https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/
# On how to create an OAuth app
# Github OAuth App Client ID.
CLIENT_ID = os.environ.get("WEB_CC_OAUTH_CLIENT_ID")
# Github OAuth App Client Secret.
CLIENT_SECRET = os.environ.get("WEB_CC_OAUTH_CLIENT_SECRET")
# A secret key generated via Fernet.generate_key().decode()
# Please replace the default one below to ensure that the
# tokens are passed securely between the frontend and the
# backend.
APP_KEY = os.environ.get(
    "WEB_CC_APP_KEY", "6BkMvztw_O1tEaspovyOWHHk-yWhYZoL25YHWlhXRq4="
)
CC_CONFIG_PATH = Path(__file__).absolute().parent / ".cookiecutterrc"

logger = logging.getLogger()


def encrypt_token(token: str):
    return Fernet(APP_KEY).encrypt(token.encode()).decode()


@lru_cache(maxsize=1024)
def decrypt_token(token: str):
    return Fernet(APP_KEY).decrypt(token.encode()).decode()


from cookiecutter import hooks

from server.patched_run_script import run_script as patched_run_script

hooks.run_script = patched_run_script

## Common Github utilities ##


@lru_cache()
def get_git_client(token: str, encrypted=True):
    """Returns a Github client"""
    if BASE_URL == GITHUB_URL:
        host_name = GITHUB_API_URL
    else:
        host_name = f"https://{BASE_URL}/api/v3"
    host_name = HOST_NAME or host_name
    token = decrypt_token(token) if encrypted else token
    return Github(base_url=host_name, login_or_token=token)


@lru_cache()
def get_current_user(token):
    """Returns the PyGithub object representing the role account used for CC creation."""
    client = get_git_client(token)
    name = client.get_user().login
    return client.get_user(name)


## Initial user input gathering stage ##


@app.get("/cookicutters")
def get_cookicutters():
    """REST end point to fetch the list of supported cookiecutter.

    Returns a map of cookiecutter repo names in `org/repo` format.
    If the repository has nested cookiecutter in subdirectories, it
    also returns a list of subdirectories which can be used. Otherwise
    each key is associated with an empty list.
    """
    return {
        "cookiecutters": {
            "audreyr/cookiecutter-pypackage": []
        }
    }


@app.get("/oauth-url")
def get_oauth():
    """REST end point to get the Github OAuth endpoint."""
    return {
        "url": f"https://{BASE_URL}/login/oauth/authorize"
        f"?client_id={CLIENT_ID}&scope=public_repo,read:org"
    }


@app.get("/oauth-token/{code}")
def get_token(code: str):
    """REST end point to fetch the list of supported cookiecutter.

    Returns a map of cookiecutter repo names in `org/repo` format.
    If the repository has nested cookiecutter in subdirectories, it
    also returns a list of subdirectories which can be used. Otherwise
    each key is associated with an empty list.
    """
    response = requests.post(
        f"https://{BASE_URL}/login/oauth/access_token",
        data={"code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
        headers={"Accept": "application/json"},
    )
    data = response.json()
    token = encrypt_token(data["access_token"])
    return {"token": token}


def validate_org(org_name: str, token: str):
    """Validates if the user provided organization is a valid target to create the repository."""
    client = get_git_client(token)
    user = get_current_user(token)
    if org_name == user.login:
        return ""
    try:
        org = client.get_organization(org_name)
    except GithubException:
        return "Please enter a valid organization"
    is_member = org.has_in_members(user)
    if not is_member:
        return (
            f"{user.login} is not a member of the '{org_name}' organization."
            f" Please invite {user.login} to this organization to continue."
        )
    if not org.members_can_create_repositories:
        return "This organization does not allow members to create repositories."
    return ""


def validate_repo(org_name: str, repo_name: str, token: str):
    """Validates if the user provided organization is a valid target to create the repository."""
    client = get_git_client(token)
    try:
        repo = client.get_repo(f"{org_name}/{repo_name}")
    except GithubException:
        return ""
    else:
        # This method returns None if the git repo is empty
        # It is an easy an inexpensive way to check for empty
        # github repos
        if repo.get_stats_contributors() is not None:
            return "This repository already exists and has commits. Please choose an empty or non-existent repository."
        return ""


@app.get("/validate/{org_name}/{repo_name}")
def validate(org_name: str, repo_name: str, token: str):
    """Validates the user provided organization and repository.

    If the role account doesn't have access to the user-specified
    organization or if it doesn't exist, this end point returns an
    error with an appropriate message.
    """
    org_response = validate_org(org_name, token)
    repo_response = ""
    if not org_response:
        repo_response = validate_repo(org_name, repo_name, token)
    return {"org": org_response, "repo": repo_response}


## Cookie cutter creation stage ##


class Template(BaseModel):
    repo: str = "audreyr/cookiecutter-pypackage"
    directory: str = ""


class FormDetails(BaseModel):
    template: Template = Template()
    org: str
    repo: str
    cc_context: Dict[str, Any] = {}
    token: str
    user_inputs: Dict[str, Any] = {}
    next_key: Optional[str] = None
    next_value: Optional[Union[str, List[str]]] = None
    done: bool = False
    has_defaults = False
    base_url = BASE_URL

### Interactive form endpoint ###


@app.post("/form")
def form(details: FormDetails):
    """Iterative end-point for determining cookiecutter user input fields.

    Currently only supports `string` or `list` values in `cookiecutter.json`.
    It also searches the user provides organization for a set of defaults for
    a cookiecutter.

    The defaults are searched for in {user_org}/.github/{cc_name}/cookiecutter.json.

    The end point iteratively asks for the next set of inputs via `next_key` and `next_value`.
    """
    if not details.cc_context:
        details.cc_context, details.has_defaults = get_config(
            details.template.repo,
            details.template.directory,
            details.org,
            details.token,
        )
    details.next_key, details.next_value, details.done = get_next_option(
        details.cc_context, details.user_inputs
    )
    return details


def get_config(repo_name, directory, user_org, token):
    """Fetches the cookiecutter input template and the user defaults stored in Github."""
    client = get_git_client(token)
    cc_repo = client.get_repo(repo_name)
    config_file_path = "cookiecutter.json"
    if directory:
        config_file_path = os.path.join(directory, config_file_path)
    context = json.loads(cc_repo.get_contents(config_file_path).decoded_content)
    try:
        config_repo = client.get_repo(f"{user_org}/.github")
    except GithubException:
        return context, False
    user_config = os.path.join("cookiecutter", repo_name, config_file_path)
    try:
        user_defaults = json.loads(
            config_repo.get_contents(user_config).decoded_content
        )
    except Exception:
        return context, False
    else:
        apply_overwrites_to_context(context, user_defaults)
    return context, True


def get_next_option(cc_context, user_inputs):
    """Parses the cookiecutter template and current context and determines the input to be requested."""
    context = {}
    context["cookiecutter"] = cc_context
    env = StrictEnvironment(context=context)
    for key in context["cookiecutter"]:
        if key == "_variables":
            continue
        if key not in user_inputs:
            raw_value = context["cookiecutter"][key]
            if key.startswith("_") and not key.endswith("__"):
                user_inputs[key] = render_variable(env, raw_value, user_inputs)
                continue
            variable_info = render_variable(
                env, cc_context.get("_variables", {}).get(key, {}), user_inputs
            )
            if variable_info.get("skip", "False").lower() == "true":
                rendered_value = render_variable(env, raw_value, user_inputs)
                if isinstance(rendered_value, list):
                    rendered_value = rendered_value[0]
                user_inputs[key] = rendered_value
                continue
            if not isinstance(raw_value, dict):
                rendered_value = render_variable(env, raw_value, user_inputs)
                return key, rendered_value or "", False
    return None, None, True


### Creationg end point ###


@app.post("/create")
def create(details: FormDetails):
    """The actual end point for cookiecutter creation.

    Takes in the final FormDetails object once "/form" end-point sets
    the `details.done` flag to true. All the values from `details.user_inputs`
    are passed to cookiecutter for generation and the output folder is uploaded
    to Github at the provided org and repository.
    """
    try:
        return validate_and_create(details)
    except CalledProcessError as error:
        logger.exception("Error occured: %s", error)
        raise HTTPException(
            status_code=500, detail=f"Error Occured:\n\n{error.stdout.decode()}"
        )
    except Exception as error:
        logger.exception("Error occured: %s", error)
        raise HTTPException(status_code=500, detail=f"Error Occured: {error}")


def validate_and_create(details: FormDetails):
    """Validates the final form inputs and creates the user repo from cookiecutter."""
    missing_values = set(
        key for key in details.cc_context if not key.startswith("_")
    ) - set(details.user_inputs)
    if missing_values:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid user input. Missing inputs for: {missing_values}",
        )
    with tempfile.TemporaryDirectory(prefix="cookiecutter") as temp_dir:
        client = get_git_client(details.token)
        user = client.get_user()
        try:
            if user.login == details.org:
                user.create_repo(details.repo)
            else:
                client.get_organization(details.org).create_repo(details.repo)
        except GithubException:
            pass

        output = StringIO()
        with redirect_stdout(output):
            cookiecutter(
                f"https://{user.login}:{decrypt_token(details.token)}@{BASE_URL}/{details.template.repo}",
                directory=details.template.directory,
                no_input=True,
                extra_context=details.user_inputs,
                overwrite_if_exists=True,
                output_dir=temp_dir,
                config_file=CC_CONFIG_PATH,
            )
        temp_dir_path = Path(temp_dir)
        output_dir = list(temp_dir_path.iterdir())[0]
        shell_command = partial(
            subprocess.run,
            shell=True,
            check=True,
            cwd=output_dir,
            stdout=PIPE,
            stderr=STDOUT,
        )
        shell_command("git init")
        shell_command(f"git config --local user.name {user.name}")
        shell_command(f"git config --local user.email {user.email}")
        url = (
            f"https://{user.login}:{decrypt_token(details.token)}@"
            f"{BASE_URL}/{shlex.quote(details.org)}/{shlex.quote(details.repo)}"
        )
        shell_command(f"git remote add {CC_ORIGIN} {url}")
        shell_command("git add .")
        shell_command(
            f"git commit -m 'Initialize repository with CC: {details.template.repo}'"
        )
        shell_command(f"git push {CC_ORIGIN} master")
        return {
            "url": f"https://{BASE_URL}/{shlex.quote(details.org)}/{shlex.quote(details.repo)}",
            "output": output.getvalue(),
        }
