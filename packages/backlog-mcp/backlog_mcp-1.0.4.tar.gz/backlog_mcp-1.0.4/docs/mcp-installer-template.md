# MCP Installer Script Template

## Overview

This template allows LLMs to generate interactive installation scripts **exclusively for PyPI-published MCP servers**. The template file is typically placed in the repository of a PyPI project.

**Important**: 
- This template is **PyPI-only** for production packages on pypi.org
- MCP configuration JSONs from Cline, GitHub Copilot, or Claude Code do NOT include an `env` field by default. The LLM must ask the user about environment variables and how to handle them.
- **The MCP_NAME must match the PyPI package name exactly** for uvx to work correctly

The generated script will:

- Check system requirements (Python 3, UV)
- Support all three agents (Cline, GitHub Copilot, Claude Code)
- Handle environment variables (Fixed or Variable types)
- Handle existing MCP configurations
- Create/update the appropriate config file

## How to Use This Template

### For LLMs

**Workflow**: The template file is typically placed in a PyPI project repository. When generating an installer script, follow these steps:

1. **Parse the configuration** (if provided) or use the template structure to extract:
   - MCP name (the key in the JSON object)
   - Command and args
   - Optional fields (autoApprove, disabled, timeout, type)
   
   **Note**: MCP configs from Cline/Copilot/Claude Code do NOT include an `env` field by default.

2. **Ask the user about environment variables** BEFORE generating the script:
   
   - Ask the user if the MCP server needs any environment variables:
     ```
     Does this MCP server need any environment variables? (Yes/No)
     ```
   
   - If **Yes**: For each env var needed, ask the user:
     - **"Is this env var Fixed or Variable?"**
       - **Fixed (Cố định)**: User provides the value now → LLM hardcodes it into the script (no prompt in script)
       - **Variable (Tùy biến)**: LLM generates prompt code in the script to ask user when running
     - If **Fixed**: Ask user to provide the value immediately
     - If **Variable**: No value needed now, will be prompted during script execution
   
   - Example questions:
     ```
     I need to know about environment variables for this MCP server.
     
     Does this MCP server need environment variables? (Yes/No)
     ```
     
     If Yes:
     ```
     Please provide the environment variables:
     
     Variable 1:
     - Name: [e.g., BACKLOG_API_KEY]
     - Type: [Fixed/Variable]
     - If Fixed, value: [e.g., 1234567890876543asdfghjkl]
     
     Variable 2:
     - Name: [e.g., BACKLOG_DOMAIN]
     - Type: [Fixed/Variable]
     - If Fixed, value: [e.g., teq-dev.backlog.com]
     
     Variable 3:
     - Name: [e.g., USER_ID]
     - Type: [Fixed/Variable]
     - If Variable, no value needed (will be prompted in script)
     
     (Continue for all needed variables)
     ```
   
   - If **No**: Skip env var section entirely (script will have no env section)

3. **Replace placeholders** in the template below with actual values based on user's answers:
   - `{{MCP_NAME}}` - The MCP server name (e.g., "backlog-mcp") - **must match PyPI package name**
   - `{{MCP_DISPLAY_NAME}}` - Human-readable name (e.g., "Backlog MCP")
   - `{{COMMAND}}` - The command (usually "uvx")
   - `{{ARGS}}` - Array of command arguments
   - `{{ENV_VAR_PROMPTS}}` - Dynamic prompts for each environment variable
   - `{{ENV_VAR_VALUES}}` - Environment variable values in the Python script
   - `{{HAS_AUTO_APPROVE}}` - "true" or "false" based on config
   - `{{HAS_DISABLED}}` - "true" or "false" based on config
   - `{{HAS_TIMEOUT}}` - "true" or "false" based on config
   - `{{TIMEOUT_VALUE}}` - Timeout value if present
   - `{{HAS_TYPE}}` - "true" or "false" based on config

4. **Generate the script** by replacing all placeholders with actual values

5. **Save as** `install-{{MCP_NAME}}.sh` and make it executable

---

## Standard Template Structure

**IMPORTANT**: This template is for PyPI-published MCP servers only.

### Required Args Format

The `args` array **MUST** always follow this structure:

```json
"args": [
  "{{MCP_NAME}}@latest"
]
```

**Placeholder:**
- `{{MCP_NAME}}`: The MCP server identifier (e.g., `backlog-mcp`)
  - **Critical**: `{{MCP_NAME}}` **must match the PyPI package name exactly** for uvx to install correctly

**Conversion to bash script format:**
```bash
"{{MCP_NAME}}@latest" "ENV_START"
```

**Note**: Production mode is simple because the package name usually matches the MCP name, and pypi.org is the default package index. The `ENV_START` marker separates args from environment variables.

**Examples:**
- If PyPI package name is `backlog-mcp` → MCP_NAME must be `backlog-mcp`
- If PyPI package name is `mcp-server-sqlite` → MCP_NAME must be `mcp-server-sqlite`

---

### User Configuration Examples

**Important Notes:**
1. Real MCP configurations from Cline/Copilot/Claude Code do NOT include an `env` field. The LLM must ask the user about environment variables separately.
2. These examples show **reference configurations** that users might have. They are provided for reference only.
3. **Always use the Standard Template Structure** (see above) regardless of what the user's config shows.
4. The generated installer script will always include the complete Standard Template Structure.
5. **MCP_NAME must match the PyPI package name exactly**.

**Cline config format (example - may vary):**
```json
{
  "backlog-mcp": {
    "autoApprove": [],
    "disabled": false,
    "timeout": 60,
    "type": "stdio",
    "command": "uvx",
    "args": [
      "backlog-mcp@latest"
    ]
  }
}
```

**GitHub Copilot config format (example - may vary):**
```json
{
  "backlog-mcp": {
    "type": "stdio",
    "timeout": 60000,
    "command": "uvx",
    "args": [
      "backlog-mcp@latest"
    ]
  }
}
```

