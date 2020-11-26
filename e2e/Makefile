SHELL := /bin/bash
########################################################################################################################
##
## app e2e tests
##
########################################################################################################################
pwd := ${PWD}
dirname := $(notdir $(patsubst %/,%,$(CURDIR)))
activate = poetry run

list:
	@grep '^[^#[:space:]].*:' Makefile

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

install:
	poetry install


test:
	$(activate) pytest

coverage:
	rm -f ../reports/e2e.xml  > /dev/null || true
	$(activate) coverage run --source ./ --module pytest -rxs -v --junit-xml=../reports/e2e.xml --ignore .venv || true
	@if [[ ! -f ../reports/e2e.xml ]]; then echo report not created; exit 1; fi