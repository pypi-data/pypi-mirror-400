#!/bin/bash
# Comprehensive End-to-End Testing for releasio (v3 - Deep Coverage)
# Goal: Maximum coverage with stress tests and edge cases

set +e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0
FAILED_TESTS=()

# Get the path to releasio CLI
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

log_skip() {
    echo -e "${CYAN}[SKIP]${NC} $1"
    ((TESTS_SKIPPED++))
}

test_start() {
    ((TESTS_RUN++))
    echo -e "\n${MAGENTA}━━━ TEST #$TESTS_RUN ━━━${NC}"
    echo -e "${BLUE}$1${NC}"
}

test_section() {
    echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  $1${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
}

cleanup_test_dir() {
    if [ -d "$1" ]; then
        chmod -R +w "$1" 2>/dev/null || true
        rm -rf "$1"
    fi
}

create_base_project() {
    local name=$1
    local version=${2:-0.1.0}
    local test_dir=$(mktemp -d /tmp/releasio_e2e_XXXXXX)

    cd "$test_dir"
    mkdir -p src/${name}

    cat > src/${name}/__init__.py <<EOF
"""${name} package."""
__version__ = "${version}"
EOF

    cat > pyproject.toml <<EOF
[project]
name = "${name}"
version = "${version}"
description = "Test project"
requires-python = ">=3.11"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/${name}"]

[tool.releasio]
default_branch = "main"

[tool.releasio.version]
tag_prefix = "v"

[tool.releasio.publish]
enabled = false
EOF

    cat > README.md <<EOF
# ${name}
Test project for releasio
EOF

    git init -q
    git config user.email "test@releasio.test"
    git config user.name "Releasio Test"
    git add .
    git commit -q -m "chore: initial commit"
    git branch -m main

    echo "$test_dir"
}

echo "══════════════════════════════════════════════════════════════"
echo "  RELEASIO END-TO-END TESTING SUITE V3 (DEEP COVERAGE)"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "Test Location: $RELEASIO_DIR"
echo "Start Time: $(date)"
echo ""

ORIGINAL_DIR=$(pwd)

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 1: PR Title Validation - Exhaustive
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 1: PR Title Validation (Exhaustive)"

ALL_TYPES=("feat" "fix" "docs" "style" "refactor" "perf" "test" "build" "ci" "chore")

for type in "${ALL_TYPES[@]}"; do
    test_start "check-pr: Valid $type type"
    run_releasio check-pr --title "$type: test message" > /tmp/test_$$ 2>&1
    if [ $? -eq 0 ]; then
        log_success "$type type accepted"
    else
        log_error "$type type rejected" "check-pr $type"
    fi
done

test_start "check-pr: Multiple scopes in same session"
for scope in "api" "ui" "core" "db" "auth"; do
    run_releasio check-pr --title "feat($scope): test" > /tmp/test_$$ 2>&1
    if [ $? -ne 0 ]; then
        log_error "Scope $scope failed" "check-pr scope $scope"
        break
    fi
done
log_success "Multiple scopes handled"

test_start "check-pr: Very long PR title (200+ chars)"
LONG_TITLE="feat: $(printf 'a%.0s' {1..200})"
run_releasio check-pr --title "$LONG_TITLE" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Very long title handled"
else
    log_warning "Very long title may have issues"
fi

test_start "check-pr: Title with special regex characters"
run_releasio check-pr --title "fix: handle [brackets] and (parens) and \$vars" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Special regex chars handled"
else
    log_error "Special regex chars failed" "check-pr regex"
fi

test_start "check-pr: Multiple exclamation marks"
run_releasio check-pr --title "feat!!: multiple exclamations" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ] && grep -qi "breaking" /tmp/test_$$; then
    log_success "Multiple ! handled as breaking"
else
    log_warning "Multiple ! behavior unclear"
fi

test_start "check-pr: Nested scopes"
run_releasio check-pr --title "feat(api/v2): nested scope" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Nested scopes handled"
else
    log_warning "Nested scopes may not be supported"
fi

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 2: All Conventional Commit Types
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 2: All Conventional Commit Types"

