#!/usr/bin/env -S uv run --script --quiet

# /// script
# dependencies = ["nox",]
# ///

import os
import shlex
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import nox

package = "dapla_metadata"
python_versions = ["3.10", "3.11", "3.12", "3.13", "3.14"]
nox.needs_version = ">= 2021.6.6"
nox.options.default_venv_backend = "uv"


def install_with_uv(
    session: nox.Session,
    *,
    groups: list[str] | None = None,
    only_groups: list[str] | None = None,
    all_extras: bool = False,
    locked: bool = True,
) -> None:
    """Install packages using uv, pinned to uv.lock."""
    cmd = ["uv", "sync", "--no-default-groups"]
    if locked:
        cmd.append("--locked")
    if groups:
        for group in groups:
            cmd.extend(["--group", group])
    if only_groups:
        for group in only_groups or []:
            cmd.extend(["--only-group", group])
    if all_extras:
        cmd.append("--all-extras")
    cmd.append(
        f"--python={session.virtualenv.location}"
    )  # Target the nox venv's Python interpreter
    session.run_install(
        *cmd, env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    )

@nox.session(name="pre-commit", python=python_versions[-1])
def precommit(session: nox.Session) -> None:
    """Lint using pre-commit."""
    install_with_uv(session, only_groups=["dev"])
    args = session.posargs or [
        "run",
        "--all-files",
        "--hook-stage=manual",
        "--show-diff-on-failure",
    ]
    session.run("pre-commit", *args)


@nox.session(python=python_versions[1:])
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    install_with_uv(session, groups=["type_check"])
    args = session.posargs or ["src", "tests"]
    session.run("mypy", *args)
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


@nox.session(python=python_versions)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    install_with_uv(session, groups=["test"])
    try:
        session.run(
            "coverage",
            "run",
            "--parallel",
            "-m",
            "pytest",
            "-o",
            "pythonpath=",
            *session.posargs,
        )
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(python=python_versions[-1], default=False)
def coverage(session: nox.Session) -> None:
    """Produce the coverage report."""
    install_with_uv(session, only_groups=["test"])
    args = session.posargs or ["report", "--skip-empty"]
    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@nox.session(python=python_versions[-1])
def typeguard(session: nox.Session) -> None:
    """Runtime type checking using Typeguard."""
    install_with_uv(session, groups=["test"])
    session.run("pytest", f"--typeguard-packages={package}.datasets", *session.posargs)


@nox.session(python=python_versions[-1])
def xdoctest(session: nox.Session) -> None:
    """Run examples with xdoctest."""
    install_with_uv(session, groups=["test"])
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if "FORCE_COLOR" in os.environ:
            args.append("--colored=1")
    session.run("python", "-m", "xdoctest", *args)


@nox.session(name="docs-build", python=python_versions[-1])
def docs_build(session: nox.Session) -> None:
    """Build the documentation."""
    install_with_uv(session, groups=["docs"])
    args = session.posargs or ["docs", "docs/_build"]
    if not session.posargs and "FORCE_COLOR" in os.environ:
        args.insert(0, "--color")
    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-build", *args)


@nox.session(python=python_versions[-1], default=False)
def docs(session: nox.Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    install_with_uv(session, only_groups=["docs"])
    args = session.posargs or ["--open-browser", "docs", "docs/_build"]
    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)


if __name__ == "__main__":
    nox.main()
