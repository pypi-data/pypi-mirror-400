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

          Backlog MCP
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
        TIMEOUT_VALUE="60"
        HAS_TYPE="true"
        HAS_AUTO_APPROVE="true"
        HAS_DISABLED="true"
        HAS_TIMEOUT="true"
        CONFIG_FILE="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
        ;;
    2)
        echo -e "${GREEN}  ✓ GitHub Copilot selected${NC}"
        AGENT_NAME="GitHub Copilot"
        AGENT_KEY="copilot"
        CONFIG_FORMAT="copilot"
        SERVERS_KEY="servers"
        TIMEOUT_VALUE="60"
        HAS_TYPE="true"
        HAS_AUTO_APPROVE="false"
        HAS_DISABLED="false"
        HAS_TIMEOUT="true"
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
CHECK_RESULT=$(python3 - "$CONFIG_FILE" "$SERVERS_KEY" "backlog-mcp" << 'PYTHON_CHECK_EOF'
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

    echo -e "${YELLOW}⚠️  WARNING: backlog-mcp already exists!${NC}"
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
echo -e "${BOLD_CYAN}🔑 Backlog MCP Configuration${NC}"
echo ""
echo -e "${WHITE}  Please configure the following environment variables:${NC}"
echo ""

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
echo -e "    ${CYAN}Name:${NC}         backlog-mcp"
echo -e "    ${CYAN}Command:${NC}      uvx"
echo -e "    ${CYAN}Environment:${NC}  ${GREEN}✓ Configured${NC}"
echo ""
echo -e "${WHITE}  ════════════════════════════════════════════════════════${NC}"
echo ""

# Create directory
mkdir -p "$(dirname "$CONFIG_FILE")"

# Validate and merge using Python
python3 - "$CONFIG_FILE" "$OVERWRITE_MODE" "$SERVERS_KEY" "$TIMEOUT_VALUE" "$HAS_TYPE" "$HAS_AUTO_APPROVE" "$HAS_DISABLED" "$HAS_TIMEOUT" "$CONFIG_FORMAT" "backlog-mcp" "uvx" "backlog-mcp@latest" "ENV_START" "BACKLOG_API_KEY=$BACKLOG_API_KEY" "BACKLOG_DOMAIN=teq-dev.backlog.com" << 'PYTHON_EOF'
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
    mcp_config["autoApprove"] = ["get_issue_details", "get_user_issue_list"]

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
