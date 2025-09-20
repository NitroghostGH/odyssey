#!/usr/bin/env bash
# rewrite_email_filter_branch.sh
# Safely rewrite all git history replacing an old email (and optionally name) with a new GitHub noreply identity.
# This uses git filter-branch (sufficient for small repos) plus safety features:
#   1. Creates/keeps a mirror backup ../odyssey-backup-mirror (bare, untouched)
#   2. Optional simulation mode: clones a temporary mirror and performs the rewrite there (no changes to working repo)
#   3. On --run executes in-place, rewrites commits for all refs (heads + tags)
#   4. Provides verification instructions & force-push guidance
#
# Usage examples:
#   ./scripts/rewrite_email_filter_branch.sh --old OLD_EMAIL --new NEW_EMAIL --name "New Name"
#       (prints plan only)
#   ./scripts/rewrite_email_filter_branch.sh --old OLD --new NEW --name "New Name" --simulate
#       (runs rewrite in temp clone, shows before/after counts)
#   ./scripts/rewrite_email_filter_branch.sh --old OLD --new NEW --name "New Name" --run
#       (performs destructive rewrite locally)
# Options:
#   --old <email>        Old email to replace
#   --new <email>        New email to use
#   --name <name>        New author/committer name when old email matched
#   --simulate           Perform rewrite in a throwaway mirror to preview result
#   --run                Execute rewrite in the current repository (destructive)
#   --force              Skip confirmation prompt when using --run
#   --help               Show this help
#
# After successful --run you must force push:  git push --force --tags origin <default-branch>
# NOTE: filter-branch is deprecated upstream but acceptable for small repos; alternative: git filter-repo.

set -euo pipefail

OLD=""
NEW=""
NEW_NAME=""
SIMULATE=0
RUN=0
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --old) OLD="$2"; shift 2;;
    --new) NEW="$2"; shift 2;;
    --name) NEW_NAME="$2"; shift 2;;
    --simulate) SIMULATE=1; shift;;
    --run) RUN=1; shift;;
    --force) FORCE=1; shift;;
    -h|--help) grep '^#' "$0" | sed 's/^# //'; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

if [[ -z "$OLD" || -z "$NEW" || -z "$NEW_NAME" ]]; then
  echo "Missing required arguments. See --help" >&2; exit 1
fi

if [[ ! -d .git ]]; then
  echo "Error: must run inside a git worktree" >&2; exit 1
fi

default_branch() {
  local d
  if d=$(git symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null); then
    echo "${d##*/}"; return 0
  fi
  if git show-ref --verify --quiet refs/heads/main; then echo main; return 0; fi
  if git show-ref --verify --quiet refs/heads/master; then echo master; return 0; fi
  git rev-parse --abbrev-ref HEAD
}

DEFAULT_BRANCH=$(default_branch)

# Backup mirror (bare) if not already present
if [[ ! -d ../odyssey-backup-mirror ]]; then
  echo "Creating mirror backup at ../odyssey-backup-mirror" >&2
  git clone --mirror . ../odyssey-backup-mirror
else
  echo "Mirror backup exists (../odyssey-backup-mirror)" >&2
fi

echo "Plan:" >&2
echo "  Replace commits where author/committer email == $OLD" >&2
echo "    -> email: $NEW" >&2
echo "    -> name : $NEW_NAME" >&2

rewrite_env_filter() {
  cat <<'EOF'
if [ "$GIT_AUTHOR_EMAIL" = "__OLD__" ]; then
  GIT_AUTHOR_NAME="__NEW_NAME__"
  GIT_AUTHOR_EMAIL="__NEW__"
fi
if [ "$GIT_COMMITTER_EMAIL" = "__OLD__" ]; then
  GIT_COMMITTER_NAME="__NEW_NAME__"
  GIT_COMMITTER_EMAIL="__NEW__"
fi
EOF
}

run_filter_branch() {
  local target_repo="$1"; shift
  ( cd "$target_repo" && \
    git filter-branch -f --env-filter "$(rewrite_env_filter | sed -e "s/__OLD__/$OLD/g" -e "s/__NEW__/$NEW/g" -e "s/__NEW_NAME__/$NEW_NAME/g")" \
      --tag-name-filter cat -- --all >/dev/null 2>&1 )
}

count_email() {
  local repo="$1"; local email="$2"; shift 2
  # Exclude refs/original/* (filter-branch backups) so counts reflect rewritten refs only
  (cd "$repo" && {
     refs=$(git for-each-ref --format='%(refname)' refs/heads refs/tags)
     if [[ -n "$refs" ]]; then
       git log --pretty='%ae%n%ce' $refs | grep -c "$email" || true
     else
       echo 0
     fi
   })
}

if [[ $SIMULATE -eq 1 ]]; then
  tmpdir=$(mktemp -d -t rewrite-sim-XXXX)
  echo "Simulation: cloning bare mirror -> work clone" >&2
  git clone ../odyssey-backup-mirror "$tmpdir/sim" >/dev/null 2>&1 || git clone . "$tmpdir/sim" >/dev/null 2>&1
  before_old=$(count_email "$tmpdir/sim" "$OLD")
  before_new=$(count_email "$tmpdir/sim" "$NEW")
  echo "  BEFORE: commits referencing OLD email: $before_old; NEW email: $before_new" >&2
  run_filter_branch "$tmpdir/sim"
  after_old=$(count_email "$tmpdir/sim" "$OLD")
  after_new=$(count_email "$tmpdir/sim" "$NEW")
  echo "  AFTER : commits referencing OLD email: $after_old; NEW email: $after_new" >&2
  if [[ $after_old -eq 0 ]]; then
    echo "SIMULATION SUCCESS: OLD email removed in rewritten history" >&2
  else
    echo "SIMULATION WARNING: OLD email still present" >&2
  fi
  echo "Temporary simulation directory: $tmpdir/sim" >&2
fi

if [[ $RUN -eq 0 ]]; then
  if [[ $SIMULATE -eq 0 ]]; then
    echo "(No action taken yet. Use --simulate for a dry preview or --run to rewrite.)" >&2
  fi
  exit 0
fi

if [[ $RUN -eq 1 ]]; then
  if [[ $FORCE -eq 0 ]]; then
    read -r -p "CONFIRM destructive rewrite of local history (yes/NO): " ans
    if [[ "$ans" != "yes" ]]; then
      echo "Aborted." >&2; exit 1
    fi
  fi
  echo "Rewriting history in-place via filter-branch..." >&2
  run_filter_branch "."
  git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin || true
  git reflog expire --all --expire=now || true
  git gc --prune=now --aggressive || true
  post_old=$(count_email "." "$OLD")
  post_new=$(count_email "." "$NEW")
  echo "Post-rewrite counts: OLD=$post_old NEW=$post_new" >&2
  if [[ $post_old -eq 0 ]]; then
    echo "SUCCESS: Old email fully removed from commit metadata." >&2
  else
    echo "WARNING: Some commits still reference old email (investigate)." >&2
  fi
  echo
  echo "Next steps:" >&2
  echo "  1. Force push: git push --force --tags origin $DEFAULT_BRANCH" >&2
  echo "  2. Teammates: fresh clone OR 'git fetch origin && git reset --hard origin/$DEFAULT_BRANCH'" >&2
  echo "  3. Optional .mailmap entry: '$NEW_NAME <$NEW> <$OLD>'" >&2
fi
