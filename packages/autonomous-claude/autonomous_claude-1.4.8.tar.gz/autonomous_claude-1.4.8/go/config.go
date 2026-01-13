package main

import (
	"os"
	"path/filepath"

	"github.com/pelletier/go-toml/v2"
)

type Config struct {
	Timeout            int     `toml:"timeout"`
	MaxTurns           int     `toml:"max_turns"`
	MaxSessions        int     `toml:"max_sessions"`
	SpecTimeout        int     `toml:"spec_timeout"`
	SandboxEnabled     bool    `toml:"enabled"`
	SandboxMemoryLimit string  `toml:"memory_limit"`
	SandboxCPULimit    float64 `toml:"cpu_limit"`
	SandboxImage       string  `toml:"image"`
	SandboxTag         string  `toml:"tag"`
}

type configFile struct {
	Session struct {
		Timeout     int `toml:"timeout"`
		MaxTurns    int `toml:"max_turns"`
		MaxSessions int `toml:"max_sessions"`
		SpecTimeout int `toml:"spec_timeout"`
	} `toml:"session"`
	Sandbox struct {
		Enabled     bool    `toml:"enabled"`
		MemoryLimit string  `toml:"memory_limit"`
		CPULimit    float64 `toml:"cpu_limit"`
		Image       string  `toml:"image"`
		Tag         string  `toml:"tag"`
	} `toml:"sandbox"`
}

const defaultImage = "ghcr.io/ferdousbhai/autonomous-claude"

func loadConfig() *Config {
	cfg := &Config{
		Timeout:            18000,
		MaxTurns:           2000,
		MaxSessions:        100,
		SpecTimeout:        1800,
		SandboxEnabled:     true,
		SandboxMemoryLimit: "8g",
		SandboxCPULimit:    4.0,
		SandboxImage:       defaultImage,
		SandboxTag:         version,
	}

	// Try to load config file
	home, err := os.UserHomeDir()
	if err != nil {
		return cfg
	}

	configPath := filepath.Join(home, ".config", "autonomous-claude", "config.toml")
	data, err := os.ReadFile(configPath)
	if err != nil {
		return cfg
	}

	var file configFile
	if err := toml.Unmarshal(data, &file); err != nil {
		return cfg
	}

	// Apply config values
	if file.Session.Timeout > 0 {
		cfg.Timeout = file.Session.Timeout
	}
	if file.Session.MaxTurns > 0 {
		cfg.MaxTurns = file.Session.MaxTurns
	}
	if file.Session.MaxSessions > 0 {
		cfg.MaxSessions = file.Session.MaxSessions
	}
	if file.Session.SpecTimeout > 0 {
		cfg.SpecTimeout = file.Session.SpecTimeout
	}
	if file.Sandbox.MemoryLimit != "" {
		cfg.SandboxMemoryLimit = file.Sandbox.MemoryLimit
	}
	if file.Sandbox.CPULimit > 0 {
		cfg.SandboxCPULimit = file.Sandbox.CPULimit
	}
	if file.Sandbox.Image != "" {
		cfg.SandboxImage = file.Sandbox.Image
	}
	if file.Sandbox.Tag != "" {
		cfg.SandboxTag = file.Sandbox.Tag
	}
	// SandboxEnabled defaults to true, only set false if explicitly configured
	cfg.SandboxEnabled = file.Sandbox.Enabled || !file.Sandbox.Enabled // Keep default unless explicitly set

	return cfg
}
