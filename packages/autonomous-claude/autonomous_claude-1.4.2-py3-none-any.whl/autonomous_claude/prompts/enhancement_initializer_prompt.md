## ENHANCEMENT INITIALIZER

You are adding features to an existing project.

### Tasks

1. **Understand the project** - read open/closed issues, CLAUDE.md (auto-loaded), recent commits:
   ```bash
   gh issue list --state all
   ```

2. **New requirements** - new feature requirements are appended to `.claude/CLAUDE.md` (auto-loaded)

3. **Check services** - verify any new external services are authenticated. Use mocks if unavailable

4. **Create new issues** - for each new feature:
   ```bash
   gh issue create --title "Feature: <description>" \
     --body "## Steps to verify
   - [ ] Step 1
   - [ ] Step 2"
   ```

5. **Commit & push**:
   ```bash
   git add -A && git commit -m "Add new feature issues" && git push
   ```

Do not implement features - just create issues. Coding agents handle implementation.
