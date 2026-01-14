---
description: Create a branch from current HEAD if needed, push, and create a PR based on diff from origin/main
allowed-tools: Bash(git:*), Bash(gh:*)
---

# Create PR from Current Changes

## Context

Current branch: !`git branch --show-current`
Default branch: !`gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'`
Unpushed commits: !`git log origin/main..HEAD --oneline 2>/dev/null || echo "none"`

## Task

Create a pull request for the current changes. Follow these steps:

1. **Fetch latest from origin**: Run `git fetch origin` to ensure we have the latest remote state.

2. **Check if branch needs to be created**: If the current branch is `main` or `master`, you need to create a new branch:
   - Analyze the diff from `origin/main` (or `origin/master`) to understand what changes were made
   - Generate a descriptive branch name based on the changes (use kebab-case, e.g., `fix-typo-in-readme`, `add-depth-visualization`)
   - Create and switch to the new branch: `git checkout -b <branch-name>`

3. **Push the branch**: Push with upstream tracking: `git push -u origin <branch-name>`

4. **Create the PR**: Use `gh pr create` with:
   - A clear, descriptive title summarizing the changes
   - A body that describes what the PR does (use the commit messages and diff as context)
   - Target the main/master branch as base
   - Use this format for the body:
     ```
     ## Summary
     <1-3 bullet points describing the changes>

     ## Test plan
     <How to verify the changes work>
     ```

5. **Return the PR URL** to the user.

If the branch already exists and is pushed, just create the PR. If a PR already exists for this branch, inform the user and provide the existing PR URL.
