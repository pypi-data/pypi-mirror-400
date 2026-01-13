#!/bin/bash
# Comprehensive End-to-End Testing for releasio (v2 - Direct CLI usage)
# Goal: Break the system and discover nasty bugs

set +e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Get the path to releasio CLI (use from current project)
# We need to run it from the releasio project directory
RELEASIO_DIR="/home/mikko/dev/release-py"
run_releasio() {
    cd "$RELEASIO_DIR" && uv run releasio "$@"
}

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
    echo -e "\n${BLUE}TEST #$TESTS_RUN:${NC} $1"
}

cleanup_test_dir() {
    if [ -d "$1" ]; then
        chmod -R +w "$1" 2>/dev/null || true
        rm -rf "$1"
    fi
}

echo "=========================================="
echo "  RELEASIO END-TO-END TESTING SUITE V2"
echo "=========================================="
echo ""
echo "Using releasio from: $RELEASIO_DIR"
echo ""

ORIGINAL_DIR=$(pwd)

# ============================================================================
# TEST SUITE 1: check-pr command (doesn't need a project)
# ============================================================================
echo -e "${BLUE}=== TEST SUITE 1: check-pr Command ===${NC}"

test_start "check-pr with valid feat title"
run_releasio check-pr --title "feat: add new feature" > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Valid feat title accepted"
else
    log_error "Valid feat title rejected" "check-pr feat"
    cat /tmp/test_out_$$
fi

test_start "check-pr with valid fix(scope) title"
run_releasio check-pr --title "fix(api): handle null" > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Valid fix with scope accepted"
else
    log_error "Valid fix with scope rejected" "check-pr fix scope"
fi

test_start "check-pr with breaking change (feat!)"
run_releasio check-pr --title "feat!: redesign API" > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ] && grep -qi "breaking" /tmp/test_out_$$; then
    log_success "Breaking change detected"
else
    log_error "Breaking change not detected" "check-pr breaking"
fi

test_start "check-pr with invalid title (no type)"
run_releasio check-pr --title "Added some feature" > /tmp/test_out_$$ 2>&1
if [ $? -ne 0 ]; then
    log_success "Invalid title rejected"
else
    log_error "Invalid title accepted" "check-pr invalid"
fi

test_start "check-pr with unknown type"
run_releasio check-pr --title "unknown: some change" > /tmp/test_out_$$ 2>&1
if [ $? -ne 0 ]; then
    log_success "Unknown type rejected"
else
    log_error "Unknown type accepted" "check-pr unknown"
fi

test_start "check-pr --require-scope without scope"
run_releasio check-pr --title "feat: no scope" --require-scope > /tmp/test_out_$$ 2>&1
if [ $? -ne 0 ] && grep -qi "scope" /tmp/test_out_$$; then
    log_success "Scope requirement enforced"
else
    log_error "Scope requirement not enforced" "check-pr require-scope"
fi

test_start "check-pr --require-scope with scope"
run_releasio check-pr --title "feat(api): with scope" --require-scope > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Scope requirement satisfied"
else
    log_error "Scope requirement failed incorrectly" "check-pr scope satisfied"
fi

# ============================================================================
# TEST SUITE 2: Real projects with proper structure
# ============================================================================
echo -e "\n${BLUE}=== TEST SUITE 2: Basic Project Workflow ===${NC}"

test_start "Create proper test project with Python package"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

# Create proper Python project structure
mkdir -p src/testpkg
cat > src/testpkg/__init__.py <<EOF
"""Test package for releasio."""
__version__ = "0.1.0"
EOF

cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "0.1.0"
description = "Test project"
requires-python = ">=3.11"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]

[tool.releasio]
default_branch = "main"

[tool.releasio.version]
tag_prefix = "v"

[tool.releasio.publish]
enabled = false
EOF

cat > README.md <<EOF
# Test Package
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: initial commit"
git branch -m main

if [ -f "pyproject.toml" ] && [ -d ".git" ] && [ -f "src/testpkg/__init__.py" ]; then
    log_success "Proper Python project created"
else
    log_error "Project creation failed" "Project setup"
fi

test_start "check on fresh project (no tags, no conventional commits)"
cd "$TEST_DIR"
run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
result=$?
if [ $result -eq 0 ] || grep -qi "first release\|no commits\|nothing to release" /tmp/test_out_$$; then
    log_success "Check handles fresh project"
else
    log_warning "Check on fresh project: unclear result (exit: $result)"
    cat /tmp/test_out_$$ | head -20
fi

test_start "Add conventional commits and check again"
cd "$TEST_DIR"
echo "feature 1" > feature1.txt
git add .
git commit -q -m "feat: add feature 1"

echo "bugfix" > bugfix.txt
git add .
git commit -q -m "fix: fix critical bug"

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ]; then
    if grep -q "feat\|fix\|0.2.0\|minor" /tmp/test_out_$$; then
        log_success "Check detects conventional commits and suggests version"
    else
        log_warning "Check succeeded but unclear output"
    fi
else
    log_error "Check failed with conventional commits" "Check with commits"
    cat /tmp/test_out_$$ | head -20
fi

test_start "check --verbose shows commit details"
cd "$TEST_DIR"
run_releasio check --verbose "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ]; then
    if grep -q "feat\|fix" /tmp/test_out_$$; then
        log_success "Verbose mode shows commit types"
    else
        log_warning "Verbose succeeded but no commit details visible"
    fi
else
    log_warning "Verbose mode failed (exit: $?)"
fi

test_start "Version bumping: PATCH for fix commit"
cd "$TEST_DIR"
git tag v0.1.0

