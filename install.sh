#!/bin/bash

# SSTInator - Global Installation Script
# Installs all engine dependencies (Python, Node.js, PHP, Ruby, Java, Go)

# --- Terminal Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Installing SSTInator (Global Setup) ===${NC}"

# --- Helper function ---
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Python ---
echo -e "\n${BLUE}Installing Python dependencies...${NC}"
if [ -f "engines/python/requirements.txt" ]; then
    python3 -m pip install --user -r engines/python/requirements.txt || \
    python3 -m pip install -r engines/python/requirements.txt

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Python dependencies installed successfully${NC}"
    else
        echo -e "${RED}✗ Python installation failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Missing requirements.txt, skipping Python${NC}"
fi

# --- Node.js ---
if command_exists npm; then
    echo -e "\n${BLUE}Installing Node.js dependencies...${NC}"
    if [ -d "engines/node" ]; then
        cd engines/node
        npm install --silent
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Node.js dependencies installed successfully${NC}"
        else
            echo -e "${RED}✗ Node.js installation failed${NC}"
        fi
        cd ../..
    fi
else
    echo -e "${YELLOW}⚠ npm not found, skipping Node.js${NC}"
fi

# --- PHP ---
if command_exists composer; then
    echo -e "\n${BLUE}Installing PHP dependencies...${NC}"
    if [ -d "engines/php" ]; then
        cd engines/php
        composer install --quiet
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ PHP dependencies installed successfully${NC}"
        else
            echo -e "${RED}✗ PHP installation failed${NC}"
        fi
        cd ../..
    fi
else
    echo -e "${YELLOW}⚠ Composer not found, skipping PHP${NC}"
fi

# --- Ruby ---
if command_exists bundle; then
    echo -e "\n${BLUE}Installing Ruby dependencies...${NC}"
    if [ -d "engines/ruby" ]; then
        cd engines/ruby
        bundle install --quiet
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Ruby dependencies installed successfully${NC}"
        else
            echo -e "${RED}✗ Ruby installation failed${NC}"
        fi
        cd ../..
    fi
else
    echo -e "${YELLOW}⚠ Bundler not found, skipping Ruby${NC}"
fi

# --- Java ---
if command_exists mvn; then
    echo -e "\n${BLUE}Installing Java dependencies...${NC}"
    if [ -d "engines/java" ]; then
        cd engines/java
        mvn clean install -q
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Java built successfully${NC}"
        else
            echo -e "${RED}✗ Java build failed${NC}"
        fi
        cd ../..
    fi
else
    echo -e "${YELLOW}⚠ Maven not found, skipping Java${NC}"
fi

# --- Go ---
if command_exists go; then
    echo -e "\n${BLUE}Installing Go dependencies...${NC}"
    if [ -d "engines/go" ]; then
        cd engines/go
        go mod tidy
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Go dependencies fetched successfully${NC}"
        else
            echo -e "${RED}✗ Go dependency setup failed${NC}"
        fi
        cd ../..
    fi
else
    echo -e "${YELLOW}⚠ Go not found, skipping Go${NC}"
fi

# --- Make launchers executable ---
chmod +x main.py


# --- Done ---
echo -e "\n${BLUE}=== Installation Complete ===${NC}"
echo -e "${GREEN}SSTInator is ready to guess!${NC}"
echo -e "\n${RED}⚠ WARNING: This tool is for legal, ethical, and educational purposes only.${NC}"

exit 0
