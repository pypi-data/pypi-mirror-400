## ENHANCEMENT INITIALIZER

You are adding features to an existing autonomous-claude project.

### Tasks

1. **Understand the project** - read existing spec, open/closed issues, progress.txt, recent commits:
   ```bash
   gh issue list --label autonomous-claude --state all
   ```

2. **Read new requirements** - `.autonomous-claude/spec.md` contains new requirements

3. **Check services** - verify any new external services are authenticated. Use mocks if unavailable

4. **Create new issues** - for each new feature:
   ```bash
   gh issue create --title "Feature: <description>" \
     --body "## Steps to verify
   - [ ] Step 1
   - [ ] Step 2" \
     --label "autonomous-claude"
   ```

5. **Update spec.md** - append new requirements section to existing spec

6. **Update progress.txt** - note new features added

7. **Commit & push**:
   ```bash
   git add .autonomous-claude/ && git commit -m "Add new feature issues" && git push
   ```

Do not implement features - just create issues. Coding agents handle implementation.
