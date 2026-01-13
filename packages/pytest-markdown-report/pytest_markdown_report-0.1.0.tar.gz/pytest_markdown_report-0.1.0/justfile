# Justfile Rules:
# - Errors should not pass silently without good reason
# - Only use `2>/dev/null` for probing (checking exit status when command has no quiet option)
# - Only use `|| true` to continue after expected failures (required with `set -e`)
# Enable bash tracing (set -x) for all recipes. Usage: just trace=true <recipe>

trace := "false"

# List available recipes
help:
    @just --list --unsorted

# Full development workflow
[no-exit-message]
dev: format check test

# Run test suite
[no-exit-message]
test *ARGS:
    #!{{ bash_prolog }}
    sync
    pytest {{ ARGS }}

# Format, check with complexity disabled, test
[no-exit-message]
lint: format
    #!{{ bash_prolog }}
    sync
    show "# ruff check"
    safe ruff check -q --ignore=C901

    show "# docformatter -c"
    safe docformatter -c src tests
    show "# mypy"
    safe mypy
    show "# pytest"
    safe pytest -q
    end-safe

# Check code style
[no-exit-message]
check:
    #!{{ bash_prolog }}
    sync
    show "# ruff check"
    safe ruff check -q
    show "# docformatter -c"
    safe docformatter -c src tests
    show "# mypy"
    safe mypy
    end-safe

# Format code
format:
    #!{{ bash_prolog }}
    sync
    tmpfile=$(mktemp tmp-fmt-XXXXXX)
    trap "rm $tmpfile" EXIT
    patch-and-print() {
        patch "$@" | sed -Ene "/^patching file '/s/^[^']+'([^']+)'/\\1/p"
    }
    ruff check -q --fix-only --diff | patch-and-print >> "$tmpfile" || true
    ruff format -q --diff | patch-and-print >> "$tmpfile" || true
    # docformatter --diff applies the change *and* outputs the diff, so we need to
    # reverse the patch (-R) and dry run (-C), and it prefixes the path with before and
    # after (-p1 ignores the first component of the path). Hence `patch -RCp1`.
    docformatter --diff src tests | patch-and-print -RCp1 >> "$tmpfile" || true
    # Markdown formatting disabled for the moment.
    # Must find replacement for dprint that handles backticks correctly.
    modified=$(sort --unique < "$tmpfile")
    if [ -n "$modified" ] ; then
        bold=$'\033[1m'; nobold=$'\033[22m'
        red=$'\033[31m'; resetfg=$'\033[39m'
        echo "${bold}${red}**Reformatted files:**"
        echo "$modified" | sed "s|^|${bold}${red}  - ${nobold}${resetfg}|"
    fi

# Create release: tag, build tarball, upload to PyPI and GitHub
# Use --dry-run to perform local changes and verify external permissions without publishing

