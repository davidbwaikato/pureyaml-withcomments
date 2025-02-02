.PHONY: clean clean-build clean-pyc clean-test clean-docs lint test tox tox-slow coverage coverage github docs builddocs servedocs release dist install develop register requirements sync

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

BROWSER 		:= python -c "$$BROWSER_PYSCRIPT"
DOCSBUILDDIR	= docs/_build
DOCSSOURCEDIR	= docs/source
PYPI			= https://pypi.python.org/simple/

help:
	@echo "clean       		remove all build, test, coverage and Python artifacts"
	@echo "clean-build 		remove build artifacts"
	@echo "clean-pyc   		remove Python file artifacts"
	@echo "clean-test  		remove test and coverage artifacts"
	@echo "clean-docs  		remove autogenerated docs files"
	@echo "lint        		check style with flake8"
	@echo "test        		run tests quickly with the default Python"
	@echo "tox    			run tests on every Python version with tox"
	@echo "tox-slow    		run tests on every Python version with tox"
	@echo "coverage    		check code coverage quickly with the default Python"
	@echo "github      		generate github's docs (i.e. README)"
	@echo "docs        		generate Sphinx HTML documentation, including API docs"
	@echo "servedocs   		semi-live edit docs"
	@echo "release     		package and upload a release"
	@echo "dist        		package"
	@echo "install     		install the package to the active Python's site-packages"
	@echo "develop     		install package in edit mode"
	@echo "register    		update pypi"
	@echo "requirements		update and install requirements"
	@echo "sync        		sync requirements with pip"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr $(DOCSBUILDDIR)/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr .htmlcov/

clean-docs:
	rm -f $(DOCSSOURCEDIR)/pureyaml.rst
	rm -f $(DOCSSOURCEDIR)/modules.rst
	$(MAKE) -C docs clean

lint:
	flake8 pureyaml tests

test: lint
	python setup.py test

tox: lint
	tox -e py26 -i $(PIP_INDEX_URL) & \
	tox -e py27 -i $(PIP_INDEX_URL) & \
	tox -e py33 -i $(PIP_INDEX_URL) & \
	tox -e py34 -i $(PIP_INDEX_URL) & \
	tox -e py35 -i $(PIP_INDEX_URL) & \
	tox -e pypy -i $(PIP_INDEX_URL) & \
	tox -e docs -i $(PIP_INDEX_URL) & \
	wait

tox-slow: lint
	tox -i $(PIP_INDEX_URL)

coverage:
	coverage run setup.py test
	coverage report
	coverage html
	$(BROWSER) .htmlcov/index.html
	$(MAKE) -C docs coverage

github:
	python docs/github_docs.py
	rst-lint README-orig.rst

docs: clean-docs builddocs github

builddocs:
	# add --no-headings if your adding them manually
	sphinx-apidoc \
		--private \
		--no-toc \
		--module-first \
		--follow-links \
		--output-dir=$(DOCSSOURCEDIR)/ pureyaml
	$(MAKE) -C docs html

servedocs: docs
	$(BROWSER) $(DOCSBUILDDIR)/html/index.html
	watchmedo shell-command \
		--pattern '*.rst;*.py' \
		--command '$(MAKE) builddocs' \
		--ignore-pattern '$(DOCSBUILDDIR)/*;$(DOCSSOURCEDIR)/pureyaml.rst' \
		--ignore-directories \
		--recursive

release: clean docs
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean docs
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean
	python setup.py install

develop: clean
	python setup.py develop

register:
	python setup.py register

requirements:
	pip install --quiet --upgrade setuptools pip wheel pip-tools
	pip-compile --no-index requirements_dev.in > /dev/null
	pip-compile --no-index requirements.in > /dev/null
	pip wheel -r requirements_dev.txt --quiet &
	pip-sync requirements_dev.txt > /dev/null
	git diff requirements.txt requirements_dev.txt 2>&1 | tee .requirements.diff

sync:
	pip install --quiet --upgrade pip-tools
	pip-sync requirements_dev.txt > /dev/null
