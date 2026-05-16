.PHONY: help init inspect check test contract-test integration-test component-test e2e-test lint run image image-test repo-check check-profile check-handoff check-tooling check-mcp doctor

help:
	@printf '%s\n' \
	  'Targets:' \
	  '  make init              inspect and bootstrap from evidence' \
	  '  make inspect           print compact repository evidence' \
	  '  make check             run repository checks' \
	  '  make repo-check        validate template contract' \
	  '  make check-profile     validate PROJECT_PROFILE.toon' \
	  '  make check-handoff     validate HANDOFF.toon' \
	  '  make doctor            concise readiness report'

init:
	@scripts/bootstrap-project

inspect:
	@scripts/inspect-project

check: repo-check check-profile check-handoff check-tooling check-mcp

repo-check:
	@scripts/check-repo-contract

check-profile:
	@scripts/check-project-profile

check-handoff:
	@scripts/check-handoff

check-tooling:
	@scripts/check-tooling

check-mcp:
	@scripts/check-mcp

doctor:
	@scripts/doctor

test contract-test integration-test component-test e2e-test lint run image image-test:
	@printf '%s\n\n' 'ERROR'
	@printf '%s\n\n' '$@ harness not specialised'
	@printf '%s\n' 'next:' '  make init'
	@printf '%s\n' 'project state:' '  testing.harness = unspecialised'
	@exit 2
