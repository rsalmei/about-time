.PHONY: build

# coverage related
SRC = about_time
COV = --cov=$(SRC) --cov-branch --cov-report=term-missing

all:
	@grep -E "^\w+:" makefile | cut -d: -f1

clean-python: clean-build clean-pyc

clean-build:
	rm -rf build dist

clean-pyc:
	find . -type f -name *.pyc -delete

build-python: clean-python
	python setup.py sdist bdist_wheel

build: build-python

release-python: build-python
	twine upload dist/*

release: release-python

test:
	pytest $(COV)

ptw:
	ptw -- $(COV)

cov-report:
	coverage report -m
