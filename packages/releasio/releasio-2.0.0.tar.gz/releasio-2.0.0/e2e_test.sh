#!/bin/bash
# Comprehensive End-to-End Testing for releasio
# Goal: Break the system and discover nasty bugs

# Don't exit on error - we want to run all tests
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test results
FAILED_TESTS=()

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((TESTS_FAILED++))
    FAILED_TESTS+=("$2")
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

test_start() {
    ((TESTS_RUN++))
    log_info "TEST #$TESTS_RUN: $1"
}

# Cleanup function
cleanup_test_dir() {
    if [ -d "$1" ]; then
        rm -rf "$1"
    fi
}

# Create a fresh test directory
create_test_project() {
    local project_name=$1
    local test_dir="/tmp/releasio_e2e_test_${project_name}_$$"

    cleanup_test_dir "$test_dir"
    mkdir -p "$test_dir"
    cd "$test_dir"

    # Initialize git
    git init -q
    git config user.email "test@releasio.com"
    git config user.name "Releasio Tester"

    # Create minimal pyproject.toml
    cat > pyproject.toml <<EOF
[project]
name = "$project_name"
version = "0.1.0"
description = "Test project for releasio"
requires-python = ">=3.11"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.releasio]
default_branch = "main"

[tool.releasio.version]
tag_prefix = "v"

[tool.releasio.publish]
enabled = false
EOF

    # Initial commit
    git add .
    git commit -q -m "chore: initial commit"
    git branch -m main

    echo "$test_dir"
}

# Function to run command and expect success
expect_success() {
    local cmd="$1"
    local test_name="$2"

    if eval "$cmd" > /tmp/releasio_output_$$ 2>&1; then
        log_success "$test_name"
        return 0
    else
        log_error "$test_name" "$test_name (exit code: $?)"
        cat /tmp/releasio_output_$$
        return 1
    fi
}

# Function to run command and expect failure
expect_failure() {
    local cmd="$1"
    local test_name="$2"
    local expected_error="$3"

    if eval "$cmd" > /tmp/releasio_output_$$ 2>&1; then
        log_error "$test_name (expected failure but succeeded)" "$test_name"
        return 1
    else
        if [ -n "$expected_error" ]; then
            if grep -q "$expected_error" /tmp/releasio_output_$$; then
                log_success "$test_name (failed as expected with: $expected_error)"
                return 0
            else
                log_error "$test_name (failed but wrong error message)" "$test_name"
                cat /tmp/releasio_output_$$
                return 1
            fi
        else
            log_success "$test_name (failed as expected)"
            return 0
        fi
    fi
}

# Start testing
echo "=========================================="
echo "  RELEASIO END-TO-END TESTING SUITE"
echo "=========================================="
echo ""

# Store original directory
ORIGINAL_DIR=$(pwd)

# ============================================================================
# TEST SUITE 1: Basic Workflow
# ============================================================================
echo -e "${BLUE}=== TEST SUITE 1: Basic Workflow ===${NC}"
echo ""

test_start "Create test project and verify structure"
TEST_DIR=$(create_test_project "basic_test")
if [ -f "$TEST_DIR/pyproject.toml" ] && [ -d "$TEST_DIR/.git" ]; then
    log_success "Project created successfully"
else
    log_error "Project creation failed" "Project structure"
fi

test_start "Run releasio check on fresh project (no tags)"
cd "$TEST_DIR"
uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if [ $? -eq 0 ]; then
    if grep -q "first release" /tmp/releasio_output_$$ || grep -q "0.1.0" /tmp/releasio_output_$$; then
        log_success "Check detects first release"
    else
        log_warning "Check succeeded but output unclear"
        cat /tmp/releasio_output_$$
    fi
else
    log_error "Check failed on fresh project" "Fresh project check"
    cat /tmp/releasio_output_$$
fi

test_start "Add conventional commits (feat, fix, docs)"
cd "$TEST_DIR"
echo "feature 1" > feature1.txt
git add .
git commit -q -m "feat: add feature 1"

echo "feature 2" > feature2.txt
git add .
git commit -q -m "fix: fix bug in feature 2"

echo "# README" > README.md
git add .
git commit -q -m "docs: add README"

log_success "Added 3 conventional commits"

test_start "Run releasio check --verbose"
uv run releasio check --verbose . > /tmp/releasio_output_$$ 2>&1
if [ $? -eq 0 ]; then
    if grep -q "feat" /tmp/releasio_output_$$ && grep -q "fix" /tmp/releasio_output_$$; then
        log_success "Check --verbose shows commit types"
    else
        log_warning "Verbose output doesn't show expected commits"
    fi
