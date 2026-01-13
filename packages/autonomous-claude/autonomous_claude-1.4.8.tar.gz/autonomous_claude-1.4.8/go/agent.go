package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

type Agent struct {
	ProjectDir  string
	Model       string
	Timeout     int
	MaxSessions int
	UseSandbox  bool
	Config      *Config
}

func (a *Agent) Run(instructions string, isNew bool) error {
	// Generate spec
	fmt.Fprintf(os.Stderr, "Generating spec...\n")
	specType := "app"
	if !isNew {
		specType = "task"
	}
	spec, err := generateSpec(a.ProjectDir, instructions, specType, a.Config.SpecTimeout)
	if err != nil {
		return fmt.Errorf("failed to generate spec: %w", err)
	}

	fmt.Fprintf(os.Stderr, "\n%s\n\n", spec)

	// Write spec
	if err := writeSpec(a.ProjectDir, spec); err != nil {
		return fmt.Errorf("failed to write spec: %w", err)
	}

	// Ensure GitHub repo
	if err := ensureRepo(a.ProjectDir, true); err != nil {
		return fmt.Errorf("failed to setup repo: %w", err)
	}

	// Run initializer session
	fmt.Fprintf(os.Stderr, "Setting up project...\n")
	var prompt string
	if isNew {
		prompt = initializerPrompt()
	} else {
		prompt = enhancementPrompt()
	}

	if _, err := a.runSession(prompt, "initializer"); err != nil {
		return fmt.Errorf("initializer failed: %w", err)
	}

	// Run coding sessions
	return a.runCodingLoop()
}

func (a *Agent) Continue() error {
	issues, err := getOpenIssues(a.ProjectDir)
	if err != nil {
		return fmt.Errorf("failed to get issues: %w", err)
	}

	if len(issues) == 0 {
		fmt.Fprintf(os.Stderr, "No open issues to work on.\n")
		return nil
	}

	fmt.Fprintf(os.Stderr, "Found %d open issues.\n", len(issues))
	return a.runCodingLoop()
}

func (a *Agent) runCodingLoop() error {
	for session := 1; session <= a.MaxSessions; session++ {
		issues, err := getOpenIssues(a.ProjectDir)
		if err != nil {
			return fmt.Errorf("failed to get issues: %w", err)
		}

		if len(issues) == 0 {
			fmt.Fprintf(os.Stderr, "All issues completed!\n")
			return nil
		}

		issue := issues[0]
		fmt.Fprintf(os.Stderr, "\n[Session %d/%d] Working on #%d: %s\n",
			session, a.MaxSessions, issue.Number, issue.Title)

		prompt := codingPrompt(issue.Number, issue.Title)
		output, err := a.runSession(prompt, fmt.Sprintf("session-%d", session))
		if err != nil {
			fmt.Fprintf(os.Stderr, "Session error: %v\n", err)
			continue
		}

		// Check if issue was closed
		if strings.Contains(output, "Issue closed") || strings.Contains(output, "gh issue close") {
			fmt.Fprintf(os.Stderr, "Issue #%d completed.\n", issue.Number)
		}
	}

	return fmt.Errorf("max sessions (%d) reached", a.MaxSessions)
}

func (a *Agent) runSession(prompt string, name string) (string, error) {
	// Create logs directory
	logsDir := filepath.Join(a.ProjectDir, ".autonomous-claude", "logs")
	os.MkdirAll(logsDir, 0755)

	logFile := filepath.Join(logsDir, fmt.Sprintf("%s-%s.log", name, time.Now().Format("20060102-150405")))

	var sandbox *Sandbox
	if a.UseSandbox {
		sandbox = NewSandbox(a.ProjectDir, a.Config)
	}

	output, err := runClaude(a.ProjectDir, prompt, a.Model, a.Config.MaxTurns, a.Timeout, sandbox)

	// Write log
	os.WriteFile(logFile, []byte(output), 0644)

	// Print output
	fmt.Print(output)

	return output, err
}

func initializerPrompt() string {
	return `You are setting up a new project for autonomous development.

## Your Tasks

1. **Read the specification** from .claude/CLAUDE.md

2. **Create GitHub Issues** for each testable feature:
   - Use label: autonomous-claude
   - Include acceptance criteria
   - Scale complexity appropriately

3. **Create init.sh** - Script to install dependencies and start dev server

4. **Create project structure** - Based on tech stack from spec

5. **Commit and push** with message: "Initial setup"

## Rules
- Create issues for ALL planned features
- Each issue should be independently testable
- Use: gh issue create --title "..." --body "..." --label autonomous-claude
- Commit all files before finishing`
}

func enhancementPrompt() string {
	return `You are adding features to an existing project.

## Your Tasks

1. **Read the specification** from .claude/CLAUDE.md

2. **Understand the existing codebase** - Check structure, patterns, tech stack

3. **Create GitHub Issues** for each new feature:
   - Use label: autonomous-claude
   - Include acceptance criteria
   - Follow existing patterns

4. **Commit and push** with message: "Add feature issues"

## Rules
- Only create issues for NEW features from the spec
- Each issue should be independently testable
- Use: gh issue create --title "..." --body "..." --label autonomous-claude`
}

func codingPrompt(issueNumber int, issueTitle string) string {
	return fmt.Sprintf(`You are implementing a feature for this project.

## Current Issue
#%d: %s

## Your Tasks

1. **Read the issue** - Run: gh issue view %d

2. **Implement the feature** - Follow existing patterns and best practices

3. **Test your work** - Verify the feature works as expected

4. **Commit and push** - Use a descriptive commit message

5. **Close the issue** - Run: gh issue close %d

## Rules
- Focus only on this issue
- Follow existing code patterns
- Test before marking complete
- Commit working code only`, issueNumber, issueTitle, issueNumber, issueNumber)
}
