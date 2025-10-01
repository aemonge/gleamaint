# Gleamaint

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Functional Programming](https://img.shields.io/badge/paradigm-functional-brightgreen.svg)](https://en.wikipedia.org/wiki/Functional_programming)
[![Powered by LLMs](https://img.shields.io/badge/powered%20by-LLMs-orange.svg)](https://openai.com/)

> **Python static analysis for enforcing Gleam-compatible functional programming
> patterns**

Gleamaint is an LLM-powered linter that analyzes Python codebases to ensure
compatibility with [Gleam](https://gleam.run/)'s functional programming principles. It
enforces immutability, Result types, pattern matching, and actor-based concurrency
patterns to create migration-ready Python code.

## Overview

Gleamaint bridges the gap between Python and Gleam by detecting patterns that prevent
clean translation to Gleam's type system and functional idioms. It provides actionable
guidance to transform imperative Python into functional, concurrent, and type-safe code.

### Key Features

- 🔍 **Deep Code Analysis** - Detects mutations, side effects, exceptions, and
  imperative patterns
- 🎯 **Gleam-Compatible** - Enforces patterns that map directly to Gleam's functional
  idioms
- 🚀 **LLM-Powered** - Uses Claude 3.5 Sonnet for intelligent, context-aware analysis
- 📊 **LSP-Compatible** - JSON diagnostics ready for CI/CD and editor integration
- 🎨 **Beautiful Output** - Professional, colorized terminal reports

## What It Checks

### Errors (Critical Violations)

- **Mutable data structures** - Enforces `pyrsistent` collections (pmap, pvector, pset)
- **Exception handling** - Requires `returns` Result types instead of try/except
- **Class inheritance** - Mandates functional composition over OOP
- **Threading/asyncio** - Requires `Thespian` actors or message passing
- **Global mutable state** - Detects and flags module-level mutations

### Warnings

- Missing Result types on fallible functions
- Missing `@typechecked` runtime validation
- Imperative loops instead of map/filter/reduce
- Missing pattern matching with match/case
- Non-tail recursive functions

## Installation

### Prerequisites

```bash
# Install the LLM CLI tool
pip install llm

# Install OpenRouter plugin
llm install llm-openrouter

# Set your OpenRouter API key
export OPENROUTER_KEY=your_key_here
llm keys set openrouter
```

### Setup

**Add to your Python project's `Makefile`:**

Copy this target directly into your existing Makefile:

```````makefile
.PHONY: it-gleam

it-gleam:
	@files="$(filter-out $@,$(MAKECMDGOALS))"; \
	if [ -z "$$files" ]; then \
		printf '\033[0;33mUsage: make it-gleam <file.py> [file2.py ...]\033[0m\n'; \
		exit 1; \
	fi; \
	total_errors=0; \
	total_warnings=0; \
	for file in $$files; do \
		if [ ! -f "$$file" ]; then \
			printf '\033[0;31m[ERROR] File not found: %s\033[0m\n' "$$file"; \
			continue; \
		fi; \
		printf '\033[0;36mAnalyzing: %s\033[0m\n' "$$file"; \
		raw_output=$$(cat "$$file" | llm \
			--system "$$(curl -s https://raw.githubusercontent.com/aemonge/gleamaint/main/gleamaint.md)" \
			--model openrouter/anthropic/claude-3.5-sonnet \
			--option temperature 0.1 \
			--no-stream \
			"Analyze this Python file. Return ONLY raw JSON array (no markdown blocks) with top 20 violations. Start with [ and end with ]."); \
		violations=$$(echo "$$raw_output" | perl -0777 -pe 's/^``````$$//; s/.*?(\[.*\]).*/$$1/s'); \
		if [ -z "$$violations" ] || [ "$$violations" = "[]" ]; then \
			printf '\033[0;32m[PASS] No violations found\033[0m\n\n'; \
			continue; \
		fi; \
		error_count=$$(echo "$$violations" | jq '[.[] | select(.severity == "Error")] | length' 2>/dev/null || echo "0"); \
		warning_count=$$(echo "$$violations" | jq '[.[] | select(.severity == "Warning")] | length' 2>/dev/null || echo "0"); \
		info_count=$$(echo "$$violations" | jq '[.[] | select(.severity == "Info")] | length' 2>/dev/null || echo "0"); \
		hint_count=$$(echo "$$violations" | jq '[.[] | select(.severity == "Hint")] | length' 2>/dev/null || echo "0"); \
		total_errors=$$((total_errors + error_count)); \
		total_warnings=$$((total_warnings + warning_count)); \
		printf '\n'; \
		echo "$$violations" | jq -r '.[] | if .severity == "Error" then "  \u001b[0;31m[ERROR]\u001b[0m   Line \(.range.start.line): \(.message)" elif .severity == "Warning" then "  \u001b[0;33m[WARN]\u001b[0m    Line \(.range.start.line): \(.message)" elif .severity == "Info" then "  \u001b[0;34m[INFO]\u001b[0m    Line \(.range.start.line): \(.message)" else "  \u001b[0;35m[HINT]\u001b[0m    Line \(.range.start.line): \(.message)" end' 2>/dev/null || printf '\033[0;31m[ERROR] Failed to parse violations\033[0m\n'; \
		printf '\n'; \
		printf '\033[1mSummary:\033[0m \033[0;31mErrors: %s\033[0m | \033[0;33mWarnings: %s\033[0m | \033[0;34mInfo: %s\033[0m | \033[0;35mHints: %s\033[0m\n' "$$error_count" "$$warning_count" "$$info_count" "$$hint_count"; \
		printf '\n'; \
	done; \
	if [ $$total_errors -gt 0 ]; then \
		exit 1; \
	else \
		printf '\033[0;32m\033[1m[PASS] All files passed gleamaint checks\033[0m\n'; \
	fi

# Prevent make from treating filenames as targets
%:
	@:
```````

**That's it!** The linter fetches the prompt directly from GitHub, so no local files
needed.

### Optional: Cache for faster analysis

For frequent use, cache the prompt locally to avoid downloading on each run:

```bash
# Download once
curl -s https://raw.githubusercontent.com/aemonge/gleamaint/main/gleamaint.md -o .gleamaint.md

# Add to .gitignore
echo ".gleamaint.md" >> .gitignore
```

Then modify the Makefile to use local file:

```makefile
--system "$$(cat .gleamaint.md)" \
```

**Update cache when prompt changes:**

```bash
curl -s https://raw.githubusercontent.com/aemonge/gleamaint/main/gleamaint.md -o .gleamaint.md
```

## Usage

### Analyze single file

```bash
make it-gleam src/main.py
```

### Analyze multiple files

```bash
make it-gleam src/main.py src/utils.py src/handlers.py
```

### Example Output

```
Analyzing: src/process_request.py

  [ERROR]   Line 5: Function should return Result type. Use Result[None, str] instead of None
  [ERROR]   Line 18: Use pyrsistent's pmap instead of dict for query parameters
  [WARN]    Line 21: Use pattern matching with match/case instead of if/getattr
  [WARN]    Line 25: Use functional operations (map/reduce) instead of for loop

Summary: Errors: 4 | Warnings: 5 | Info: 1 | Hints: 0
```

### CI/CD Integration

Add to `.gitlab-ci.yml`:

```yaml
gleamaint:
  stage: lint
  image: python:3.11
  before_script:
    - pip install llm llm-openrouter jq
    - llm keys set openrouter $OPENROUTER_KEY
  script:
    - CHANGED_FILES=$(git diff --name-only --diff-filter=AM origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME...HEAD | grep '\.py$' || true)
    - |
      if [ -z "$CHANGED_FILES" ]; then
        echo "✅ No Python files changed"
        exit 0
      fi
    - make it-gleam $CHANGED_FILES
  only:
    refs:
      - merge_requests
    changes:
      - "**/*.py"
  allow_failure: false
```

## Required Libraries

Gleamaint enforces usage of these Python libraries for Gleam compatibility:

```bash
pip install returns sspipe pyrsistent typeguard pyright thespian PyPubSub background tco
```

| Library      | Purpose                                                  | Status         |
| ------------ | -------------------------------------------------------- | -------------- |
| `returns`    | Result/Maybe/IO types for railway-oriented programming   | ✅ Essential   |
| `sspipe`     | Gleam-like pipe operator (`p`, `px`)                     | ✅ Essential   |
| `pyrsistent` | Immutable data structures (pmap, pvector, pset, PRecord) | ✅ Essential   |
| `typeguard`  | Runtime type validation with `@typechecked`              | ✅ Essential   |
| `pyright`    | Static type checking in strict mode                      | ✅ Essential   |
| `Thespian`   | Pure actor model for concurrency                         | ✅ Recommended |
| `PyPubSub`   | Message passing for decoupled communication              | ✅ Recommended |
| `background` | Simple decorator-based background tasks                  | 🟠 Optional    |
| `tco`        | Tail call optimization for recursive functions           | 🟠 Optional    |

## Feature Coverage

| Gleam Feature      | Python Gap          | Our Solution             | Status         |
| ------------------ | ------------------- | ------------------------ | -------------- |
| Result/Error types | Exceptions          | `returns` Result/Ok/Err  | ✅ Better      |
| Immutable data     | Mutable by default  | `pyrsistent` collections | ✅ Solved      |
| Pattern matching   | Limited if/else     | `match/case` with guards | ✅ Solved      |
| Pipe operator      | No native pipes     | `sspipe` operators       | ✅ Solved      |
| Pure functions     | Side effects common | Enforce purity rules     | ✅ Enforced    |
| Actor model        | Threading/async     | `Thespian` actors        | ✅ Solved      |
| Compile-time types | Runtime typing      | `pyright` + `typeguard`  | 🟠 Much Better |
| Tail recursion     | Imperative loops    | `tco` + optimization     | 🟠 Improved    |

## Examples

See the [`examples/`](./examples/) directory for:

- ❌ **Bad**: Traditional Python patterns (violations.py)
- ✅ **Good**: Gleam-compatible functional Python (clean.py)

## Why Gleamaint?

1. **Migration Readiness** - Write Python that can be mechanically translated to Gleam
2. **Better Code Quality** - Functional patterns lead to more testable, maintainable
   code
3. **Type Safety** - Catch errors at compile-time and runtime
4. **Concurrency** - Actor model prevents race conditions and shared state bugs
5. **Future-Proof** - Easy path to BEAM VM's legendary reliability

## Contributing

Contributions welcome! Please:

1. Fork this repository
2. Create a feature branch
3. Submit a PR with examples

## License

MIT License - see [LICENSE](LICENSE) for details

## Credits

- Powered by [Anthropic Claude 3.5 Sonnet](https://www.anthropic.com/claude)
- Built with [Simon Willison's LLM CLI](https://github.com/simonw/llm)
- Inspired by [Gleam](https://gleam.run/)'s elegant functional design

## Links

- [Gleam Documentation](https://gleam.run/documentation/)
- [Python Functional Programming Guide](https://docs.python.org/3/howto/functional.html)
- [returns Library](https://returns.readthedocs.io/)
- [pyrsistent Documentation](https://pyrsistent.readthedocs.io/)

---

**Made with ❤️ for functional programming enthusiasts**
