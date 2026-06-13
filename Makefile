.PHONY: build check lint test

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

check:
	"$(ROOT)/scripts/check-baseline.sh"

lint: check

test: check

build: check
