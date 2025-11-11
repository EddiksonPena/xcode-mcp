#!/bin/bash
# Script to create GitHub repository and push code
# This script helps set up the GitHub repository after it's created via GitHub MCP

set -e

REPO_NAME="xcode-mcp"
GITHUB_USER=""  # Will be set from git config or user input

echo "🚀 GitHub Repository Setup Script"
echo "=================================="
echo ""

# Get GitHub username
if command -v gh &> /dev/null; then
    GITHUB_USER=$(gh api user -q .login 2>/dev/null || echo "")
fi

if [ -z "$GITHUB_USER" ]; then
    # Try to get from git config
    GITHUB_USER=$(git config user.name 2>/dev/null || echo "")
    if [ -z "$GITHUB_USER" ]; then
        read -p "Enter your GitHub username: " GITHUB_USER
    fi
fi

echo "GitHub Username: $GITHUB_USER"
echo "Repository Name: $REPO_NAME"
echo ""

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo "⚠️  Remote 'origin' already exists:"
    git remote get-url origin
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
    else
        echo "Keeping existing remote. Exiting."
        exit 0
    fi
fi

# Add remote
echo "📡 Adding GitHub remote..."
git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

# Set main branch
echo "🌿 Setting main branch..."
git branch -M main 2>/dev/null || echo "Already on main branch"

# Check if repository exists on GitHub
echo "🔍 Checking if repository exists on GitHub..."
if git ls-remote --exit-code origin &> /dev/null; then
    echo "✅ Repository exists on GitHub"
    echo ""
    echo "📤 Pushing code to GitHub..."
    git push -u origin main
    echo ""
    echo "✅ Success! Repository pushed to GitHub"
    echo "🔗 https://github.com/${GITHUB_USER}/${REPO_NAME}"
else
    echo "⚠️  Repository not found on GitHub"
    echo ""
    echo "Please create the repository first using one of these methods:"
    echo ""
    echo "1. Using GitHub MCP in Cursor:"
    echo "   Ask Cursor: 'Create a GitHub repository named xcode-mcp with description \"Comprehensive MCP server for Xcode development automation\" and make it public'"
    echo ""
    echo "2. Using GitHub Web Interface:"
    echo "   Go to: https://github.com/new"
    echo "   Name: $REPO_NAME"
    echo "   Description: Comprehensive MCP server for Xcode development automation"
    echo "   Visibility: Public"
    echo "   Don't initialize with README (we already have one)"
    echo ""
    echo "3. After creating, run this script again to push the code"
    echo ""
    exit 1
fi

