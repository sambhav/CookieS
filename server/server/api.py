import json
import os
import shlex
import subprocess
import tempfile
from functools import lru_cache, partial
from logging import error
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from cookiecutter.environment import StrictEnvironment
from cookiecutter.generate import apply_overwrites_to_context
from cookiecutter.main import cookiecutter
from cookiecutter.prompt import render_variable
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
# Token for the role account. Note: This is a secret value
# and should not be checked in.
TOKEN = os.environ.get("WEB_CC_TOKEN")
# Github API host name. Useful for GHE usage.
HOST_NAME = os.environ.get("WEB_CC_GITHUB_HOST_NAME", "")
# Github base url. Useful for GHE usage.
BASE_URL = os.environ.get("WEB_CC_GITHUB_BASE_URL", GITHUB_URL)
# Role account username for use by the backend.
BOT_NAME = os.environ.get("WEB_CC_BOT_NAME", "samj1912")
# Role account email for use by the backend.
# Will be used to create commits.
BOT_MAIL = os.environ.get("WEB_CC_BOT_MAIL", "sambhavs.email@gmail.com")


## Common Github utilities ##


@lru_cache()
def get_git_client():
    """Returns a Github client"""
    if BASE_URL == GITHUB_URL:
        host_name = GITHUB_API_URL
    else:
        host_name = f"https://{BASE_URL}/api/v3"
    host_name = HOST_NAME or host_name
    return Github(base_url=host_name, login_or_token=TOKEN)


@lru_cache()
def get_current_user():
    """Returns the PyGithub object representing the role account used for CC creation."""
    client = get_git_client()
    return client.get_user(BOT_NAME)


## Initial user input gathering stage ##


@app.get("/cookicutters")
def get_cookicutters():
    """REST end point to fetch the list of supported cookiecutter.

    Returns a map of cookiecutter repo names in `org/repo` format.
    If the repository has nested cookiecutter in subdirectories, it
    also returns a list of subdirectories which can be used. Otherwise
    each key is associated with an empty list.
    """
    return {"cookiecutters": {"audreyr/cookiecutter-pypackage": [],}}


def validate_org(org_name: str):
    """Validates if the user provided organization is a valid target to create the repository."""
    client = get_git_client()
    try:
        org = client.get_organization(org_name)
    except GithubException:
        return "Please enter a valid organization"
    is_member = org.has_in_members(get_current_user())
    if not is_member:
        return (
            f"{BOT_NAME} is not a member of the '{org_name}' organization."
            f" Please invite {BOT_NAME} to this organization to continue."
        )
    if not org.members_can_create_repositories:
        return "This organization does not allow members to create repositories."
    return ""


@app.get("/validate/{org_name}/{repo_name}")
def validate(org_name: str, repo_name: str):
    """Validates the user provided organization and repository.

    If the role account doesn't have access to the user-specified
    organization or if it doesn't exist, this end point returns an
    error with an appropriate message.
    """
    org_response = validate_org(org_name)
    return {"org": org_response}


## Cookie cutter creation stage ##


class Template(BaseModel):
    repo: str = "audreyr/cookiecutter-pypackage"
    directory: str = ""


class FormDetails(BaseModel):
    template: Template = Template()
    org: str
    repo: str
    cc_context: Dict[str, Any] = {}
    user_inputs: Dict[str, Any] = {}
    next_key: Optional[str] = None
    next_value: Optional[Union[str, List[str]]] = None
    done: bool = False


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
        details.cc_context = get_config(
            details.template.repo, details.template.directory, details.org
        )
    details.next_key, details.next_value, details.done = get_next_option(
        details.cc_context, details.user_inputs
    )
    return details


def get_config(repo_name, directory, user_org):
    """Fetches the cookiecutter input template and the user defaults stored in Github."""
    client = get_git_client()
    cc_repo = client.get_repo(repo_name)
    config_file_path = "cookiecutter.json"
    if directory:
        config_file_path = os.path.join(directory, config_file_path)
    context = json.loads(cc_repo.get_contents(config_file_path).decoded_content)
    try:
        config_repo = client.get_repo(f"{user_org}/.github")
    except GithubException:
        return context
    user_config = os.path.join("cookiecutter", repo_name, config_file_path)
    try:
        user_defaults = json.loads(
            config_repo.get_contents(user_config).decoded_content
        )
        apply_overwrites_to_context(context, user_defaults)
    except GithubException:
        pass
    return context


def get_next_option(cc_context, user_inputs):
    """Parses the cookiecutter template and current context and determines the input to be requested."""
    context = {}
    context["cookiecutter"] = cc_context
    env = StrictEnvironment(context=context)

    for key in context["cookiecutter"]:
        if key not in user_inputs:
            rendered_value = render_variable(
                env, context["cookiecutter"][key], user_inputs
            )
            return key, rendered_value, False
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
    except BaseException as error:
        raise HTTPException(status_code=500, detail=f"Error Occured: {error}")


def validate_and_create(details: FormDetails):
    """Validates the final form inputs and creates the user repo from cookiecutter."""
    missing_values = set(details.cc_context) - set(details.user_inputs)
    if missing_values:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid user input. Missing inputs for: {missing_values}",
        )
    with tempfile.TemporaryDirectory(prefix="cookiecutter") as temp_dir:
        client = get_git_client()
        try:
            client.get_organization(details.org).create_repo(details.repo)
        except GithubException:
            pass
        cookiecutter(
            f"https://{BASE_URL}/{details.template.repo}",
            directory=details.template.directory,
            no_input=True,
            extra_context=details.user_inputs,
            overwrite_if_exists=True,
            output_dir=temp_dir,
        )
        temp_dir_path = Path(temp_dir)
        output_dir = list(temp_dir_path.iterdir())[0]
        shell_command = partial(subprocess.run, shell=True, check=True, cwd=output_dir)
        shell_command("git init")
        shell_command(f"git config --local user.name {BOT_NAME}")
        shell_command(f"git config --local user.email {BOT_MAIL}")
        shell_command(
            f"git remote add {CC_ORIGIN} https://{BOT_NAME}:{TOKEN}@{BASE_URL}/{shlex.quote(details.org)}/{shlex.quote(details.repo)}"
        )
        shell_command("git add .")
        shell_command(
            f"git commit -m 'Initialize repository with CC: {details.template.repo}'"
        )
        shell_command(f"git push {CC_ORIGIN} master -f")
