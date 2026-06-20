.PHONY: build check lint test

override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

check:
	"$(ROOT)/scripts/check-baseline.sh"

lint: check

test: check

build: check
