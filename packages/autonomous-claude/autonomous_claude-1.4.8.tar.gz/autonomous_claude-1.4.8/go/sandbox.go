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

type Sandbox struct {
	ProjectDir  string
	MemoryLimit string
	CPULimit    float64
	Image       string
	Tag         string
}

func NewSandbox(projectDir string, cfg *Config) *Sandbox {
	tag := cfg.SandboxTag
	if tag == "" || tag == "dev" {
		tag = "latest"
	}
	return &Sandbox{
		ProjectDir:  projectDir,
		MemoryLimit: cfg.SandboxMemoryLimit,
		CPULimit:    cfg.SandboxCPULimit,
		Image:       cfg.SandboxImage,
		Tag:         tag,
	}
}

func (s *Sandbox) EnsureImage() error {
	// Check if image exists locally
	if s.imageExists(s.Tag) {
		return nil
	}

	// Try to pull
	fmt.Fprintf(os.Stderr, "Pulling %s:%s...\n", s.Image, s.Tag)
	if err := s.pullImage(s.Tag); err == nil {
		return nil
	}

	// Fall back to latest
	if s.Tag != "latest" {
		if s.imageExists("latest") {
			s.Tag = "latest"
			return nil
		}
		if err := s.pullImage("latest"); err == nil {
			s.Tag = "latest"
			return nil
		}
	}

	return fmt.Errorf("failed to pull image %s:%s", s.Image, s.Tag)
}

func (s *Sandbox) imageExists(tag string) bool {
	cmd := exec.Command("docker", "images", "-q", fmt.Sprintf("%s:%s", s.Image, tag))
	output, err := cmd.Output()
	return err == nil && len(strings.TrimSpace(string(output))) > 0
}

func (s *Sandbox) pullImage(tag string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()
	cmd := exec.CommandContext(ctx, "docker", "pull", fmt.Sprintf("%s:%s", s.Image, tag))
	cmd.Stdout = os.Stderr
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func (s *Sandbox) Run(claudeArgs []string, timeout int) (string, error) {
	if err := s.EnsureImage(); err != nil {
		return "", err
	}

	args := s.buildCommand(claudeArgs)

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeout)*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "docker", args...)
	output, err := cmd.CombinedOutput()
	return string(output), err
}

func (s *Sandbox) buildCommand(claudeArgs []string) []string {
	args := []string{
		"run", "--rm",
		fmt.Sprintf("--memory=%s", s.MemoryLimit),
		fmt.Sprintf("--cpus=%f", s.CPULimit),
	}

	// Mount project directory
	args = append(args, "-v", fmt.Sprintf("%s:/workspace:rw", s.ProjectDir))

	// Mount Claude config files
	home, _ := os.UserHomeDir()
	claudeDir := filepath.Join(home, ".claude")

	mounts := []struct {
		src  string
		dest string
		mode string
	}{
		{".credentials.json", ".credentials.json", "rw"},
		{"settings.json", "settings.json", "ro"},
		{"settings.local.json", "settings.local.json", "ro"},
		{"CLAUDE.md", "CLAUDE.md", "ro"},
		{"skills", "skills", "rw"},
		{"plugins", "plugins", "ro"},
	}

	for _, m := range mounts {
		srcPath := filepath.Join(claudeDir, m.src)
		if _, err := os.Stat(srcPath); err == nil {
			args = append(args, "-v", fmt.Sprintf("%s:/home/node/.claude/%s:%s", srcPath, m.dest, m.mode))
		}
	}

	// Mount gh config
	ghConfig := filepath.Join(home, ".config", "gh")
	if _, err := os.Stat(ghConfig); err == nil {
		args = append(args, "-v", fmt.Sprintf("%s:/home/node/.config/gh:rw", ghConfig))
	}

	// Pass GH_TOKEN for keyring-stored tokens
	if token := getGhToken(); token != "" {
		args = append(args, "-e", fmt.Sprintf("GH_TOKEN=%s", token))
	}

	// Container settings
	args = append(args,
		"-w", "/workspace",
		"-e", "HOME=/home/node",
		"-e", "USER=node",
		"--network", "bridge",
		"--cap-drop=ALL",
		"--security-opt=no-new-privileges",
		fmt.Sprintf("%s:%s", s.Image, s.Tag),
	)

	// Claude CLI args
	args = append(args, claudeArgs...)

	return args
}

func isDockerRunning() bool {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "docker", "info")
	return cmd.Run() == nil
}
