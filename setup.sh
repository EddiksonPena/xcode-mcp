#!/bin/bash
# Xcode MCP Server Setup Script
# This script installs all dependencies and sets up the MCP server for use with Cursor

set -e  # Exit on error

echo "🧠 Xcode MCP Server Setup"
echo "========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ This script is designed for macOS only${NC}"
    exit 1
fi

# Check for conda
echo "📦 Checking for Conda..."
if ! command -v conda &> /dev/null; then
    echo -e "${YELLOW}⚠️  Conda not found. Installing Miniconda...${NC}"
    echo "Please install Miniconda from: https://docs.conda.io/en/latest/miniconda.html"
    echo "Or run: brew install miniconda"
    exit 1
fi
echo -e "${GREEN}✅ Conda found${NC}"

# Check for Ollama (optional but recommended)
echo ""
echo "🤖 Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama not found. Installing via Homebrew...${NC}"
    if command -v brew &> /dev/null; then
        brew install ollama
        echo -e "${GREEN}✅ Ollama installed${NC}"
        echo -e "${YELLOW}💡 Start Ollama with: ollama serve${NC}"
    else
        echo -e "${YELLOW}⚠️  Homebrew not found. Please install Ollama manually from: https://ollama.ai${NC}"
    fi
else
    echo -e "${GREEN}✅ Ollama found${NC}"
    # Check if qwen3-coder:30b is installed
    if ollama list | grep -q "qwen3-coder:30b"; then
        echo -e "${GREEN}✅ qwen3-coder:30b model found${NC}"
    else
        echo -e "${YELLOW}⚠️  qwen3-coder:30b not found. Pulling model...${NC}"
        ollama pull qwen3-coder:30b
        echo -e "${GREEN}✅ Model downloaded${NC}"
    fi
fi

# Create conda environment
echo ""
echo "🐍 Creating Conda environment..."
if conda env list | grep -q "xcode-mcp"; then
    echo -e "${YELLOW}⚠️  Environment 'xcode-mcp' already exists. Updating...${NC}"
    conda env update -f environment.yml --prune
else
    conda env create -f environment.yml
fi
echo -e "${GREEN}✅ Conda environment ready${NC}"

# Activate environment and verify installation
echo ""
echo "🔍 Verifying installation..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate xcode-mcp

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# Verify packages
echo "📚 Checking installed packages..."
REQUIRED_PACKAGES=("fastapi" "uvicorn" "ollama" "openai" "requests" "pydantic")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $package"
    else
        echo -e "  ${RED}❌${NC} $package (missing)"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Some packages are missing. Installing...${NC}"
    pip install "${MISSING_PACKAGES[@]}"
fi

# Create config directory
echo ""
echo "⚙️  Setting up configuration..."
CONFIG_DIR="$HOME/.xcode-mcp"
mkdir -p "$CONFIG_DIR"
echo -e "${GREEN}✅ Config directory created: $CONFIG_DIR${NC}"

# Check for API keys
echo ""
echo "🔑 Checking API keys..."
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  DEEPSEEK_API_KEY not set${NC}"
    echo "   To use DeepSeek, add to your ~/.zshrc:"
    echo "   export DEEPSEEK_API_KEY=\"your-api-key-here\""
else
    echo -e "${GREEN}✅ DEEPSEEK_API_KEY is set${NC}"
fi

# Test server import
echo ""
echo "🧪 Testing server setup..."
if python -c "from src.server_http import app; from src.tool_registry import get_registry; registry = get_registry(); print(f'✅ {len(registry.tools)} tools loaded')" 2>/dev/null; then
    echo -e "${GREEN}✅ Server imports successfully${NC}"
else
    echo -e "${RED}❌ Server import failed${NC}"
    exit 1
fi

# Create startup script
echo ""
echo "📝 Creating startup script..."
cat > start_server.sh << 'EOF'
#!/bin/bash
# Start Xcode MCP Server