**Claude Code config format (example - may vary):**
```json
{
  "backlog-mcp": {
    "command": "uvx",
    "args": [
      "backlog-mcp@latest"
    ]
  }
}
```

### Example Output

The generated script will:
- Ask which agent (Cline/Copilot/Claude Code)
- Check if "backlog-mcp" already exists
- Prompt for environment variables (if needed)
- Write the configuration to the appropriate file

---

## Bash Script Template

```bash
#!/bin/bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
BOLD_CYAN='\033[1;36m'
BOLD_YELLOW='\033[1;33m'
BOLD_ORANGE='\033[1;38;5;166m'
NC='\033[0m' # No Color

clear
echo ""
echo -e "${BOLD_ORANGE}"
cat << "EOF"
     _____ _____ ___       _    ____ ___    _
    |_   _| ____/ _ \     / \  / ___|_ _|  / \
      | | |  __| | | |   / _ \ \___ \| |  / _ \
      | | | |__| |_| |  / ___ \ ___) | | / ___ \
      |_| |_____\__\_\ /_/   \_\____/___/_/   \_\

          {{MCP_DISPLAY_NAME}}
                Installer v1.0
EOF
echo -e "${NC}"

# ============================================
# SYSTEM REQUIREMENTS CHECK
# ============================================
echo -e "${BOLD_CYAN}🔍 Checking system requirements...${NC}"
echo ""

# Check Python 3
echo -e "${WHITE}  Checking Python 3...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}  ✓ Python 3 found: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}  ✗ Python 3 not found${NC}"
    echo -e "${YELLOW}  Please install Python 3 first: https://www.python.org/downloads/${NC}"
    exit 1
fi

# Check UV
echo -e "${WHITE}  Checking UV (Python package installer)...${NC}"
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}  ✓ UV found: ${UV_VERSION}${NC}"
elif command -v uvx &> /dev/null; then
    UV_VERSION=$(uvx --version 2>&1 | head -n 1)
    echo -e "${GREEN}  ✓ UV found: ${UV_VERSION}${NC}"
else
    echo -e "${YELLOW}  ⚠️  UV not found on your system${NC}"
    echo ""
    echo -e "${WHITE}  UV is required to run this MCP server.${NC}"
    echo -e "${CYAN}  UV is a fast Python package installer and resolver.${NC}"
    echo -e "  🔗 More info: ${BLUE}https://github.com/astral-sh/uv${NC}"
    echo ""
    echo -e "${BOLD_YELLOW}  Would you like to install UV now?${NC}"
    echo ""
    echo "  1) ✅ Yes - Install UV automatically"
    echo "  2) ❌ No  - Exit (you can install manually later)"
    echo ""

    while true; do
        read -p "  ➤ Enter your choice (1-2): " install_uv_choice

        case $install_uv_choice in
            1)
                echo ""
                echo -e "${CYAN}  📥 Installing UV...${NC}"
                echo ""

                # Detect OS and install accordingly
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    # macOS
                    echo -e "${WHITE}  Detected: macOS${NC}"

                    # Check if Homebrew is available
                    if command -v brew &> /dev/null; then
                        echo -e "${CYAN}  Installing via Homebrew...${NC}"
                        brew install uv
                    else
                        echo -e "${CYAN}  Installing via official installer...${NC}"
                        curl -LsSf https://astral.sh/uv/install.sh | sh
                    fi

                elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                    # Linux
                    echo -e "${WHITE}  Detected: Linux${NC}"
                    echo -e "${CYAN}  Installing via official installer...${NC}"
                    curl -LsSf https://astral.sh/uv/install.sh | sh

                elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
                    # Windows (Git Bash/Cygwin)
                    echo -e "${WHITE}  Detected: Windows${NC}"
                    echo -e "${CYAN}  Installing via PowerShell...${NC}"
                    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

                else
                    echo -e "${RED}  ✗ Unsupported OS: $OSTYPE${NC}"
                    echo -e "${YELLOW}  Please install UV manually: https://github.com/astral-sh/uv${NC}"
                    exit 1
                fi

                # Verify installation
                echo ""
                echo -e "${WHITE}  Verifying UV installation...${NC}"

                # Reload PATH
                export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

                if command -v uv &> /dev/null; then
                    UV_VERSION=$(uv --version 2>&1 | awk '{print $2}')
                    echo -e "${GREEN}  ✓ UV successfully installed: ${UV_VERSION}${NC}"
                elif command -v uvx &> /dev/null; then
                    UV_VERSION=$(uvx --version 2>&1 | head -n 1)
                    echo -e "${GREEN}  ✓ UV successfully installed: ${UV_VERSION}${NC}"
                else
                    echo -e "${YELLOW}  ⚠️  UV installed but not found in PATH${NC}"
                    echo -e "${CYAN}  Please restart your terminal and run this script again.${NC}"
                    echo ""
                    echo -e "${WHITE}  Or add this to your PATH:${NC}"
                    echo -e "  ${BLUE}export PATH=\"\$HOME/.cargo/bin:\$HOME/.local/bin:\$PATH\"${NC}"
                    echo ""
                    exit 1
                fi

                break
                ;;
            2)
                echo ""
                echo -e "${YELLOW}  Installation cancelled${NC}"
                echo -e "${CYAN}  💡 You can install UV manually:${NC}"
                echo -e "     ${BLUE}https://github.com/astral-sh/uv${NC}"
                echo ""
                echo -e "${WHITE}  Quick install commands:${NC}"
                echo -e "  ${CYAN}macOS/Linux:${NC}  curl -LsSf https://astral.sh/uv/install.sh | sh"
                echo -e "  ${CYAN}Windows:${NC}      powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
                echo ""
                exit 0
                ;;
            *)
                echo -e "${RED}  ✗ Invalid choice. Please enter 1 or 2.${NC}"
                ;;
        esac
    done
fi

echo ""
echo -e "${WHITE}  ════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================
# SET IDE CONSTANTS (VSCode only)
# ============================================
IDE_NAME="VS Code"
IDE_KEY="vscode"

# ============================================
# QUESTION 1: Which Agent?
# ============================================
echo -e "${BOLD_CYAN}🤖 Which AI coding agent are you using in VS Code?${NC}"
echo ""
echo "  1) 🔷 Cline"
echo "  2) 🤖 GitHub Copilot"
echo "  3) 🟣 Claude Code"
echo ""
read -p "  ➤ Enter your choice (1-3): " agent_choice

# ============================================
# AGENT CONFIGURATION DEFINITIONS
# ============================================
# Each agent has different configuration structure
# Flags control which fields to include in the final JSON

case $agent_choice in
    1)
        echo -e "${GREEN}  ✓ Cline selected${NC}"
        AGENT_NAME="Cline"
        AGENT_KEY="cline"
        CONFIG_FORMAT="standard"
        SERVERS_KEY="mcpServers"
        TIMEOUT_VALUE="{{TIMEOUT_VALUE}}"
        HAS_TYPE="{{HAS_TYPE}}"
        HAS_AUTO_APPROVE="{{HAS_AUTO_APPROVE}}"
        HAS_DISABLED="{{HAS_DISABLED}}"
        HAS_TIMEOUT="{{HAS_TIMEOUT}}"
        CONFIG_FILE="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
        ;;
    2)
        echo -e "${GREEN}  ✓ GitHub Copilot selected${NC}"
        AGENT_NAME="GitHub Copilot"
        AGENT_KEY="copilot"
        CONFIG_FORMAT="copilot"
        SERVERS_KEY="servers"
        TIMEOUT_VALUE="{{TIMEOUT_VALUE}}"
        HAS_TYPE="{{HAS_TYPE}}"
        HAS_AUTO_APPROVE="false"
        HAS_DISABLED="false"
        HAS_TIMEOUT="{{HAS_TIMEOUT}}"
        CONFIG_FILE="$HOME/Library/Application Support/Code/User/mcp.json"
        ;;
    3)
        echo -e "${GREEN}  ✓ Claude Code selected${NC}"
        AGENT_NAME="Claude Code"
        AGENT_KEY="claude-code"
        CONFIG_FORMAT="claude-code"
        SERVERS_KEY="mcpServers"
        TIMEOUT_VALUE=""
        HAS_TYPE="false"
        HAS_AUTO_APPROVE="false"
        HAS_DISABLED="false"
        HAS_TIMEOUT="false"
        CONFIG_FILE="$HOME/.claude.json"
        ;;
    *)
        echo -e "${RED}  ✗ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}  📁 Configuration file:${NC}"
echo -e "     ${BLUE}$CONFIG_FILE${NC}"

echo ""
echo -e "${WHITE}  ════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================
# Check if MCP already exists
# ============================================
OVERWRITE_MODE="false"
MCP_EXISTS="false"

# Create a temporary Python script to check if MCP exists
CHECK_RESULT=$(python3 - "$CONFIG_FILE" "$SERVERS_KEY" "{{MCP_NAME}}" << 'PYTHON_CHECK_EOF'
import json
import sys
import os

def strip_json_comments(text):
    """Remove comments from JSON-like text line by line"""
    lines = text.split('\n')
    cleaned_lines = []
    in_multiline_comment = False
    
    for line_idx, line in enumerate(lines):
        original_line = line
        # Handle multi-line comments
        if '/*' in line:
            in_multiline_comment = True
            line = line[:line.index('/*')]
        
        if in_multiline_comment:
            if '*/' in line:
                in_multiline_comment = False
                line = line[line.index('*/') + 2:]
            else:
                continue
        
        # Handle single-line comments
        if '//' in line:
            # Check if // is inside a string
            in_string = False
            quote_char = None
            for i, char in enumerate(line):
                if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                
                if not in_string and i < len(line) - 1 and line[i:i+2] == '//':
                    line = line[:i]
                    break
        
        # Remove trailing commas before } or ]
        line = line.rstrip()
        if line.endswith(','):
            temp_line = line[:-1].rstrip()
            # Check if next significant character is } or ]
            remaining = '\n'.join(lines[line_idx+1:])
            stripped_remaining = remaining.lstrip()
            if stripped_remaining and stripped_remaining[0] in '}]':
                line = temp_line
        
        if line.strip():
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

config_file = sys.argv[1]
servers_key = sys.argv[2]
mcp_name = sys.argv[3]

if not os.path.exists(config_file):
    print("NOT_EXISTS")
    sys.exit(0)

try:
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strip comments before parsing
    clean_content = strip_json_comments(content)
    config = json.loads(clean_content)

    if servers_key in config and mcp_name in config[servers_key]:
        print("EXISTS")
        # Print current config details
        mcp_config = config[servers_key][mcp_name]
        print(f"COMMAND:{mcp_config.get('command', 'N/A')}")
        print(f"TYPE:{mcp_config.get('type', 'N/A')}")
        print(f"DISABLED:{mcp_config.get('disabled', False)}")

        if 'env' in mcp_config:
            print("ENV_VARS:")
            for key, value in mcp_config['env'].items():
                if any(sensitive in key.upper() for sensitive in ['TOKEN', 'PASSWORD', 'KEY', 'SECRET', 'API_KEY']):
                    print(f"  {key}: *** (hidden)")
                else:
                    print(f"  {key}: {value}")
    else:
        print("NOT_EXISTS")
except json.JSONDecodeError as e:
    print(f"ERROR:JSON Parse Error - {str(e)}")
except Exception as e:
    print(f"ERROR:{str(e)}")
PYTHON_CHECK_EOF
)

# Parse the check result
if echo "$CHECK_RESULT" | grep -q "^EXISTS"; then
    MCP_EXISTS="true"

    echo -e "${YELLOW}⚠️  WARNING: {{MCP_NAME}} already exists!${NC}"
    echo ""
    echo -e "${WHITE}  Configuration file:${NC}"
    echo -e "  ${CYAN}$CONFIG_FILE${NC}"
    echo ""
    echo -e "${WHITE}  📋 Current MCP configuration:${NC}"

    # Display the configuration details
    echo "$CHECK_RESULT" | grep -v "^EXISTS" | while IFS= read -r line; do
        if [[ $line == COMMAND:* ]]; then
            echo "     Command: ${line#COMMAND:}"
        elif [[ $line == TYPE:* ]]; then
            echo "     Type: ${line#TYPE:}"
        elif [[ $line == DISABLED:* ]]; then
            echo "     Disabled: ${line#DISABLED:}"
        elif [[ $line == "ENV_VARS:" ]]; then
            echo "     Environment variables:"
        elif [[ $line == "  "* ]]; then
            echo "    $line"
        fi
    done

    echo ""
    echo -e "${BOLD_YELLOW}  ❓ Do you want to overwrite the existing configuration?${NC}"
    echo ""
    echo "  1) ✅ Yes - Overwrite with new configuration"
    echo "  2) ❌ No  - Cancel installation (keep existing)"
    echo ""

    while true; do
        read -p "  ➤ Enter your choice (1-2): " overwrite_choice

        case $overwrite_choice in
            1)
                echo -e "${GREEN}  ✓ Will overwrite existing configuration${NC}"
                OVERWRITE_MODE="true"
                break
                ;;
            2)
                echo ""
                echo -e "${YELLOW}  ✓ Installation cancelled${NC}"
                echo -e "${CYAN}  💡 No changes were made to your configuration.${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo -e "${RED}  ✗ Invalid choice. Please enter 1 or 2.${NC}"
                ;;
        esac
    done

    echo ""
    echo -e "${WHITE}  ════════════════════════════════════════════════════════${NC}"
    echo ""
elif echo "$CHECK_RESULT" | grep -q "^ERROR:"; then
    ERROR_MSG=$(echo "$CHECK_RESULT" | grep "^ERROR:" | cut -d: -f2-)
    echo ""
    echo -e "${RED}✗ Error: Cannot read config file${NC}"
    echo ""
    echo -e "${WHITE}  Configuration file:${NC}"
    echo -e "  ${CYAN}$CONFIG_FILE${NC}"
    echo ""
    echo -e "${WHITE}  Error details:${NC}"
    echo -e "  ${RED}$ERROR_MSG${NC}"
    echo ""
    echo -e "${YELLOW}  💡 Please fix the JSON syntax manually:${NC}"
    echo -e "     1. Open the file in your editor"
    echo -e "     2. Remove any comments (// or /* */)"
    echo -e "     3. Fix any JSON syntax errors"
    echo -e "     4. Or delete the file and run this script again"
    echo ""
    exit 1
fi

# ============================================
# QUESTION 2: Environment Variables Configuration
# ============================================
{{ENV_VAR_SECTION}}
# Note: {{ENV_VAR_SECTION}} should be replaced with:
# - If env vars are needed: The full section with prompts (see example below)
# - If no env vars needed: Empty string or comment "# No environment variables needed"

echo ""
echo -e "${WHITE}  ════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================
# Configuration Summary
# ============================================
echo -e "${BOLD_CYAN}  📊 Configuration Summary:${NC}"
echo -e "  ${WHITE}Agent:${NC}         $AGENT_NAME (VS Code)"
echo -e "  ${WHITE}Config file:${NC}   $CONFIG_FILE"
echo -e "  ${WHITE}Format:${NC}        $CONFIG_FORMAT ($SERVERS_KEY)"
if [ "$HAS_TIMEOUT" = "true" ] && [ -n "$TIMEOUT_VALUE" ]; then
    echo -e "  ${WHITE}Timeout:${NC}       $TIMEOUT_VALUE"
fi
if [ "$OVERWRITE_MODE" = "true" ]; then
    echo -e "  ${WHITE}Mode:${NC}          ${YELLOW}⚠️  OVERWRITE${NC}"
else
    echo -e "  ${WHITE}Mode:${NC}          ${GREEN}✨ NEW INSTALLATION${NC}"
fi
echo ""
echo -e "  ${WHITE}MCP Server:${NC}"
echo -e "    ${CYAN}Name:${NC}         {{MCP_NAME}}"
echo -e "    ${CYAN}Command:${NC}      {{COMMAND}}"
echo -e "    ${CYAN}Environment:${NC}  ${GREEN}✓ Configured${NC}"
echo ""
echo -e "${WHITE}  ════════════════════════════════════════════════════════${NC}"
echo ""

# Create directory
mkdir -p "$(dirname "$CONFIG_FILE")"

# Validate and merge using Python
python3 - "$CONFIG_FILE" "$OVERWRITE_MODE" "$SERVERS_KEY" "$TIMEOUT_VALUE" "$HAS_TYPE" "$HAS_AUTO_APPROVE" "$HAS_DISABLED" "$HAS_TIMEOUT" "$CONFIG_FORMAT" "{{MCP_NAME}}" "{{COMMAND}}" {{ARGS}} {{ENV_VAR_VALUES}} << 'PYTHON_EOF'
import json
import sys
import os

def strip_json_comments(text):
    """Remove comments from JSON-like text line by line"""
    lines = text.split('\n')
    cleaned_lines = []
    in_multiline_comment = False
    
    for line_idx, line in enumerate(lines):
        original_line = line
        # Handle multi-line comments
        if '/*' in line:
            in_multiline_comment = True
            line = line[:line.index('/*')]
        
        if in_multiline_comment:
            if '*/' in line:
                in_multiline_comment = False
                line = line[line.index('*/') + 2:]
            else:
                continue
        
        # Handle single-line comments
        if '//' in line:
            # Check if // is inside a string
            in_string = False
            quote_char = None
            for i, char in enumerate(line):
                if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                
                if not in_string and i < len(line) - 1 and line[i:i+2] == '//':
                    line = line[:i]
                    break
        
        # Remove trailing commas before } or ]
        line = line.rstrip()
        if line.endswith(','):
            temp_line = line[:-1].rstrip()
            # Check if next significant character is } or ]
            remaining = '\n'.join(lines[line_idx+1:])
            stripped_remaining = remaining.lstrip()
            if stripped_remaining and stripped_remaining[0] in '}]':
                line = temp_line
        
        if line.strip():
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

config_file = sys.argv[1]
overwrite_mode = sys.argv[2] == "true"
servers_key = sys.argv[3]
timeout_value = sys.argv[4]
has_type = sys.argv[5] == "true"
has_auto_approve = sys.argv[6] == "true"
has_disabled = sys.argv[7] == "true"
has_timeout = sys.argv[8] == "true"
config_format = sys.argv[9]
mcp_name = sys.argv[10]
command = sys.argv[11]

# Parse args (starting from index 12)
args = []
env_vars = {}
arg_index = 12

# Parse args until we hit the env vars marker
while arg_index < len(sys.argv):
    arg = sys.argv[arg_index]
    if arg == "ENV_START":
        arg_index += 1
        break
    args.append(arg)
    arg_index += 1

# Parse env vars (format: KEY=VALUE)
while arg_index < len(sys.argv):
    env_pair = sys.argv[arg_index]
    if '=' in env_pair:
        key, value = env_pair.split('=', 1)
        env_vars[key] = value
    arg_index += 1

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[1;36m'
WHITE = '\033[1;37m'
NC = '\033[0m'

def print_color(color, message):
    print(f"{color}{message}{NC}")

# Check if file exists
if os.path.exists(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Strip comments before parsing
        clean_content = strip_json_comments(content)
        config = json.loads(clean_content)

        # Validate structure
        if not isinstance(config, dict):
            print_color(RED, "  ✗ Error: Config file is not a valid JSON object")
            print(f"  📝 File: {config_file}")
            print(f"  🔧 Expected: {{ \"{servers_key}\": {{...}} }}")
            sys.exit(1)

        if servers_key in config:
            if not isinstance(config[servers_key], dict):
                print_color(RED, f"  ✗ Error: '{servers_key}' must be an object")
                print(f"  📝 File: {config_file}")
                sys.exit(1)
        else:
            config[servers_key] = {}

        if overwrite_mode:
            print_color(YELLOW, "  ⚠️  Overwriting existing configuration...")
        else:
            print_color(CYAN, f"  📋 Found {len(config[servers_key])} existing MCP server(s)")

    except json.JSONDecodeError as e:
        print_color(RED, "  ✗ Error: Invalid JSON in config file")
        print(f"  📝 File: {config_file}")
        print(f"  🔍 Error: {str(e)}")
        print("")
        print_color(YELLOW, "  💡 Please fix the JSON syntax manually:")
        print("     1. Open the file in your editor")
        print("     2. Remove any comments (// or /* */)")
        print("     3. Fix any JSON syntax errors")
        print("     4. Or delete the file and run this script again")
        sys.exit(1)
    except Exception as e:
        print_color(RED, f"  ✗ Error reading config: {str(e)}")
        sys.exit(1)
else:
    print_color(WHITE, "  📝 Config file not found, creating new one...")
    config = {servers_key: {}}

# Prepare the MCP configuration (base config - always included)
mcp_config = {
    "command": command,
    "args": args,
    "env": env_vars
}

# Add optional fields based on agent configuration flags
if has_type:
    mcp_config["type"] = "stdio"

if has_auto_approve:
    mcp_config["autoApprove"] = []

if has_disabled:
    mcp_config["disabled"] = False

if has_timeout and timeout_value:
    # Convert timeout based on agent type:
    # - Copilot: milliseconds (convert seconds to milliseconds)
    # - Cline: seconds (keep as is)
    # - Claude Code: not supported (has_timeout is false)
    timeout_int = int(timeout_value)
    if config_format == "copilot":
        # Copilot uses milliseconds, convert from seconds
        mcp_config["timeout"] = timeout_int * 1000
    else:
        # Cline uses seconds
        mcp_config["timeout"] = timeout_int

# Add/Update MCP server
config[servers_key][mcp_name] = mcp_config

# Write back (clean JSON without comments)
try:
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    if overwrite_mode:
        print_color(GREEN, f"  ✓ Successfully overwritten {mcp_name}")
    else:
        print_color(GREEN, f"  ✓ Successfully added {mcp_name}")

    print(f"  📝 Config: {config_file}")
    print_color(CYAN, f"  🔢 Total MCP servers: {len(config[servers_key])}")

    # List all servers
    print_color(WHITE, f"\n  📋 All MCP servers (format: {config_format}):")
    for server_name in config[servers_key].keys():
        server_config = config[servers_key][server_name]
        status = "disabled" if server_config.get('disabled', False) else "enabled"
        emoji = "🔴" if server_config.get('disabled', False) else "🟢"
        has_env = "🔐" if server_config.get('env') else ""
        marker = "⚡" if server_name == mcp_name else " "
        print(f"   {marker} {emoji} {server_name} ({status}) {has_env}")

    print_color(GREEN, "\n  ✅ Installation complete!")
    print_color(YELLOW, "  🔄 Please restart VS Code and your agent to apply changes")
    
    if config_format != "claude-code":
        print_color(CYAN, "\n  💡 Note: JSON comments were removed from the file")
        print_color(CYAN, "     (This is normal - the file will still work perfectly)")

except Exception as e:
    print_color(RED, f"  ✗ Error writing config: {str(e)}")
    sys.exit(1)
PYTHON_EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${WHITE}"
    cat << "EOF"
              ✨ Installation Success! ✨
                 🎉 All Done! 🎉
EOF
    echo -e "${NC}"
fi
```