echo "bugfix2" > bugfix2.txt
git add .
git commit -q -m "fix: another bugfix"

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if grep -q "0.1.1\|patch" /tmp/test_out_$$; then
    log_success "PATCH bump detected"
else
    log_error "PATCH bump not detected" "PATCH bump"
fi

cleanup_test_dir "$TEST_DIR"

test_start "Version bumping: MINOR for feat commit"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p src/testpkg
cat > src/testpkg/__init__.py <<'EOF'
__version__ = "0.1.0"
EOF

cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "0.1.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]
[tool.releasio]
default_branch = "main"
[tool.releasio.publish]
enabled = false
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: init"
git branch -m main
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: new feature"

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if grep -q "0.2.0\|minor" /tmp/test_out_$$; then
    log_success "MINOR bump detected"
else
    log_error "MINOR bump not detected" "MINOR bump"
fi

cleanup_test_dir "$TEST_DIR"

test_start "Version bumping: MAJOR for breaking change"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p src/testpkg
cat > src/testpkg/__init__.py <<'EOF'
__version__ = "1.0.0"
EOF

cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "1.0.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]
[tool.releasio]
default_branch = "main"
[tool.releasio.publish]
enabled = false
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: init"
git branch -m main
git tag v1.0.0

echo "breaking" > breaking.txt
git add .
git commit -q -m "feat!: redesign API"

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if grep -q "2.0.0\|major" /tmp/test_out_$$; then
    log_success "MAJOR bump detected for !"
else
    log_error "MAJOR bump not detected" "MAJOR bump !"
fi

cleanup_test_dir "$TEST_DIR"

test_start "Version bumping: MAJOR for BREAKING CHANGE footer"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p src/testpkg
cat > src/testpkg/__init__.py <<'EOF'
__version__ = "1.0.0"
EOF

cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "1.0.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]
[tool.releasio]
default_branch = "main"
[tool.releasio.publish]
enabled = false
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: init"
git branch -m main
git tag v1.0.0

echo "breaking" > breaking.txt
git add .
git commit -q -m "feat: new feature

BREAKING CHANGE: This changes the API"

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if grep -q "2.0.0\|major" /tmp/test_out_$$; then
    log_success "MAJOR bump detected for BREAKING CHANGE footer"
else
    log_error "MAJOR bump not detected for footer" "MAJOR bump footer"
fi

cleanup_test_dir "$TEST_DIR"

# ============================================================================
# TEST SUITE 3: Edge Cases
# ============================================================================
echo -e "\n${BLUE}=== TEST SUITE 3: Edge Cases ===${NC}"

test_start "Commit with scope"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p src/testpkg
echo '__version__ = "0.1.0"' > src/testpkg/__init__.py
cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "0.1.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]
[tool.releasio]
default_branch = "main"
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: init"
git branch -m main
git tag v0.1.0

echo "api" > api.txt
git add .
git commit -q -m "feat(api): new endpoint"

run_releasio check --verbose "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Scope in commit handled"
else
    log_error "Scope handling failed" "Scope"
fi

cleanup_test_dir "$TEST_DIR"

test_start "Mixed conventional and non-conventional commits"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p src/testpkg
echo '__version__ = "0.1.0"' > src/testpkg/__init__.py
cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "0.1.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]
[tool.releasio]
default_branch = "main"
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: init"
git branch -m main
git tag v0.1.0

echo "feat" > feat.txt
git add .
git commit -q -m "feat: proper feature"

echo "random" > random.txt
git add .
git commit -q -m "Updated some stuff"

echo "fix" > fix.txt
git add .
git commit -q -m "fix: proper fix"

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Mixed commits handled gracefully"
else
    log_warning "Mixed commits caused issues"
fi

cleanup_test_dir "$TEST_DIR"

test_start "Multi-line commit message"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p src/testpkg
echo '__version__ = "0.1.0"' > src/testpkg/__init__.py
cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "0.1.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]
[tool.releasio]
default_branch = "main"
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: init"
git branch -m main
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: add feature

This is a longer description
that spans multiple lines.

- Item 1
- Item 2"

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Multi-line commit handled"
else
    log_error "Multi-line commit failed" "Multi-line"
fi

cleanup_test_dir "$TEST_DIR"

test_start "Unicode in commit message"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p src/testpkg
echo '__version__ = "0.1.0"' > src/testpkg/__init__.py
cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "0.1.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]
[tool.releasio]
default_branch = "main"
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: init"
git branch -m main
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: add emoji support 🚀 with 中文"

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Unicode in commit handled"
else
    log_error "Unicode handling failed" "Unicode"
fi

cleanup_test_dir "$TEST_DIR"

test_start "Wrong branch detection"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p src/testpkg
echo '__version__ = "0.1.0"' > src/testpkg/__init__.py
cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "0.1.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]
[tool.releasio]
default_branch = "main"
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: init"
git branch -m main
git checkout -q -b develop

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if [ $? -ne 0 ] && grep -qi "branch\|main" /tmp/test_out_$$; then
    log_success "Wrong branch detected"
else
    log_error "Wrong branch not detected" "Wrong branch"
fi

cleanup_test_dir "$TEST_DIR"

test_start "No commits since last tag"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p src/testpkg
echo '__version__ = "0.1.0"' > src/testpkg/__init__.py
cat > pyproject.toml <<EOF
[project]
name = "testpkg"
version = "0.1.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/testpkg"]
[tool.releasio]
default_branch = "main"
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test User"
git add .
git commit -q -m "chore: init"
git branch -m main
git tag v0.1.0

run_releasio check "$TEST_DIR" > /tmp/test_out_$$ 2>&1
if grep -qi "no commits\|nothing to release" /tmp/test_out_$$; then
    log_success "No commits detected"
else
    log_warning "No commits handling unclear"
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