cd "$(dirname "$0")"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate xcode-mcp

echo "🚀 Starting Xcode MCP Server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📖 API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn src.server_http:app --host 0.0.0.0 --port 8000
EOF

chmod +x start_server.sh
echo -e "${GREEN}✅ Startup script created: ./start_server.sh${NC}"

# Add to Cursor MCP configuration
echo ""
echo "🎯 Adding to Cursor MCP configuration..."
CURSOR_CONFIG_FILE="$HOME/.cursor/mcp.json"
PROJECT_DIR="$(pwd)"

# Check if mcp.json exists
if [ ! -f "$CURSOR_CONFIG_FILE" ]; then
    echo "Creating new Cursor MCP config file..."
    cat > "$CURSOR_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "xcode-mcp": {
      "command": "$PROJECT_DIR/start_server.sh",
      "args": [],
      "env": {
        "DEEPSEEK_API_KEY": "${DEEPSEEK_API_KEY:-}"
      }
    }
  }
}
EOF
    echo -e "${GREEN}✅ Created Cursor config: $CURSOR_CONFIG_FILE${NC}"
else
    # Check if xcode-mcp already exists
    if grep -q '"xcode-mcp"' "$CURSOR_CONFIG_FILE"; then
        echo -e "${YELLOW}⚠️  xcode-mcp already exists in config. Updating...${NC}"
        # Use Python to safely update JSON
        python3 << PYTHON_SCRIPT
import json
import sys

config_file = "$CURSOR_CONFIG_FILE"
project_dir = "$PROJECT_DIR"
deepseek_key = "${DEEPSEEK_API_KEY:-}"

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Update or add xcode-mcp
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"]["xcode-mcp"] = {
        "command": f"{project_dir}/start_server.sh",
        "args": [],
        "env": {
            "DEEPSEEK_API_KEY": deepseek_key
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Updated Cursor MCP config")
except Exception as e:
    print(f"❌ Error updating config: {e}")
    sys.exit(1)
PYTHON_SCRIPT
    else
        echo -e "${YELLOW}⚠️  Adding xcode-mcp to existing config...${NC}"
        # Use Python to safely add to JSON
        python3 << PYTHON_SCRIPT
import json
import sys

config_file = "$CURSOR_CONFIG_FILE"
project_dir = "$PROJECT_DIR"
deepseek_key = "${DEEPSEEK_API_KEY:-}"

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"]["xcode-mcp"] = {
        "command": f"{project_dir}/start_server.sh",
        "args": [],
        "env": {
            "DEEPSEEK_API_KEY": deepseek_key
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Added xcode-mcp to Cursor MCP config")
except Exception as e:
    print(f"❌ Error updating config: {e}")
    sys.exit(1)
PYTHON_SCRIPT
    fi
    echo -e "${GREEN}✅ Updated: $CURSOR_CONFIG_FILE${NC}"
fi

echo -e "${YELLOW}💡 Restart Cursor for the MCP server to be recognized${NC}"

# Summary
echo ""
echo "========================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "========================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the server:"
echo "   ./start_server.sh"
echo ""
echo "2. Or use the run script:"
echo "   ./run_server.sh"
echo ""
echo "3. Test the server:"
echo "   curl http://localhost:8000"
echo "   curl http://localhost:8000/tools"
echo ""
echo "4. Connect from Cursor:"
echo "   - The MCP config has been created at: $CURSOR_CONFIG_DIR/xcode-mcp.json"
echo "   - Restart Cursor to load the MCP server"
echo "   - The server will start automatically when Cursor connects"
echo ""
echo "5. Set your DeepSeek API key (optional):"
echo "   export DEEPSEEK_API_KEY=\"your-api-key-here\""
echo "   Add this to your ~/.zshrc for persistence"
echo ""
echo "📖 Documentation:"
echo "   - Main README: README.md"
echo "   - LLM Guide: README_LLM.md"
echo ""

