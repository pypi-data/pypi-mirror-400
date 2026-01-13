package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

const issueLabel = "autonomous-claude"

type Issue struct {
	Number int    `json:"number"`
	Title  string `json:"title"`
	State  string `json:"state"`
}

func isGhAuthenticated() bool {
	cmd := exec.Command("gh", "auth", "status")
	return cmd.Run() == nil
}

func getGhToken() string {
	// Try gh auth token first (handles keyring)
	cmd := exec.Command("gh", "auth", "token")
	output, err := cmd.Output()
	if err == nil && len(output) > 0 {
		return strings.TrimSpace(string(output))
	}
	// Fall back to environment
	if token := os.Getenv("GH_TOKEN"); token != "" {
		return token
	}
	return os.Getenv("GITHUB_TOKEN")
}

func getRepoName(projectDir string) string {
	return filepath.Base(projectDir)
}

func repoExists(projectDir string) bool {
	cmd := exec.Command("gh", "repo", "view", "--json", "name")
	cmd.Dir = projectDir
	return cmd.Run() == nil
}

func createRepo(projectDir string, private bool) error {
	name := getRepoName(projectDir)
	args := []string{"repo", "create", name, "--source", ".", "--push"}
	if private {
		args = append(args, "--private")
	} else {
		args = append(args, "--public")
	}
	cmd := exec.Command("gh", args...)
	cmd.Dir = projectDir
	cmd.Stdout = os.Stderr
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func getOpenIssues(projectDir string) ([]Issue, error) {
	cmd := exec.Command("gh", "issue", "list",
		"--label", issueLabel,
		"--state", "open",
		"--json", "number,title,state",
	)
	cmd.Dir = projectDir
	output, err := cmd.Output()
	if err != nil {
		return nil, err
	}

	var issues []Issue
	if err := json.Unmarshal(output, &issues); err != nil {
		return nil, err
	}
	return issues, nil
}

func hasIssues(projectDir string) bool {
	issues, err := getOpenIssues(projectDir)
	return err == nil && len(issues) > 0
}

func createIssue(projectDir, title, body string) error {
	cmd := exec.Command("gh", "issue", "create",
		"--title", title,
		"--body", body,
		"--label", issueLabel,
	)
	cmd.Dir = projectDir
	cmd.Stdout = os.Stderr
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func closeIssue(projectDir string, number int) error {
	cmd := exec.Command("gh", "issue", "close", fmt.Sprintf("%d", number))
	cmd.Dir = projectDir
	return cmd.Run()
}

func ensureLabel(projectDir string) error {
	// Check if label exists
	cmd := exec.Command("gh", "label", "list", "--json", "name")
	cmd.Dir = projectDir
	output, err := cmd.Output()
	if err != nil {
		return nil // Might not have repo yet
	}

	var labels []struct {
		Name string `json:"name"`
	}
	if err := json.Unmarshal(output, &labels); err != nil {
		return nil
	}

	for _, l := range labels {
		if l.Name == issueLabel {
			return nil
		}
	}

	// Create label
	cmd = exec.Command("gh", "label", "create", issueLabel,
		"--description", "Managed by autonomous-claude",
		"--color", "7057ff",
	)
	cmd.Dir = projectDir
	cmd.Run() // Ignore errors
	return nil
}

func initGitRepo(projectDir string) error {
	// Check if already a git repo
	if _, err := os.Stat(filepath.Join(projectDir, ".git")); err == nil {
		return nil
	}

	cmd := exec.Command("git", "init")
	cmd.Dir = projectDir
	if err := cmd.Run(); err != nil {
		return err
	}

	// Create initial commit if no commits exist
	cmd = exec.Command("git", "rev-parse", "HEAD")
	cmd.Dir = projectDir
	if cmd.Run() != nil {
		// No commits, create initial one
		// Add all files
		cmd = exec.Command("git", "add", "-A")
		cmd.Dir = projectDir
		cmd.Run()

		// Create initial commit
		cmd = exec.Command("git", "commit", "-m", "Initial commit", "--allow-empty")
		cmd.Dir = projectDir
		cmd.Run()
	}

	return nil
}

func ensureRepo(projectDir string, private bool) error {
	if err := initGitRepo(projectDir); err != nil {
		return fmt.Errorf("git init failed: %w", err)
	}

	if !repoExists(projectDir) {
		fmt.Fprintf(os.Stderr, "Creating GitHub repo: %s\n", getRepoName(projectDir))
		if err := createRepo(projectDir, private); err != nil {
			return fmt.Errorf("failed to create repo: %w", err)
		}
	}

	ensureLabel(projectDir)
	return nil
}