---

## Placeholder Reference

### Required Placeholders

| Placeholder | Description | Example |
|------------|-------------|---------|
| `{{MCP_NAME}}` | The MCP server identifier (key in JSON) - **must match PyPI package name exactly** | `backlog-mcp` |
| `{{MCP_DISPLAY_NAME}}` | Human-readable name for prompts (used in banner) | `Backlog MCP` |
| `{{COMMAND}}` | Command to run | `uvx` |
| `{{ARGS}}` | Array of command arguments | See example below |
| `{{ENV_VAR_PROMPTS}}` | Bash code to prompt for each env var | See example below |
| `{{ENV_VAR_VALUES}}` | Environment variable values for Python script | See example below |
| `{{HAS_AUTO_APPROVE}}` | "true" or "false" | `true` |
| `{{HAS_DISABLED}}` | "true" or "false" | `true` |
| `{{HAS_TIMEOUT}}` | "true" or "false" | `true` |
| `{{TIMEOUT_VALUE}}` | Timeout value in seconds (script auto-converts for Copilot) or empty string | `60` (seconds, script converts to `60000` for Copilot) or `` |
| `{{HAS_TYPE}}` | "true" or "false" | `true` |

### Generating Placeholder Values

#### 1. `{{MCP_NAME}}`
Extract from the JSON key:
```json
{
  "backlog-mcp": { ... }  // ← This is the MCP name
}
```

