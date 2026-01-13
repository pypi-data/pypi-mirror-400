import nox

nox.options.python = "3.11"
nox.options.default_venv_backend = "uv"


@nox.session(python=["3.11"], tags=["lint"])
def lint(session):
    session.install("ruff")
    session.run("uv", "run", "ruff", "check")
    session.run("uv", "run", "ruff", "format")


@nox.session(python=["3.11", "3.12", "3.13"], tags=["mypy"])
def mypy(session):
    session.install(".")
    session.install("mypy", "types-psutil")
    session.run("uv", "run", "mypy", "src")


@nox.session(python=["3.11", "3.12", "3.13"], tags=["pytest"])
def pytest(session):
    session.install(".")
    session.install("pytest")
    test_files = ["test.py"]
    session.run("uv", "run", "pytest", *test_files)
