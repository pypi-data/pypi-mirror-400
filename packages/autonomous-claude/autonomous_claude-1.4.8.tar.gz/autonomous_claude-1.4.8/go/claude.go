package main

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

func commandExists(name string) bool {
	_, err := exec.LookPath(name)
	return err == nil
}

func runClaude(projectDir string, prompt string, model string, maxTurns int, timeout int, sandbox *Sandbox) (string, error) {
	args := []string{
		"--print",
		"--dangerously-skip-permissions",
		"-p", prompt,
		"--max-turns", fmt.Sprintf("%d", maxTurns),
	}
	if model != "" {
		args = append(args, "--model", model)
	}

	if sandbox != nil {
		return sandbox.Run(args, timeout)
	}

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "claude", args...)
	cmd.Dir = projectDir
	output, err := cmd.CombinedOutput()
	return string(output), err
}

func generateSpec(projectDir string, description string, specType string, timeout int) (string, error) {
	var prompt string
	if specType == "app" {
		prompt = fmt.Sprintf(`Write a concise application specification for: "%s"

Check for *.md files that might contain relevant context.

Format:
# <App Name>

## Overview
One paragraph.

## Core Features
- Feature 1: Brief description
(3-6 features)

## Tech Stack
Appropriate technologies.

Output only the spec.`, description)
	} else {
		prompt = fmt.Sprintf(`Write a concise task specification for: "%s"

Check for *.md files that might contain relevant context.

Format:
# Task: <Brief Title>

## Overview
One paragraph.

## Requirements
- Key requirements

## Guidelines
- Follow existing patterns

Output only the spec.`, description)
	}

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)
	defer cancel()

	args := []string{
		"--print",
		"-p", prompt,
		"--dangerously-skip-permissions",
		"--allowedTools", "Read,Glob",
	}

	cmd := exec.CommandContext(ctx, "claude", args...)
	cmd.Dir = projectDir
	output, err := cmd.CombinedOutput()
	if err != nil {
		// Return fallback
		if specType == "app" {
			return fmt.Sprintf("# Application\n\n## Overview\n%s", description), nil
		}
		return fmt.Sprintf("# Task\n\n## Overview\n%s", description), nil
	}

	return strings.TrimSpace(string(output)), nil
}

func writeSpec(projectDir string, spec string) error {
	claudeDir := filepath.Join(projectDir, ".claude")
	if err := os.MkdirAll(claudeDir, 0755); err != nil {
		return err
	}

	claudeMD := filepath.Join(claudeDir, "CLAUDE.md")

	// Check if file exists
	existing := ""
	if data, err := os.ReadFile(claudeMD); err == nil {
		existing = string(data)
	}

	var content string
	if existing != "" && !strings.Contains(existing, "## Specification") {
		content = existing + "\n\n## Specification\n\n" + spec
	} else if existing != "" {
		// Replace existing spec section
		parts := strings.SplitN(existing, "## Specification", 2)
		content = parts[0] + "## Specification\n\n" + spec
	} else {
		content = "## Specification\n\n" + spec
	}

	return os.WriteFile(claudeMD, []byte(content), 0644)
}
