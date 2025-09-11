# Setup

Follow the given instructions to set up the project.

## Prerequisites

Install the following tools before setting up the project:

- [pyenv]
- [uv] (via `make uv`)
- [git]

## Setting up the repository
```bash
git clone https://github.com/jakemingolla/calendar-condenser.git
cd calendar-condenser
```

Run `make help` to see the available commands.

## Install python and dependencies
```bash
pyenv install
```

```bash
uv venv
source .venv/bin/activate
uv sync --frozen
```

## Set up environment variables
```bash
cp .env.example .env
```

Edit the `.env` file to set the appropriate environment variables, like your OpenAI API key.

## Test the application is working

In one terminal, run the following command to start the application:
```
make dev
```

In the other terminal, check the API is up and running:
```bash
curl http://localhost:8000/
```

<!-- References -->
[pyenv]: https://github.com/pyenv/pyenv
[uv]: https://github.com/astral-sh/uv
[git]: https://git-scm.com/
