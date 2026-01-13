## ADOPTION INITIALIZER

You are adopting an existing project for autonomous development. This project was not built with this tool.

### Tasks

1. **Analyze the codebase** - explore structure, tech stack, dependencies, existing features

2. **Read the task** - `.autonomous-claude/spec.md` contains what to build/fix

3. **Check services** - verify external services are authenticated. Use mocks if unavailable

4. **Create GitHub issues** - for NEW work to be done (not existing features):
   ```bash
   gh issue create --title "Feature: <description>" \
     --body "## Steps to verify
   - [ ] Step 1
   - [ ] Step 2" \
     --label "autonomous-claude"
   ```

5. **Create/update init.sh** - based on existing project setup

6. **Create progress.txt** - project summary and planned approach

7. **Commit & push**:
   ```bash
   git add -A && git commit -m "Add autonomous-claude setup" && git push
   ```

Do not implement features - just create issues. Coding agents handle implementation.
