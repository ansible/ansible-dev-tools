# ruff: noqa: I002

"""A prototype MCP server for ansible-dev-tools."""

import asyncio
import json
import logging

from pathlib import Path

from fastmcp import FastMCP
from fastmcp.utilities.logging import configure_logging
from pydantic import JsonValue


# Initialize FastMCP server
logger = logging.getLogger(__name__)
configure_logging(level=logging.DEBUG, logger=logger)
mcp: FastMCP[str] = FastMCP("ansible-dev-tools")


common_navigator_params = [
    "--dc=false",
    "--ee=false",
    "--format=json",
    "--mode=stdout",
    "--pp=never",
]


async def subprocess_run(cmd: list[str]) -> tuple[int | None, str, str]:
    """Run a subprocess using asyncio.

    Args:
        cmd: The command to run as a list of strings.

    Returns:
        A tuple containing the return code, stdout, and stderr of the command.
    """
    logger.info("Running command: %s", " ".join(cmd))
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return_code = process.returncode
    str_stdout = stdout.decode("utf-8")
    str_stderr = stderr.decode("utf-8")
    if return_code != 0:
        logger.error("Command: %s", " ".join(cmd))
        logger.error("Command failed with return code: %s", return_code)
        logger.error("Stderr: %s", str_stderr)
        logger.error("Stdout: %s", str_stdout)
    return return_code, str_stdout, str_stderr


@mcp.tool()
async def ansible_collections_list() -> JsonValue:
    """List all the installed ansible collections.

    Returns:
        Dictionary containing the result of the ansible-navigator collections command
    """
    cmd = ["uv", "run", "ansible-navigator", "collections", *common_navigator_params]
    return_code, stdout, stderr = await subprocess_run(cmd)
    return json.loads(stdout) if return_code == 0 else {"error": stderr}


@mcp.tool()
async def ansible_run_playbook(name: str) -> JsonValue:
    """Run ansible playbook and return the result.

    Args:
        name: The name of the ansible playbook to run.

    Returns:
        Dictionary containing the result of the ansible playbook run
    """
    filename = Path("./.cache/ansible-navigator-artifact.json")
    cmd = [
        "uv",
        "run",
        "ansible-navigator",
        "run",
        name,
        "--pae=True",
        "--pas",
        str(filename),
        "--ll=debug",
        "--la=false",
        "--lf=./.cache/ansible-navigator.log",
        *common_navigator_params,
    ]

    # Run the command and capture output
    _return_code, _stdout, _stderr = await subprocess_run(cmd)

    contents = filename.read_text(encoding="utf-8") if filename.exists() else ""

    return json.loads(contents) if contents else {"error": "No output"}


@mcp.tool()
async def ansible_execution_environments_list() -> JsonValue:
    """List all the available execution environments.

    Returns:
        Dictionary containing the result of the ansible-navigator images command
    """
    # Run the command and capture output
    cmd = [
        "uv",
        "run",
        "ansible-navigator",
        "images",
        *common_navigator_params,
    ]
    return_code, stdout, stderr = await subprocess_run(cmd)
    return json.loads(stdout) if return_code == 0 else {"error": stderr}


@mcp.tool()
async def ansible_install_collection(name: str) -> JsonValue:
    """Install an ansible collection.

    Args:
        name: Name of the ansible collection to install.

    Returns:
        Dictionary containing the result of the ansible collection installation
    """
    cmd = ["uv", "run", "ade", "install", name, "-vvv"]

    return_code, stdout, stderr = await subprocess_run(cmd)

    return {"result": stdout} if return_code == 0 else {"error": stderr}


@mcp.tool()
async def ansible_doc(name: str = "", kind: str = "") -> JsonValue:
    """Return documentation for an ansible plugin or role.

    Args:
        name: Name of the ansible plugin or role.
        kind: Type of the ansible plugin (e.g., module, role, etc.).

    Returns:
        Dictionary containing the result of the ansible-doc command
    """
    cmd = [
        "uv",
        "run",
        "ansible-navigator",
        "doc",
        name,
        "--type",
        kind,
        *common_navigator_params,
        "--",
        "--json",
    ]

    # Run the command and capture output
    return_code, stdout, stderr = await subprocess_run(cmd)

    return json.loads(stdout) if return_code == 0 else {"error": stderr}


@mcp.tool()
async def ansible_lint(fix: bool = False) -> JsonValue:  # noqa: FBT001, FBT002
    """Run ansible-lint check on the provided playbook or role.

    Args:
        fix: If True, run ansible-lint with the --fix option.

    Returns:
        Dictionary containing the result of the ansible-lint command
    """
    # Command to run ansible-lint with validated inputs
    cmd = [
        "uv",
        "run",
        "ansible-lint",
        "--nocolor",
        "--format=json",
    ]
    if fix:
        cmd.append("--fix")

    # Run the command asynchronously and capture output
    return_code, stdout, stderr = await subprocess_run(cmd)

    if return_code == 0:
        return {"output": "ansible-lint found no issues"}

    try:
        response = json.loads(stdout) if stdout else stderr
    except json.JSONDecodeError:
        response = stderr

    return {"output": response}


class Mcp:
    """MCP server class."""

    def run(self) -> None:
        """Run the MCP server."""
        mcp.run()


if __name__ == "__main__":
    mcp.run()
