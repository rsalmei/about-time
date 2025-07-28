cov := "--cov=about_time --cov-branch --cov-report=term-missing"

all:
    @just --list

install:
    pip install -r requirements/dev.txt -r requirements/test.txt -e .

clean: clean-build clean-pyc

clean-build:
    rm -rf build dist about_time.egg-info

clean-pyc:
    find . -type f -name *.pyc -delete

lint:
    ruff check about_time --line-length 100

build: lint clean
    python -m build

release: build && tag
    twine upload dist/*

tag:
    #!/usr/bin/env zsh
    tag=$(python -c 'import about_time; print(f"v{about_time.__version__}")')
    git tag -a $tag -m "Details: https://github.com/rsalmei/about-time#changelog-highlights"
    git push origin $tag

test:
    pytest {{ cov }}

ptw:
    ptw -- {{ cov }}

cov-report:
    coverage report -m