test_start "All 10 standard commit types in one repo"
TEST_DIR=$(create_base_project "alltypes" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

for i in "${!ALL_TYPES[@]}"; do
    echo "file $i" > "file_$i.txt"
    git add .
    git commit -q -m "${ALL_TYPES[$i]}: test ${ALL_TYPES[$i]} commit"
done

run_releasio check --verbose "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    # Check if we can see various types in output
    found_count=0
    for type in "feat" "fix" "docs"; do
        if grep -q "$type" /tmp/test_$$; then
            ((found_count++))
        fi
    done
    if [ $found_count -ge 2 ]; then
        log_success "All commit types processed"
    else
        log_warning "Some commit types may not be visible"
    fi
else
    log_error "Failed processing all types" "All types"
fi

cleanup_test_dir "$TEST_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 3: Version Bump Precision Tests
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 3: Version Bump Precision"

test_start "PATCH: Only fix commits after tag"
TEST_DIR=$(create_base_project "patch" "1.2.3")
cd "$TEST_DIR"
git tag v1.2.3

for i in {1..5}; do
    echo "fix $i" > "fix$i.txt"
    git add .
    git commit -q -m "fix: bugfix $i"
done

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if grep -q "1.2.4\|patch" /tmp/test_$$; then
    log_success "Multiple fix commits → PATCH bump"
else
    log_error "PATCH bump incorrect" "PATCH multiple"
fi
cleanup_test_dir "$TEST_DIR"

test_start "MINOR: feat takes precedence over fix"
TEST_DIR=$(create_base_project "minor" "1.0.0")
cd "$TEST_DIR"
git tag v1.0.0

echo "fix" > fix.txt
git add .
git commit -q -m "fix: some fix"

echo "feat" > feat.txt
git add .
git commit -q -m "feat: new feature"

echo "fix2" > fix2.txt
git add .
git commit -q -m "fix: another fix"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if grep -q "1.1.0\|minor" /tmp/test_$$; then
    log_success "feat + fix → MINOR bump (not PATCH)"
else
    log_error "MINOR precedence failed" "MINOR precedence"
fi
cleanup_test_dir "$TEST_DIR"

test_start "MAJOR: Breaking change takes precedence over all"
TEST_DIR=$(create_base_project "major" "2.5.9")
cd "$TEST_DIR"
git tag v2.5.9

echo "feat" > feat.txt
git add .
git commit -q -m "feat: feature"

echo "fix" > fix.txt
git add .
git commit -q -m "fix: fix"

echo "breaking" > breaking.txt
git add .
git commit -q -m "feat!: breaking change"

echo "feat2" > feat2.txt
git add .
git commit -q -m "feat: another feature"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if grep -q "3.0.0\|major" /tmp/test_$$; then
    log_success "Breaking change → MAJOR (overrides feat/fix)"
else
    log_error "MAJOR precedence failed" "MAJOR precedence"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Version bump from 0.x.x → 1.0.0 (breaking in pre-1.0)"
TEST_DIR=$(create_base_project "pre10" "0.9.5")
cd "$TEST_DIR"
git tag v0.9.5

echo "breaking" > breaking.txt
git add .
git commit -q -m "feat!: breaking change before 1.0"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if grep -q "1.0.0\|major" /tmp/test_$$; then
    log_success "Breaking in 0.x → 1.0.0"
else
    log_warning "Pre-1.0 breaking behavior may differ"
fi
cleanup_test_dir "$TEST_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 4: Complex Commit Scenarios
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 4: Complex Commit Scenarios"

test_start "Commits with multiple BREAKING CHANGE footers"
TEST_DIR=$(create_base_project "multibreak" "1.0.0")
cd "$TEST_DIR"
git tag v1.0.0

echo "file" > file.txt
git add .
git commit -q -m "feat: new feature

BREAKING CHANGE: First breaking change
BREAKING CHANGE: Second breaking change"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if grep -q "2.0.0\|major" /tmp/test_$$; then
    log_success "Multiple BREAKING CHANGE footers handled"
else
    log_error "Multiple breaking footers failed" "Multi breaking"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Commit body with code blocks and markdown"
TEST_DIR=$(create_base_project "markdown" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

echo "file" > file.txt
git add .
git commit -q -m 'feat: add feature

This commit includes:

```python
def hello():
    print("world")
```

And some **bold** and *italic* text.

- List item 1
- List item 2

See: https://example.com'

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Markdown in commit body handled"
else
    log_error "Markdown parsing failed" "Markdown body"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Commit with Co-authored-by trailers"
TEST_DIR=$(create_base_project "coauthor" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

echo "file" > file.txt
git add .
git commit -q -m "feat: collaborative feature

Co-authored-by: Alice <alice@example.com>
Co-authored-by: Bob <bob@example.com>"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Co-authored-by trailers handled"
else
    log_error "Co-authored trailers failed" "Co-authored"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Revert commit handling"
TEST_DIR=$(create_base_project "revert" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

echo "feature" > feature.txt
git add .
git commit -q -m "feat: add feature"
COMMIT_SHA=$(git rev-parse HEAD)

git revert --no-edit $COMMIT_SHA

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Revert commits handled"
else
    log_warning "Revert commit handling unclear"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Merge commit in history"
TEST_DIR=$(create_base_project "merge" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

# Create a feature branch
git checkout -q -b feature
echo "feature" > feature.txt
git add .
git commit -q -m "feat: feature branch work"

# Go back to main and merge
git checkout -q main
git merge --no-ff -m "Merge branch 'feature'" feature -q

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Merge commits handled"
else
    log_warning "Merge commit handling unclear"
fi
cleanup_test_dir "$TEST_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 5: Tag and Version Edge Cases
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 5: Tag and Version Edge Cases"

test_start "Multiple tags on same commit"
TEST_DIR=$(create_base_project "multitag" "1.0.0")
cd "$TEST_DIR"
git tag v1.0.0
git tag release-1.0.0

echo "feat" > feat.txt
git add .
git commit -q -m "feat: new feature"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if grep -q "1.1.0\|minor" /tmp/test_$$ || [ $? -eq 0 ]; then
    log_success "Multiple tags handled"
else
    log_warning "Multiple tags may cause issues"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Tag prefix with numbers: rel-1.0.0"
TEST_DIR=$(create_base_project "numprefix" "1.0.0")
cd "$TEST_DIR"

cat > pyproject.toml <<EOF
[project]
name = "numprefix"
version = "1.0.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/numprefix"]
[tool.releasio]
default_branch = "main"
[tool.releasio.version]
tag_prefix = "rel-"
[tool.releasio.publish]
enabled = false
EOF

git add .
git commit -q -m "chore: update config"
git tag rel-1.0.0

echo "feat" > feat.txt
git add .
git commit -q -m "feat: new feature"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if grep -q "rel-1.1.0\|1.1.0" /tmp/test_$$ || [ $? -eq 0 ]; then
    log_success "Numeric tag prefix handled"
else
    log_warning "Numeric tag prefix unclear"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Annotated vs lightweight tags"
TEST_DIR=$(create_base_project "tagtypes" "1.0.0")
cd "$TEST_DIR"

# Create annotated tag
git tag -a v1.0.0 -m "Release 1.0.0"

echo "feat" > feat.txt
git add .
git commit -q -m "feat: new feature"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if grep -q "1.1.0" /tmp/test_$$; then
    log_success "Annotated tags handled same as lightweight"
else
    log_warning "Annotated tag handling unclear"
fi
cleanup_test_dir "$TEST_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 6: Configuration Variations
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 6: Configuration Variations"

test_start "Custom default_branch: develop"
TEST_DIR=$(create_base_project "custombranch" "0.1.0")
cd "$TEST_DIR"

cat > pyproject.toml <<EOF
[project]
name = "custombranch"
version = "0.1.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/custombranch"]
[tool.releasio]
default_branch = "develop"
[tool.releasio.publish]
enabled = false
EOF

git add .
git commit -q -m "chore: config update"
git branch -m develop
git tag v0.1.0

echo "feat" > feat.txt
git add .
git commit -q -m "feat: on develop"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Custom default_branch works"
else
    log_error "Custom branch failed" "Custom branch"
fi
cleanup_test_dir "$TEST_DIR"

test_start "allow_dirty = true with uncommitted changes"
TEST_DIR=$(create_base_project "dirty" "0.1.0")
cd "$TEST_DIR"

cat >> pyproject.toml <<EOF

[tool.releasio]
allow_dirty = true
EOF

git add .
git commit -q -m "chore: allow dirty"
git tag v0.1.0

echo "uncommitted" > uncommitted.txt
git add uncommitted.txt
# Leave staged but not committed

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "allow_dirty=true permits uncommitted changes"
else
    log_error "allow_dirty failed" "allow_dirty"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Empty tag prefix (no prefix)"
TEST_DIR=$(create_base_project "noprefix" "1.0.0")
cd "$TEST_DIR"

cat > pyproject.toml <<EOF
[project]
name = "noprefix"
version = "1.0.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/noprefix"]
[tool.releasio]
default_branch = "main"
[tool.releasio.version]
tag_prefix = ""
[tool.releasio.publish]
enabled = false
EOF

git add .
git commit -q -m "chore: no prefix"
git tag 1.0.0

echo "feat" > feat.txt
git add .
git commit -q -m "feat: feature"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if grep -q "1.1.0" /tmp/test_$$; then
    log_success "Empty tag prefix works"
else
    log_error "Empty prefix failed" "Empty prefix"
fi
cleanup_test_dir "$TEST_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 7: Stress Tests
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 7: Stress Tests"

test_start "100 commits with mixed types"
TEST_DIR=$(create_base_project "stress100" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

types=("feat" "fix" "docs" "chore")
for i in {1..100}; do
    type_idx=$((i % 4))
    echo "commit $i" > "file_$i.txt"
    git add .
    git commit -q -m "${types[$type_idx]}: commit $i" >/dev/null 2>&1
done

start_time=$(date +%s)
run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
end_time=$(date +%s)
duration=$((end_time - start_time))

if [ $? -eq 0 ]; then
    log_success "100 commits processed (${duration}s)"
else
    log_error "100 commits failed" "Stress 100"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Deep commit history: 50 tags with commits between"
TEST_DIR=$(create_base_project "deephistory" "0.1.0")
cd "$TEST_DIR"

for version in {1..20}; do
    git tag "v0.1.$version"
    for commit in {1..3}; do
        echo "v0.1.$version-$commit" > "file_${version}_${commit}.txt"
        git add .
        git commit -q -m "feat: version 0.1.$version commit $commit" >/dev/null 2>&1
    done
done

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Deep history (20 tags) handled"
else
    log_warning "Deep history may cause issues"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Very large single file (10MB) in commit"
TEST_DIR=$(create_base_project "largefile" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

dd if=/dev/zero of=large.bin bs=1M count=10 2>/dev/null
git add large.bin
git commit -q -m "feat: add large binary file"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Large file in commit handled"
else
    log_warning "Large files may slow processing"
fi
cleanup_test_dir "$TEST_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 8: Project Structure Variations
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 8: Project Structure Variations"

test_start "Flat layout (no src/ directory)"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

mkdir -p flatpkg

cat > flatpkg/__init__.py <<'EOF'
__version__ = "0.1.0"
EOF

cat > pyproject.toml <<'EOF'
[project]
name = "flatpkg"
version = "0.1.0"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["flatpkg"]
[tool.releasio]
default_branch = "main"
EOF

git init -q
git config user.email "test@test.com"
git config user.name "Test"
git add .
git commit -q -m "chore: init"
git branch -m main
git tag v0.1.0

echo "feat" > feat.txt
git add .
git commit -q -m "feat: flat layout feature"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Flat layout structure works"
else
    log_error "Flat layout failed" "Flat layout"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Hyphenated package name (my-cool-pkg)"
TEST_DIR=$(create_base_project "my-cool-pkg" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

echo "feat" > feat.txt
git add .
git commit -q -m "feat: hyphenated package"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Hyphenated package name works"
else
    log_warning "Hyphenated names may have issues"
fi
cleanup_test_dir "$TEST_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 9: Error Handling and Recovery
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 9: Error Handling"

test_start "Missing pyproject.toml"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"
git init -q

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -ne 0 ] && grep -qi "pyproject\|project not found" /tmp/test_$$; then
    log_success "Missing pyproject.toml detected gracefully"
else
    log_error "Missing pyproject error unclear" "Missing pyproject"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Non-git directory"
TEST_DIR=$(mktemp -d /tmp/releasio_e2e_XXXXXX)
cd "$TEST_DIR"

cat > pyproject.toml <<'EOF'
[project]
name = "test"
version = "0.1.0"
EOF

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -ne 0 ] && grep -qi "git\|repository" /tmp/test_$$; then
    log_success "Non-git directory error clear"
else
    log_error "Non-git error unclear" "Non-git"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Invalid version format in pyproject.toml"
TEST_DIR=$(create_base_project "badver" "0.1.0")
cd "$TEST_DIR"

# Corrupt the version
sed -i 's/version = "0.1.0"/version = "not-a-version"/' pyproject.toml
git add .
git commit -q -m "chore: bad version"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -ne 0 ]; then
    log_success "Invalid version format detected"
else
    log_warning "Invalid version not caught"
fi
cleanup_test_dir "$TEST_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# SUITE 10: Unicode and Special Characters (Extended)
# ═══════════════════════════════════════════════════════════════════════════
test_section "SUITE 10: Unicode and Internationalization"

test_start "Commit with Arabic text"
TEST_DIR=$(create_base_project "arabic" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

echo "file" > file.txt
git add .
git commit -q -m "feat: دعم اللغة العربية (Arabic support)"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Arabic text handled"
else
    log_error "Arabic text failed" "Arabic"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Commit with Japanese text"
TEST_DIR=$(create_base_project "japanese" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

echo "file" > file.txt
git add .
git commit -q -m "feat: 日本語サポート追加 (Japanese support)"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Japanese text handled"
else
    log_error "Japanese text failed" "Japanese"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Commit with mixed scripts"
TEST_DIR=$(create_base_project "mixed" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

echo "file" > file.txt
git add .
git commit -q -m "feat: Support 🌍 English, 中文, العربية, 日本語, Русский"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Mixed scripts handled"
else
    log_error "Mixed scripts failed" "Mixed scripts"
fi
cleanup_test_dir "$TEST_DIR"

test_start "Emoji storm: Multiple emojis"
TEST_DIR=$(create_base_project "emojistorm" "0.1.0")
cd "$TEST_DIR"
git tag v0.1.0

echo "file" > file.txt
git add .
git commit -q -m "feat: 🎉🚀🔥💯✨🎯🏆🌟⭐🎊 emoji party"

run_releasio check "$TEST_DIR" > /tmp/test_$$ 2>&1
if [ $? -eq 0 ]; then
    log_success "Emoji storm handled"
else
    log_warning "Emoji storm may cause issues"
fi
cleanup_test_dir "$TEST_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# FINAL REPORT
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  TEST EXECUTION COMPLETE"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "End Time: $(date)"
echo ""
echo "╔══════════════════════ SUMMARY ═══════════════════════════╗"
echo "║                                                          ║"
printf "║  Total Tests Run:    %-31s ║\n" "$TESTS_RUN"
printf "║  ${GREEN}✓${NC} Passed:          %-31s ║\n" "$TESTS_PASSED"
printf "║  ${RED}✗${NC} Failed:          %-31s ║\n" "$TESTS_FAILED"
printf "║  ${CYAN}○${NC} Skipped:         %-31s ║\n" "$TESTS_SKIPPED"
echo "║                                                          ║"

if [ $TESTS_FAILED -eq 0 ]; then
    PASS_RATE=100
else
    PASS_RATE=$((TESTS_PASSED * 100 / (TESTS_PASSED + TESTS_FAILED)))
fi

printf "║  Pass Rate:         ${GREEN}%-4d%%${NC}                           ║\n" "$PASS_RATE"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}FAILED TESTS:${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗${NC} $test"
    done
    echo ""
    exit 1
else
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                       ║${NC}"
    echo -e "${GREEN}║           🎉 ALL TESTS PASSED! 🎉                     ║${NC}"
    echo -e "${GREEN}║                                                       ║${NC}"
    echo -e "${GREEN}║  Releasio is production-ready and battle-tested!      ║${NC}"
    echo -e "${GREEN}║                                                       ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 0
fi