**CRITICAL**: `{{MCP_NAME}}` **must match the PyPI package name exactly** for uvx to install correctly.

**Examples:**
- If PyPI package is `backlog-mcp` → `{{MCP_NAME}}` = `backlog-mcp`
- If PyPI package is `mcp-server-sqlite` → `{{MCP_NAME}}` = `mcp-server-sqlite`
- If PyPI package is `agent-coding-standards-mcp` → `{{MCP_NAME}}` = `agent-coding-standards-mcp`

#### 2. `{{MCP_DISPLAY_NAME}}`
Create a human-readable name:
- `backlog-mcp` → `Backlog MCP`
- `agent-coding-standards-mcp` → `Agent Coding Standards MCP`
- `mcp-server-sqlite` → `MCP Server SQLite`

#### 3. `{{COMMAND}}`
Usually `uvx`, but check the config:
```json
"command": "uvx"  // ← Use this value
```

#### 4. `{{ARGS}}`

**Always use the Standard Template Structure:**

```bash
"{{MCP_NAME}}@latest" "ENV_START"
```

**Placeholders:**
- Replace `{{MCP_NAME}}` with the MCP server identifier (e.g., `backlog-mcp`)
- **CRITICAL**: `{{MCP_NAME}}` must match the PyPI package name exactly