# Use --rollback to revert local changes from a crashed dry-run
[no-exit-message]
release *ARGS: _fail_if_claudecode dev
    #!{{ bash_prolog }}
    DRY_RUN=false
    ROLLBACK=false
    BUMP=patch
    # Parse flags and positional args
    for arg in {{ ARGS }}; do
        case "$arg" in
            --dry-run) DRY_RUN=true ;;
            --rollback) ROLLBACK=true ;;
            --*) fail "Error: unknown option: $arg" ;;
            *) [[ -n "${positional:-}" ]] && fail "Error: too many arguments"
               positional=$arg ;;
        esac
    done
    [[ -n "${positional:-}" ]] && BUMP=$positional

    # Cleanup function: revert commit and remove build artifacts
    cleanup_release() {
        local initial_head=$1
        local initial_branch=$2
        local version=$3
        visible git reset --hard "$initial_head"
        if [[ -n "$initial_branch" ]]; then
            visible git checkout "$initial_branch"
        else
            visible git checkout "$initial_head"
        fi

        # Remove only this version's build artifacts
        if [[ -n "$version" ]] && [[ -d dist ]]; then
            find dist -name "*${version}*" -delete
            [[ -d dist ]] && [[ -z "$(ls -A dist)" ]] && visible rmdir dist
        fi
    }

    # Rollback mode
    if [[ "$ROLLBACK" == "true" ]]; then
        # Check if there's a release commit at HEAD
        if git log -1 --format=%s | grep -q "🔖 Release"; then
            # Verify no permanent changes (commit not pushed to remote)
            # Skip check if HEAD is detached or has no upstream
            if git symbolic-ref -q HEAD >/dev/null && git rev-parse --abbrev-ref @{u} >/dev/null 2>&1; then
                # We're on a branch with upstream - check if release commit is unpushed
                if ! git log @{u}.. --oneline | grep -q "🔖 Release"; then
                    fail "Error: release commit already pushed to remote"
                fi
            fi

            version=$(git log -1 --format=%s | grep -oP '(?<=Release ).*')
            current_branch=$(git symbolic-ref -q --short HEAD || echo "")
            cleanup_release "HEAD~1" "$current_branch" "$version"
            echo "${GREEN}✓${NORMAL} Rollback complete"
        else
            fail "No release commit found"
        fi
        exit 0
    fi

    # Check preconditions
    git diff --quiet HEAD || fail "Error: uncommitted changes"
    current_branch=$(git symbolic-ref -q --short HEAD || echo "")
    [[ -z "$current_branch" ]] && fail "Error: not on a branch (HEAD is detached)"
    main_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
    [[ "$current_branch" != "$main_branch" ]] && fail "Error: must be on $main_branch branch (currently on $current_branch)"
    release=$(uv version --bump "$BUMP" --dry-run)
    tag="v$(echo "$release" | awk '{print $NF}')"
    git rev-parse "$tag" >/dev/null 2>&1 && fail "Error: tag $tag already exists"

    # Interactive confirmation (skip in dry-run)
    if [[ "$DRY_RUN" == "false" ]]; then
        while read -re -p "Release $release? [y/n] " answer; do
            case "$answer" in
                y|Y) break;;
                n|N) exit 1;;
                *) continue;;
            esac
        done
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        INITIAL_HEAD=$(git rev-parse HEAD)
        INITIAL_BRANCH=$(git symbolic-ref -q --short HEAD || echo "")
        trap 'cleanup_release "$INITIAL_HEAD" "$INITIAL_BRANCH" "${version:-}"; exit 1' ERR EXIT
    fi

    # Perform local changes: version bump, commit, build
    visible uv version --bump "$BUMP"
    version=$(uv version)
    git add pyproject.toml uv.lock
    visible git commit -m "🔖 Release $version"
    tag="v$(uv version --short)"
    visible uv build

    if [[ "$DRY_RUN" == "true" ]]; then
        # Verify external permissions
        git push --dry-run || fail "Error: cannot push to git remote"
        [[ -z "${UV_PUBLISH_TOKEN:-}" ]] && fail "Error: UV_PUBLISH_TOKEN not set. Get token from https://pypi.org/manage/account/token/"
        uv publish --dry-run dist/* || fail "Error: cannot publish to PyPI"
        gh auth status >/dev/null 2>&1 || fail "Error: not authenticated with GitHub"

        echo ""
        echo "${GREEN}✓${NORMAL} Dry-run complete: $version"
        echo "  ${GREEN}✓${NORMAL} Git push permitted"
        echo "  ${GREEN}✓${NORMAL} PyPI publish permitted"
        echo "  ${GREEN}✓${NORMAL} GitHub release permitted"

        # Normal cleanup
        trap - ERR EXIT
        cleanup_release "$INITIAL_HEAD" "$INITIAL_BRANCH" "$version"
        echo ""
        echo "Run: ${COMMAND}just release $BUMP${NORMAL}"
        exit 0
    fi

    # Perform external actions
    visible git push
    visible git tag -a "$tag" -m "Release $version"
    visible git push origin "$tag"
    visible uv publish
    visible gh release create "$tag" --title "$version" --generate-notes
    echo "${GREEN}✓${NORMAL} Release $tag complete"

# Bash prolog
[private]
bash_prolog := \
    ( if trace == "true" { "/usr/bin/env bash -xeuo pipefail" } \
    else { "/usr/bin/env bash -euo pipefail" } ) + "\n" + '''
COMMAND="''' + style('command') + '''"
ERROR="''' + style('error') + '''"
GREEN=$'\033[32m'
NORMAL="''' + NORMAL + '''"
safe () { "$@" || status=false; }
end-safe () { ${status:-true}; }
show () { echo "$COMMAND$*$NORMAL"; }
visible () { show "$@"; "$@"; }
fail () { echo "${ERROR}$*${NORMAL}"; exit 1; }

# Use direct venv binaries when in Claude Code sandbox
# (uv run crashes on system config access)
sandboxed=$(test -w /tmp && echo "false" || echo "true")
sync() { if ! $sandboxed; then uv sync -q "$@"; fi; }
define_env_cmd () { if $sandboxed; then eval "$1() { .venv/bin/$1 \"\$@\"; }"; else eval "$1() { uv run $1 \"\$@\"; }"; fi; }
define_env_cmd pytest
define_env_cmd ruff
define_env_cmd mypy
define_env_cmd claudeutils
'''

# Fail if CLAUDECODE is set
[no-exit-message]
[private]
_fail_if_claudecode:
    #!{{ bash_prolog }}
    if [ "${CLAUDECODE:-}" != "" ]; then
        echo -e '{{ style("error") }}⛔️ Denied: use agent recipes{{ NORMAL }}'
        exit 1
    fi
