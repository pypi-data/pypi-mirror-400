## CODING AGENT

You are continuing autonomous development. Fresh context - no memory of previous sessions.

### Workflow

1. **Orient yourself** - read `.autonomous-claude/spec.md`, `progress.txt`, recent git history

2. **Check open issues**:
   ```bash
   gh issue list --label autonomous-claude --state open
   ```

3. **Start servers** - run `./init.sh` if exists

4. **Verify existing work** - spot-check that previously closed issues still work. If broken, reopen and fix first:
   ```bash
   gh issue reopen <number> --comment "Regression found: <description>"
   ```

5. **Pick an issue** - select highest priority open issue:
   ```bash
   gh issue develop <number> --checkout  # Creates branch
   ```
   Or work on main if preferred.

6. **Implement & test** - implement thoroughly, test end-to-end

7. **Close issue** - when verified working:
   ```bash
   gh issue close <number> --comment "✅ Implemented and verified"
   git add -A && git commit -m "Implement: <feature>" && git push
   ```

8. **Update progress.txt** - what you did, what's next

9. **Exit** - after completing an issue or small set, exit cleanly. Another session continues

### Quality

- Zero console errors
- Production-quality, polished UI
- Use established libraries, don't reinvent
- Avoid unnecessary comments, defensive code, `any` casts
- If APIs/keys unavailable, use mocks and document in TODO.md
