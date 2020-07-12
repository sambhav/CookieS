import json
from logging import error
import os
import shlex
import subprocess
import tempfile
from functools import lru_cache, partial
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

TOKEN = "d101fe08dc7a2745fe99ed51ade203de8039989c"
HOST_NAME = ""
BASE_URL = "github.com"
CC_ORIGIN = "cc-origin"
BOT_NAME = "samj1912"
BOT_MAIL = "cc-creator@creator.cc"


@lru_cache()
def get_git_client():
    host_name = HOST_NAME or "https://api.github.com"
    return Github(base_url=host_name, login_or_token=TOKEN)


@lru_cache()
def get_current_user():
    client = get_git_client()
    return client.get_user(BOT_NAME)


def get_config(repo_name, directory, user_org):
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
    user_config = os.path.join(repo_name, config_file_path)
    try:
        user_defaults = json.loads(
            config_repo.get_contents(user_config).decoded_content
        )
        apply_overwrites_to_context(context, user_defaults)
    except GithubException:
        pass
    return context


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


def get_next_option(cc_context, user_inputs):
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


def validate_and_create(details: FormDetails):
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


@app.get("/cookicutters")
def get_cookicutters():
    return {
        "cookiecutters": {
            "audreyr/cookiecutter-pypackage": [],
        }
    }


def validate_org(org_name: str):
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
    org_response = validate_org(org_name)
    return {"org": org_response}


@app.post("/form")
def form(details: FormDetails):
    if not details.cc_context:
        details.cc_context = get_config(
            details.template.repo, details.template.directory, details.org
        )
    details.next_key, details.next_value, details.done = get_next_option(
        details.cc_context, details.user_inputs
    )
    return details


@app.post("/create")
def create(details: FormDetails):
    try:
        return validate_and_create(details)
    except BaseException as error:
        raise HTTPException(status_code=500, detail=f"Error Occured: {error}")
