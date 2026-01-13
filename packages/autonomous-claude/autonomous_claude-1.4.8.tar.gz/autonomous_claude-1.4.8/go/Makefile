VERSION ?= $(shell git describe --tags --always 2>/dev/null || echo "dev")
LDFLAGS := -ldflags "-s -w -X main.version=$(VERSION)"
BINARY := autonomous-claude
DIST := dist

.PHONY: build clean release install

build:
	go build $(LDFLAGS) -o $(BINARY) .

install: build
	mkdir -p ~/.local/bin
	cp $(BINARY) ~/.local/bin/

clean:
	rm -rf $(BINARY) $(DIST)

release: clean
	mkdir -p $(DIST)
	# Linux
	GOOS=linux GOARCH=amd64 go build $(LDFLAGS) -o $(DIST)/$(BINARY)-linux-amd64 .
	GOOS=linux GOARCH=arm64 go build $(LDFLAGS) -o $(DIST)/$(BINARY)-linux-arm64 .
	# macOS
	GOOS=darwin GOARCH=amd64 go build $(LDFLAGS) -o $(DIST)/$(BINARY)-darwin-amd64 .
	GOOS=darwin GOARCH=arm64 go build $(LDFLAGS) -o $(DIST)/$(BINARY)-darwin-arm64 .
	# Windows
	GOOS=windows GOARCH=amd64 go build $(LDFLAGS) -o $(DIST)/$(BINARY)-windows-amd64.exe .
	# Checksums
	cd $(DIST) && sha256sum * > checksums.txt
	@echo "Built release $(VERSION) in $(DIST)/"
	@ls -lh $(DIST)/