**Important:** 
- Always append `"ENV_START"` as a marker after all args, before the env vars.
- The `ENV_START` marker is used by the Python script to separate args from env vars.

**Example (backlog-mcp):**
```bash
"backlog-mcp@latest" "ENV_START"
```

**Example (mcp-server-sqlite):**
```bash
"mcp-server-sqlite@latest" "ENV_START"
```

#### 5. `{{ENV_VAR_SECTION}}` and `{{ENV_VAR_PROMPTS}}`

**`{{ENV_VAR_SECTION}}`** - The complete environment variables section:
- **If env vars are needed**: Generate the full section with header and prompts
- **If no env vars needed**: Leave empty or use comment `# No environment variables needed`

**`{{ENV_VAR_PROMPTS}}`** - Bash code to prompt for each environment variable (only if env vars are needed):

```bash
# For BACKLOG_API_KEY (sensitive - mask default)
DEFAULT_BACKLOG_API_KEY="o0Jl3e6snvUg9GZTy32pFpDWPP3IptoxHS2xBWHed9h7Ll3K6m91HzxTxgXrIyV3"
echo -e "${CYAN}  ℹ️  BACKLOG_API_KEY${NC}"
echo -e "${WHITE}     Default: ${YELLOW}*** (hidden)${NC}"
read -p "  🔐 Enter BACKLOG_API_KEY [Press Enter to use default]: " BACKLOG_API_KEY
if [ -z "$BACKLOG_API_KEY" ]; then
    BACKLOG_API_KEY="$DEFAULT_BACKLOG_API_KEY"
    echo -e "${GREEN}  ✓ Using default value${NC}"
else
    echo -e "${GREEN}  ✓ Custom value set (${#BACKLOG_API_KEY} characters)${NC}"
fi
echo ""

# For BACKLOG_DOMAIN (non-sensitive - show default)
DEFAULT_BACKLOG_DOMAIN="teq-dev.backlog.com"
echo -e "${CYAN}  ℹ️  BACKLOG_DOMAIN${NC}"
echo -e "${WHITE}     Default: ${BLUE}$DEFAULT_BACKLOG_DOMAIN${NC}"
read -p "  🔐 Enter BACKLOG_DOMAIN [Press Enter to use default]: " BACKLOG_DOMAIN
if [ -z "$BACKLOG_DOMAIN" ]; then
    BACKLOG_DOMAIN="$DEFAULT_BACKLOG_DOMAIN"
    echo -e "${GREEN}  ✓ Using default value${NC}"
else
    echo -e "${GREEN}  ✓ Custom value set: $BACKLOG_DOMAIN${NC}"
fi
echo ""

# For USER_ID (non-sensitive - show default)
DEFAULT_USER_ID="589678"
echo -e "${CYAN}  ℹ️  USER_ID${NC}"
echo -e "${WHITE}     Default: ${BLUE}$DEFAULT_USER_ID${NC}"
read -p "  🔐 Enter USER_ID [Press Enter to use default]: " USER_ID
if [ -z "$USER_ID" ]; then
    USER_ID="$DEFAULT_USER_ID"
    echo -e "${GREEN}  ✓ Using default value${NC}"
else
    echo -e "${GREEN}  ✓ Custom value set: $USER_ID${NC}"
fi
echo ""
```

