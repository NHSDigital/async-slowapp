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
	rm -r ../reports  > /dev/null || true
	$(activate) coverage run --source ./ --module pytest -rxs -v --junit-xml=../reports/e2e.xml --ignore .venv
#	$(activate) coverage html ; mv htmlcov/* reports/coverage/html
#	$(activate) coverage xml ; mv coverage.xml reports/coverage/xml