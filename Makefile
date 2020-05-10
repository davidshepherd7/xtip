install:
	poetry install

poetry-check:
	poetry check

typecheck:
	poetry run mypy xtip/ tests/

test:
	poetry run pytest tests/

black:
	black xtip/ tests/

build: black typecheck test poetry-check
	poetry build

publish: build
	# Check that git is clean
	git diff --exit-code
	git diff --cached --exit-code

	poetry publish