**Example for `{{ENV_VAR_SECTION}}` when env vars are needed:**
```bash
echo -e "${BOLD_CYAN}🔑 {{MCP_DISPLAY_NAME}} Configuration${NC}"
echo ""
echo -e "${WHITE}  Please configure the following environment variables:${NC}"
echo ""

{{ENV_VAR_PROMPTS}}
```

**Example for `{{ENV_VAR_SECTION}}` when no env vars needed:**
```bash
# No environment variables needed for this MCP server
```

**Rules for generating `{{ENV_VAR_PROMPTS}}`:**
- Only generate prompts for **Variable** env vars (not Fixed vars)
- **Fixed env vars**: Do NOT generate any prompt code - they will use hardcoded values provided by user
- **Variable env vars**: Generate prompt code to ask user when script runs
- If Variable env var name contains: `TOKEN`, `PASSWORD`, `KEY`, `SECRET`, `API_KEY` → 
  - Use `read -sp` (silent password input) instead of `read -p`
  - Add `echo ""` after `read -sp` to add a newline
- Otherwise → 
  - Use `read -p` (normal input)
- **Variable env vars**: Use `while` loop to ensure value is not empty (required input)

#### 6. `{{ENV_VAR_VALUES}}`
Generate the arguments to pass to Python script. Format: `KEY1=VALUE1 KEY2=VALUE2 ...` (without ENV_START, as it's already in args).

**Include ALL env vars** (both Variable and Fixed):
- **Variable env vars**: Use the variable name (e.g., `$BACKLOG_API_KEY` - the value will be set by user input when script runs)
- **Fixed env vars**: Use the hardcoded value directly provided by user (e.g., `"BACKLOG_DOMAIN=teq-dev.backlog.com"`)

**If no env vars needed:**
- If user said "No" to needing env vars, leave this empty: `""`
- The Python script will handle empty env vars correctly

For the backlog-mcp example (assuming BACKLOG_API_KEY is Variable, BACKLOG_DOMAIN is Fixed with value "teq-dev.backlog.com", USER_ID is Variable):
```bash
"BACKLOG_API_KEY=$BACKLOG_API_KEY" "BACKLOG_DOMAIN=teq-dev.backlog.com" "USER_ID=$USER_ID"
```

Note: BACKLOG_DOMAIN uses the hardcoded value `teq-dev.backlog.com` because it's Fixed (user provided value when LLM asked), while BACKLOG_API_KEY and USER_ID use variables because they are Variable (prompted in script).

**Note:** The `ENV_START` marker should be included in `{{ARGS}}`, not here. The Python script uses `ENV_START` to know where args end and env vars begin.

#### 7. Optional Fields
Check the config for these fields and set accordingly:
- `{{HAS_AUTO_APPROVE}}`: `"true"` if `autoApprove` exists, else `"false"`
- `{{HAS_DISABLED}}`: `"true"` if `disabled` exists, else `"false"`
- `{{HAS_TIMEOUT}}`: `"true"` if `timeout` exists, else `"false"`
- `{{TIMEOUT_VALUE}}`: The timeout value if present, or empty string `""`
  - **Important**: Extract timeout value from config (usually in seconds, e.g., `60`)
  - The Python script will automatically convert based on agent type:
    - **Cline**: Uses seconds (value kept as is, e.g., `60`)
    - **GitHub Copilot**: Uses milliseconds (script converts: `60` → `60000`)
    - **Claude Code**: Not supported (timeout is not set)
- `{{HAS_TYPE}}`: `"true"` if `type` exists, else `"false"`

**Note:** For GitHub Copilot, always set:
- `HAS_AUTO_APPROVE="false"`
- `HAS_DISABLED="false"`

For Claude Code, always set:
- `HAS_TYPE="false"`
- `HAS_AUTO_APPROVE="false"`
- `HAS_DISABLED="false"`
- `HAS_TIMEOUT="false"`
- `TIMEOUT_VALUE=""`

---

## Complete Example: backlog-mcp

This example demonstrates generating an installer script for a PyPI-published MCP server (`backlog-mcp`).

### Input Configuration

**Note**: Real MCP configs do NOT include `env` field. This example shows a Cline config format that a user might provide (for reference only):

```json
{
  "backlog-mcp": {
    "autoApprove": [],
    "disabled": false,
    "timeout": 60,
    "type": "stdio",
    "command": "uvx",
    "args": [
      "backlog-mcp@latest"
    ]
  }
}
```

**Important**: The MCP name (`backlog-mcp`) matches the PyPI package name (`backlog-mcp`). This is required for uvx to work correctly.

The LLM must ask the user about environment variables separately.

### Generated Placeholder Values

```bash
MCP_NAME="backlog-mcp"  # Must match PyPI package name
MCP_DISPLAY_NAME="Backlog MCP"
COMMAND="uvx"
ARGS="backlog-mcp@latest" "ENV_START"  # MCP_NAME matches package name
HAS_AUTO_APPROVE="true"
HAS_DISABLED="true"
HAS_TIMEOUT="true"
TIMEOUT_VALUE="60"
# Note: TIMEOUT_VALUE is in seconds (60). The Python script will automatically convert:
# - For Cline: 60 seconds (kept as is)
# - For Copilot: 60000 milliseconds (60 * 1000)
HAS_TYPE="true"
```

### Example: User Answers About Env Vars

**Before generating script, LLM should ask:**
```
Does this MCP server need any environment variables? (Yes/No)
```

If Yes:
```
Please provide the environment variables:

Variable 1:
- Name: BACKLOG_API_KEY
- Type: Variable (will be prompted in script)

Variable 2:
- Name: BACKLOG_DOMAIN
- Type: Fixed
- Value: teq-dev.backlog.com

Variable 3:
- Name: USER_ID
- Type: Variable (will be prompted in script)
```

### Generated ENV_VAR_PROMPTS

Based on user's answers above, generate prompts ONLY for Variable env vars (BACKLOG_API_KEY and USER_ID). Do NOT generate prompts for Fixed vars (BACKLOG_DOMAIN):

```bash
# BACKLOG_API_KEY (Variable - sensitive, will be prompted)
echo -e "${CYAN}  ℹ️  BACKLOG_API_KEY${NC}"
echo -e "${YELLOW}     ⚠️  Required: Please enter your BACKLOG_API_KEY${NC}"
while [ -z "$BACKLOG_API_KEY" ]; do
    read -sp "  🔐 Enter BACKLOG_API_KEY: " BACKLOG_API_KEY
    echo ""
    if [ -z "$BACKLOG_API_KEY" ]; then
        echo -e "${RED}  ✗ BACKLOG_API_KEY cannot be empty. Please try again.${NC}"
    else
        echo -e "${GREEN}  ✓ BACKLOG_API_KEY set (${#BACKLOG_API_KEY} characters)${NC}"
    fi
done
echo ""

# Note: BACKLOG_DOMAIN is Fixed - no prompt generated, value will be hardcoded

# USER_ID (Variable - will be prompted)
echo -e "${CYAN}  ℹ️  USER_ID${NC}"
echo -e "${YELLOW}     ⚠️  Required: Please enter your USER_ID${NC}"
while [ -z "$USER_ID" ]; do
    read -p "  🔐 Enter USER_ID: " USER_ID
    if [ -z "$USER_ID" ]; then
        echo -e "${RED}  ✗ USER_ID cannot be empty. Please try again.${NC}"
    else
        echo -e "${GREEN}  ✓ USER_ID set: $USER_ID${NC}"
    fi
done
echo ""
```

### Generated ARGS (with ENV_START marker)

**Using Standard Template Structure:**

```bash
"backlog-mcp@latest" "ENV_START"
```

**Note**: `backlog-mcp` matches the PyPI package name exactly.

### Generated ENV_VAR_VALUES

Include all env vars (Variable vars use `$VAR_NAME`, Fixed vars use hardcoded value):
```bash
"BACKLOG_API_KEY=$BACKLOG_API_KEY" "BACKLOG_DOMAIN=teq-dev.backlog.com" "USER_ID=$USER_ID"
```

Note: 
- BACKLOG_API_KEY uses `$BACKLOG_API_KEY` because it's Variable (prompted in script)
- BACKLOG_DOMAIN uses hardcoded value `teq-dev.backlog.com` because it's Fixed (user provided value when LLM asked)
- USER_ID uses `$USER_ID` because it's Variable (prompted in script)

---

## Implementation Checklist

When generating a script from this template:

- [ ] Parse the MCP config JSON (if provided) or use template structure
- [ ] Extract MCP name from the key
- [ ] **VERIFY**: MCP_NAME matches the PyPI package name exactly
- [ ] Extract command and args: Always use **Standard Template Structure** for args
- [ ] **ASK USER about env vars**: Does the MCP server need environment variables?
- [ ] **For each env var needed**: Ask user if it's Fixed (cố định) or Variable (tùy biến)
  - If **Fixed**: Get value from user and hardcode in script
  - If **Variable**: Will be prompted in script (no value needed now)
- [ ] Determine optional fields (autoApprove, disabled, timeout, type) based on agent type
- [ ] Generate env var prompts ONLY for Variable env vars (Fixed vars use hardcoded values)
- [ ] Generate env var values string for Python script: Variable vars use `$VAR_NAME`, Fixed vars use hardcoded values
- [ ] Replace all placeholders in template
- [ ] Save as `install-{{MCP_NAME}}.sh`
- [ ] Make script executable: `chmod +x install-{{MCP_NAME}}.sh`

---

## Notes

1. **Package Name Matching**: **CRITICAL** - The `{{MCP_NAME}}` must match the PyPI package name exactly for uvx to install correctly. For example:
   - If PyPI package is `backlog-mcp` → MCP_NAME must be `backlog-mcp`
   - If PyPI package is `mcp-server-sqlite` → MCP_NAME must be `mcp-server-sqlite`
   - If PyPI package is `agent-coding-standards-mcp` → MCP_NAME must be `agent-coding-standards-mcp`

2. **Banner ASCII Art**: The banner is always the same ASCII art from `install-mcp.sh`. Only the `{{MCP_DISPLAY_NAME}}` changes in the banner.

3. **Sensitive Value Detection**: The template automatically detects sensitive values by checking if the env var name contains: `TOKEN`, `PASSWORD`, `KEY`, `SECRET`, or `API_KEY` (case-insensitive).

4. **Agent-Specific Behavior**: 
   - **Cline**: Supports all optional fields. Timeout uses **seconds** (e.g., `60` = 60 seconds)
   - **GitHub Copilot**: Doesn't support `autoApprove` or `disabled`. Timeout uses **milliseconds** (e.g., `60000` = 60 seconds). The Python script automatically converts seconds to milliseconds.
   - **Claude Code**: Doesn't support any optional fields (no timeout)

5. **Workflow**: The template file is typically placed in a PyPI project repository (90% of use cases). When generating an installer script, the LLM should parse the config structure and ask the user about environment variables.

6. **Config Format**: MCP configurations from Cline, GitHub Copilot, or Claude Code do NOT include an `env` field by default. The LLM must ask the user about environment variables separately.

7. **Environment Variables**: There are two types of env vars:
   - **Fixed (Cố định)**: User provides the value when LLM asks → LLM hardcodes it into the script (no prompt in script). Use this for static values that don't change.
   - **Variable (Tùy biến)**: LLM generates prompt code in the script to ask user when running. Use this for values that vary per installation.

8. **Error Handling**: The script includes comprehensive error handling for:
   - Missing system requirements
   - Invalid JSON in config files
   - Existing MCP configurations
   - Missing environment variables

9. **JSON Comments**: The script handles JSON files with comments (both `//` and `/* */` style) by stripping them before parsing.

10. **Important Bug Fix**: The `strip_json_comments` function uses `enumerate(lines)` instead of `lines.index(line)` to get the current line index. This prevents the `"'...' is not in list"` error that occurs when a modified line (after stripping comments) cannot be found in the original list. Always use `line_idx` from `enumerate()` when accessing `lines[line_idx+1:]` to check for trailing commas.
