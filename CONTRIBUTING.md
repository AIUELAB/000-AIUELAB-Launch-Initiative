# Contributing

Thanks for considering contributing!

## Setup

- Python 3.11+
- `python3 -m venv venv && source venv/bin/activate`
- `pip install -r requirements.txt`
- `pre-commit install`

## Development

- Run `make format lint type coverage` before pushing
- Write tests for new features (`tests/`)
- Keep functions small and well-typed

## Commit

- Prefer Conventional Commits style (feat:, fix:, chore:, docs:, refactor:)

## PR

- Include a short summary and screenshots/logs if helpful
- Ensure CI is green