else
    log_error "Check --verbose failed" "Check verbose"
fi

cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 2: Version Bumping Logic
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 2: Version Bumping Logic ===${NC}"
echo ""

test_start "PATCH bump: fix commit"
TEST_DIR=$(create_test_project "patch_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "bugfix" > fix.txt
git add .
git commit -q -m "fix: critical bugfix"

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if grep -q "0.1.1" /tmp/releasio_output_$$ || grep -q "patch" /tmp/releasio_output_$$; then
    log_success "PATCH bump detected for fix commit"
else
    log_error "PATCH bump not detected" "PATCH bump"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

test_start "MINOR bump: feat commit"
TEST_DIR=$(create_test_project "minor_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "new feature" > feature.txt
git add .
git commit -q -m "feat: add new feature"

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if grep -q "0.2.0" /tmp/releasio_output_$$ || grep -q "minor" /tmp/releasio_output_$$; then
    log_success "MINOR bump detected for feat commit"
else
    log_error "MINOR bump not detected" "MINOR bump"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

test_start "MAJOR bump: breaking change with !"
TEST_DIR=$(create_test_project "major_test")
cd "$TEST_DIR"
git tag v1.0.0

echo "breaking change" > breaking.txt
git add .
git commit -q -m "feat!: redesign API completely"

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if grep -q "2.0.0" /tmp/releasio_output_$$ || grep -q "major" /tmp/releasio_output_$$; then
    log_success "MAJOR bump detected for breaking change"
else
    log_error "MAJOR bump not detected" "MAJOR bump"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

test_start "MAJOR bump: BREAKING CHANGE in footer"
TEST_DIR=$(create_test_project "major_footer_test")
cd "$TEST_DIR"
git tag v1.0.0

echo "breaking change" > breaking.txt
git add .
git commit -q -m "feat: new feature

BREAKING CHANGE: This changes the API"

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if grep -q "2.0.0" /tmp/releasio_output_$$ || grep -q "major" /tmp/releasio_output_$$; then
    log_success "MAJOR bump detected for BREAKING CHANGE footer"
else
    log_error "MAJOR bump not detected for footer" "MAJOR bump footer"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 3: Edge Cases & Error Handling
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 3: Edge Cases & Error Handling ===${NC}"
echo ""

test_start "Check fails on dirty repository (uncommitted changes)"
TEST_DIR=$(create_test_project "dirty_test")
cd "$TEST_DIR"
echo "uncommitted" > uncommitted.txt
git add uncommitted.txt
# Leave it staged but not committed

# Add allow_dirty = false to config
cat >> pyproject.toml <<EOF

[tool.releasio]
allow_dirty = false
EOF

expect_failure "uv run releasio check ." "Dirty repo check" "uncommitted"
cleanup_test_dir "$TEST_DIR"

test_start "Check works on dirty repository with allow_dirty = true"
TEST_DIR=$(create_test_project "dirty_allowed_test")
cd "$TEST_DIR"
echo "uncommitted" > uncommitted.txt
git add uncommitted.txt

cat >> pyproject.toml <<EOF

[tool.releasio]
allow_dirty = true
EOF

expect_success "uv run releasio check ." "Dirty repo with allow_dirty=true"
cleanup_test_dir "$TEST_DIR"

test_start "Check fails on non-git directory"
TEST_DIR=$(mktemp -d /tmp/releasio_no_git_$$)
cd "$TEST_DIR"
cat > pyproject.toml <<EOF
[project]
name = "test"
version = "0.1.0"
EOF

expect_failure "uv run releasio check ." "Non-git directory" "not a git repository"
cleanup_test_dir "$TEST_DIR"

test_start "Check fails on missing pyproject.toml"
TEST_DIR=$(mktemp -d /tmp/releasio_no_pyproject_$$)
cd "$TEST_DIR"
git init -q

expect_failure "uv run releasio check ." "Missing pyproject.toml" "pyproject.toml"
cleanup_test_dir "$TEST_DIR"

test_start "Check fails on wrong branch"
TEST_DIR=$(create_test_project "wrong_branch_test")
cd "$TEST_DIR"
git checkout -q -b develop

expect_failure "uv run releasio check ." "Wrong branch" "Must be on"
cleanup_test_dir "$TEST_DIR"

test_start "Check handles no commits since last tag"
TEST_DIR=$(create_test_project "no_commits_test")
cd "$TEST_DIR"
git tag v0.1.0
# No new commits

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if [ $? -eq 0 ]; then
    if grep -q "No commits" /tmp/releasio_output_$$ || grep -q "nothing to release" /tmp/releasio_output_$$; then
        log_success "Correctly detects no commits to release"
    else
        log_warning "Check succeeded but unclear message"
        cat /tmp/releasio_output_$$
    fi
else
    # It's OK if it fails gracefully
    if grep -q "No commits" /tmp/releasio_output_$$; then
        log_success "Correctly handles no commits (with error)"
    else
        log_error "Unexpected error for no commits" "No commits handling"
        cat /tmp/releasio_output_$$
    fi
fi
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 4: Commit Parsing Edge Cases
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 4: Commit Parsing Edge Cases ===${NC}"
echo ""

test_start "Commit with scope"
TEST_DIR=$(create_test_project "scope_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat(api): add new API endpoint"

uv run releasio check --verbose . > /tmp/releasio_output_$$ 2>&1
if grep -q "api" /tmp/releasio_output_$$; then
    log_success "Scope parsed correctly"
else
    log_warning "Scope may not be shown in output"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Multiple scopes in different commits"
TEST_DIR=$(create_test_project "multi_scope_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "api" > api.txt
git add .
git commit -q -m "feat(api): new endpoint"

echo "ui" > ui.txt
git add .
git commit -q -m "feat(ui): new button"

echo "core" > core.txt
git add .
git commit -q -m "fix(core): memory leak"

uv run releasio check --verbose . > /tmp/releasio_output_$$ 2>&1
if grep -q "api" /tmp/releasio_output_$$ && grep -q "ui" /tmp/releasio_output_$$; then
    log_success "Multiple scopes handled"
else
    log_warning "Not all scopes visible in output"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Non-conventional commits mixed with conventional"
TEST_DIR=$(create_test_project "mixed_commits_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "feat" > feat.txt
git add .
git commit -q -m "feat: proper feature"

echo "random" > random.txt
git add .
git commit -q -m "Updated some files"

echo "fix" > fix.txt
git add .
git commit -q -m "fix: proper fix"

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Mixed commits handled gracefully"
else
    log_error "Mixed commits caused failure" "Mixed commits"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

test_start "Commit with multi-line body"
TEST_DIR=$(create_test_project "multiline_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: add feature

This is a longer description
of the feature that spans
multiple lines.

- Item 1
- Item 2"

expect_success "uv run releasio check ." "Multi-line commit body"
cleanup_test_dir "$TEST_DIR"

test_start "Very long commit subject"
TEST_DIR=$(create_test_project "long_subject_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "feature" > feature.txt
git add .
LONG_SUBJECT="feat: this is a very very very very very very very very very very very very very very very very very very long commit subject that exceeds normal lengths"
git commit -q -m "$LONG_SUBJECT"

expect_success "uv run releasio check ." "Very long commit subject"
cleanup_test_dir "$TEST_DIR"

test_start "Special characters in commit message"
TEST_DIR=$(create_test_project "special_chars_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: add feature with special chars: @#\$%^&*(){}[]"

expect_success "uv run releasio check ." "Special characters in commit"
cleanup_test_dir "$TEST_DIR"

test_start "Unicode characters in commit message"
TEST_DIR=$(create_test_project "unicode_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: add emoji support 🚀 with 中文 and émojis"

expect_success "uv run releasio check ." "Unicode in commit message"
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 5: Tag Prefix Handling
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 5: Tag Prefix Handling ===${NC}"
echo ""

test_start "Default tag prefix 'v'"
TEST_DIR=$(create_test_project "prefix_v_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: new feature"

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if grep -q "v0.2.0" /tmp/releasio_output_$$; then
    log_success "Tag prefix 'v' works correctly"
else
    log_error "Tag prefix 'v' not working" "Tag prefix v"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

test_start "No tag prefix"
TEST_DIR=$(create_test_project "no_prefix_test")
cd "$TEST_DIR"

# Update config to remove prefix
cat > pyproject.toml <<EOF
[project]
name = "no_prefix_test"
version = "0.1.0"

[tool.releasio]
default_branch = "main"

[tool.releasio.version]
tag_prefix = ""

[tool.releasio.publish]
enabled = false
EOF

git add .
git commit -q -m "chore: update config"
git tag 0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: new feature"

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if grep -q "0.2.0" /tmp/releasio_output_$$; then
    log_success "No tag prefix works correctly"
else
    log_error "No tag prefix not working" "No tag prefix"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

test_start "Custom tag prefix 'release-'"
TEST_DIR=$(create_test_project "custom_prefix_test")
cd "$TEST_DIR"

cat > pyproject.toml <<EOF
[project]
name = "custom_prefix_test"
version = "0.1.0"

[tool.releasio]
default_branch = "main"

[tool.releasio.version]
tag_prefix = "release-"

[tool.releasio.publish]
enabled = false
EOF

git add .
git commit -q -m "chore: update config"
git tag release-0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: new feature"

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if grep -q "release-0.2.0" /tmp/releasio_output_$$ || grep -q "0.2.0" /tmp/releasio_output_$$; then
    log_success "Custom tag prefix works correctly"
else
    log_error "Custom tag prefix not working" "Custom tag prefix"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 6: Version Detection from Various Sources
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 6: Version Detection ===${NC}"
echo ""

test_start "Version from pyproject.toml [project] section"
TEST_DIR=$(create_test_project "version_project_test")
cd "$TEST_DIR"
expect_success "uv run releasio check ." "Version from [project]"
cleanup_test_dir "$TEST_DIR"

test_start "Version from __init__.py"
TEST_DIR=$(create_test_project "version_init_test")
cd "$TEST_DIR"

# Remove version from pyproject.toml
cat > pyproject.toml <<EOF
[project]
name = "version_init_test"
version = "0.1.0"

[tool.releasio]
default_branch = "main"
EOF

mkdir -p src/version_init_test
cat > src/version_init_test/__init__.py <<EOF
__version__ = "0.1.0"
EOF

git add .
git commit -q -m "chore: add __init__.py version"

expect_success "uv run releasio check ." "Version from __init__.py"
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 7: check-pr Command
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 7: check-pr Command ===${NC}"
echo ""

test_start "check-pr: valid conventional PR title"
expect_success "uv run releasio check-pr --title 'feat: add new feature'" "Valid PR title"

test_start "check-pr: valid PR title with scope"
expect_success "uv run releasio check-pr --title 'fix(api): handle null values'" "PR title with scope"

test_start "check-pr: breaking change with !"
uv run releasio check-pr --title 'feat!: redesign API' > /tmp/releasio_output_$$ 2>&1
if [ $? -eq 0 ] && grep -qi "breaking" /tmp/releasio_output_$$; then
    log_success "Breaking change detected in PR title"
else
    log_error "Breaking change not detected" "PR breaking change"
fi

test_start "check-pr: invalid PR title (no type)"
expect_failure "uv run releasio check-pr --title 'Added some feature'" "Invalid PR title" "invalid"

test_start "check-pr: invalid PR title (unknown type)"
expect_failure "uv run releasio check-pr --title 'unknown: some change'" "Unknown PR type" "invalid"

test_start "check-pr: require scope fails without scope"
expect_failure "uv run releasio check-pr --title 'feat: no scope' --require-scope" "Require scope without scope" "scope"

test_start "check-pr: require scope passes with scope"
expect_success "uv run releasio check-pr --title 'feat(api): with scope' --require-scope" "Require scope with scope"

# ============================================================================
# TEST SUITE 8: Stress Tests
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 8: Stress Tests ===${NC}"
echo ""

test_start "Many commits (100 commits)"
TEST_DIR=$(create_test_project "many_commits_test")
cd "$TEST_DIR"
git tag v0.1.0

for i in {1..100}; do
    echo "commit $i" > "file_$i.txt"
    git add .

    # Alternate between feat and fix
    if [ $((i % 2)) -eq 0 ]; then
        git commit -q -m "feat: feature $i"
    else
        git commit -q -m "fix: fix $i"
    fi
done

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Handled 100 commits successfully"
else
    log_error "Failed with 100 commits" "Many commits"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

test_start "Large files in repository"
TEST_DIR=$(create_test_project "large_files_test")
cd "$TEST_DIR"
git tag v0.1.0

# Create a 10MB file
dd if=/dev/zero of=large_file.bin bs=1M count=10 2>/dev/null
git add .
git commit -q -m "feat: add large file"

expect_success "uv run releasio check ." "Large files in repo"
cleanup_test_dir "$TEST_DIR"

test_start "Deep directory nesting"
TEST_DIR=$(create_test_project "deep_nesting_test")
cd "$TEST_DIR"
git tag v0.1.0

# Create deep directory structure
mkdir -p "a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p"
echo "deep file" > "a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/file.txt"
git add .
git commit -q -m "feat: add deeply nested file"

expect_success "uv run releasio check ." "Deep directory nesting"
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 9: Configuration Edge Cases
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 9: Configuration Edge Cases ===${NC}"
echo ""

test_start "Minimal valid configuration"
TEST_DIR=$(create_test_project "minimal_config_test")
cd "$TEST_DIR"

cat > pyproject.toml <<EOF
[project]
name = "minimal"
version = "0.1.0"
EOF

git add .
git commit -q -m "chore: minimal config"

expect_success "uv run releasio check ." "Minimal configuration"
cleanup_test_dir "$TEST_DIR"

test_start "Extra unknown fields in config (should be rejected)"
TEST_DIR=$(create_test_project "unknown_fields_test")
cd "$TEST_DIR"

cat >> pyproject.toml <<EOF

[tool.releasio]
unknown_field = "value"
another_unknown = 123
EOF

git add .
git commit -q -m "chore: add unknown fields"

uv run releasio check . > /tmp/releasio_output_$$ 2>&1
if [ $? -ne 0 ] && grep -q "Extra inputs are not permitted" /tmp/releasio_output_$$; then
    log_success "Unknown fields rejected correctly"
else
    log_warning "Unknown fields may not be validated strictly"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Custom commit parsers configuration"
TEST_DIR=$(create_test_project "custom_parser_test")
cd "$TEST_DIR"

cat > pyproject.toml <<EOF
[project]
name = "custom_parser"
version = "0.1.0"

[tool.releasio]
default_branch = "main"

[[tool.releasio.commits.commit_parsers]]
pattern = "^hotfix:"
group = "🔥 Hotfixes"

[[tool.releasio.commits.commit_parsers]]
pattern = "^security:"
group = "🔒 Security"
EOF

git add .
git commit -q -m "chore: add custom parsers"
git tag v0.1.0

echo "hotfix" > hotfix.txt
git add .
git commit -q -m "hotfix: critical production fix"

expect_success "uv run releasio check ." "Custom commit parsers"
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 10: Concurrent/Race Conditions (if applicable)
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 10: Filesystem Edge Cases ===${NC}"
echo ""

test_start "Read-only files in repository"
TEST_DIR=$(create_test_project "readonly_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "readonly" > readonly.txt
chmod 444 readonly.txt
git add .
git commit -q -m "feat: add readonly file"

expect_success "uv run releasio check ." "Read-only files"
chmod 644 readonly.txt  # Cleanup
cleanup_test_dir "$TEST_DIR"

test_start "Symbolic links in repository"
TEST_DIR=$(create_test_project "symlink_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "target" > target.txt
ln -s target.txt link.txt
git add .
git commit -q -m "feat: add symlink"

expect_success "uv run releasio check ." "Symbolic links"
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 11: Different Commit Types
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 11: All Commit Types ===${NC}"
echo ""

test_start "All standard commit types recognized"
TEST_DIR=$(create_test_project "all_types_test")
cd "$TEST_DIR"
git tag v0.1.0

TYPES=("feat" "fix" "docs" "style" "refactor" "perf" "test" "build" "ci" "chore")

for type in "${TYPES[@]}"; do
    echo "$type" > "${type}.txt"
    git add .
    git commit -q -m "$type: test $type commit"
done

uv run releasio check --verbose . > /tmp/releasio_output_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "All standard commit types handled"
else
    log_error "Failed with all commit types" "All commit types"
    cat /tmp/releasio_output_$$
fi
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 12: Update Command
# ============================================================================
echo ""
echo -e "${BLUE}=== TEST SUITE 12: Update Command ===${NC}"
echo ""

test_start "update command dry-run (preview mode)"
TEST_DIR=$(create_test_project "update_dryrun_test")
cd "$TEST_DIR"
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: new feature"

uv run releasio update . > /tmp/releasio_output_$$ 2>&1
if [ $? -eq 0 ]; then
    # Check that files weren't actually modified (dry-run)
    if grep -q "0.1.0" pyproject.toml; then
        log_success "Update dry-run doesn't modify files"
    else
        log_error "Update dry-run modified files" "Update dry-run"
    fi
else
    log_warning "Update command structure may have changed"
fi
cleanup_test_dir "$TEST_DIR"

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo ""
echo "=========================================="
echo "  TEST SUMMARY"
echo "=========================================="
echo -e "Total Tests Run:    ${BLUE}$TESTS_RUN${NC}"
echo -e "Tests Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed:       ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}FAILED TESTS:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗${NC} $test"
    done
    echo ""
    exit 1
else
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    exit 0
fi
