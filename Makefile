install:
	poetry install

build:
	rm -rf dist
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

lint:
	poetry run flake8 page_loader
	poetry run mypy page_loader

pytest:
	poetry run pytest -vv

cover:
	poetry run pytest --cov=page_loader tests/ --cov-report xml
