package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
)

var version = "dev"

func main() {
	var (
		continueFlag = flag.Bool("continue", false, "Continue work on existing features")
		contFlag     = flag.Bool("c", false, "Continue work on existing features (shorthand)")
		noSandbox    = flag.Bool("no-sandbox", false, "Run without Docker sandbox")
		model        = flag.String("model", "", "Claude model to use")
		modelShort   = flag.String("m", "", "Claude model (shorthand)")
		maxSessions  = flag.Int("max-sessions", 100, "Maximum number of sessions")
		maxN         = flag.Int("n", 100, "Maximum sessions (shorthand)")
		timeout      = flag.Int("timeout", 18000, "Session timeout in seconds")
		timeoutShort = flag.Int("t", 18000, "Session timeout (shorthand)")
		showVersion  = flag.Bool("version", false, "Show version")
		versionShort = flag.Bool("v", false, "Show version (shorthand)")
	)

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: autonomous-claude [OPTIONS] [INSTRUCTIONS]\n\n")
		fmt.Fprintf(os.Stderr, "Build apps autonomously with Claude Code CLI.\n\n")
		fmt.Fprintf(os.Stderr, "Options:\n")
		fmt.Fprintf(os.Stderr, "  -c, --continue      Continue work on existing features\n")
		fmt.Fprintf(os.Stderr, "  --no-sandbox        Run without Docker sandbox\n")
		fmt.Fprintf(os.Stderr, "  -m, --model         Claude model to use\n")
		fmt.Fprintf(os.Stderr, "  -n, --max-sessions  Maximum number of sessions (default: 100)\n")
		fmt.Fprintf(os.Stderr, "  -t, --timeout       Session timeout in seconds (default: 18000)\n")
		fmt.Fprintf(os.Stderr, "  -v, --version       Show version\n")
	}

	flag.Parse()

	// Handle shorthand flags
	if *contFlag {
		*continueFlag = true
	}
	if *modelShort != "" {
		*model = *modelShort
	}
	if *maxN != 100 {
		*maxSessions = *maxN
	}
	if *timeoutShort != 18000 {
		*timeout = *timeoutShort
	}
	if *versionShort {
		*showVersion = true
	}

	if *showVersion {
		fmt.Printf("autonomous-claude %s\n", version)
		os.Exit(0)
	}

	// Get project directory
	projectDir, err := os.Getwd()
	if err != nil {
		fatal("failed to get working directory: %v", err)
	}

	// Load config
	cfg := loadConfig()
	if *timeout == 18000 {
		*timeout = cfg.Timeout
	}
	if *maxSessions == 100 {
		*maxSessions = cfg.MaxSessions
	}

	// Determine sandbox mode
	useSandbox := cfg.SandboxEnabled && !*noSandbox

	// Get instructions
	instructions := ""
	if flag.NArg() > 0 {
		instructions = flag.Arg(0)
		// Check if it's a file path
		if _, err := os.Stat(instructions); err == nil {
			content, err := os.ReadFile(instructions)
			if err != nil {
				fatal("failed to read file: %v", err)
			}
			instructions = string(content)
		}
	}

	// Validate
	if !*continueFlag && instructions == "" {
		fatal("instructions required (or use --continue)")
	}

	// Check prerequisites
	if err := checkPrerequisites(useSandbox); err != nil {
		fatal("%v", err)
	}

	// Run agent
	agent := &Agent{
		ProjectDir:  projectDir,
		Model:       *model,
		Timeout:     *timeout,
		MaxSessions: *maxSessions,
		UseSandbox:  useSandbox,
		Config:      cfg,
	}

	var runErr error
	if *continueFlag {
		runErr = agent.Continue()
	} else {
		// Check for existing issues
		if hasIssues(projectDir) {
			fmt.Fprintf(os.Stderr, "Project has open issues. Use --continue to work on them.\n")
			os.Exit(1)
		}

		// Determine if new project or enhancement
		isNew := isNewProject(projectDir)
		runErr = agent.Run(instructions, isNew)
	}

	if runErr != nil {
		fatal("%v", runErr)
	}
}

func fatal(format string, args ...interface{}) {
	fmt.Fprintf(os.Stderr, "error: "+format+"\n", args...)
	os.Exit(1)
}

func isNewProject(dir string) bool {
	// Check for common project indicators
	indicators := []string{"package.json", "go.mod", "Cargo.toml", "pyproject.toml", "pom.xml", ".git"}
	for _, ind := range indicators {
		if _, err := os.Stat(filepath.Join(dir, ind)); err == nil {
			return false
		}
	}
	return true
}

func checkPrerequisites(useSandbox bool) error {
	// Check claude CLI
	if !useSandbox {
		if !commandExists("claude") {
			return fmt.Errorf("claude CLI not found. Install: npm install -g @anthropic-ai/claude-code")
		}
	}

	// Check gh CLI
	if !commandExists("gh") {
		return fmt.Errorf("gh CLI not found. Install: https://cli.github.com/")
	}

	// Check gh auth
	if !isGhAuthenticated() {
		return fmt.Errorf("gh not authenticated. Run: gh auth login")
	}

	// Check Docker if using sandbox
	if useSandbox {
		if !commandExists("docker") {
			return fmt.Errorf("docker not found. Install: https://docs.docker.com/get-docker/")
		}
		if !isDockerRunning() {
			return fmt.Errorf("docker daemon not running")
		}
	}

	return nil
}
