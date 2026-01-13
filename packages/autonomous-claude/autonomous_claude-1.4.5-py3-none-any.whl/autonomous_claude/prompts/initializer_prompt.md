## INITIALIZER AGENT

You are setting up a new project for autonomous development.

### Tasks

1. **Understand what to build** - the project specification is in `.claude/CLAUDE.md` (auto-loaded)

2. **Check external services** - if the spec requires services (Modal, Convex, Firebase, etc.), verify authentication. If unavailable, use mocks and document in `TODO.md`

3. **Create GitHub issues** - for each testable feature:
   ```bash
   gh issue create --title "Feature: User can create todo" \
     --body "## Steps to verify
   - [ ] Click 'New' button
   - [ ] Enter todo text
   - [ ] Todo appears in list"
   ```
   Scale complexity appropriately. Create issues for ALL planned features.

4. **Create `init.sh`** - install deps, start dev server

5. **Create project structure** - based on tech stack

6. **Initialize git & push**:
   ```bash
   git add -A && git commit -m "Initial setup" && git push
   ```
