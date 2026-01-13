# Backlog MCP Server

## Introduction

**Backlog MCP Server** is a remote server designed to integrate the **Backlog** project management tool with AI assistants via the **Model Context Protocol (MCP)**.

The server uses **API key authentication** for secure and simple access, allowing AI assistants such as **Claude AI** and **Geniai Assistant** to access and manage tasks, projects, and issues in Backlog efficiently.

This server is **truly stateless**, meaning it does **not store session state between requests**, which enhances both security and scalability.

---

## Architecture Highlights

- Simple API key authentication with Backlog
- MCP-compliant design based on [MCP Specification (2025-06-18)]
- Stateless architecture for simplicity and scalability
- Single workspace configuration for personal use
- Supports `stdio` protocol for direct communication

---

## MCP Tools

The server provides a set of MCP tools that allow AI assistants to interact with Backlog via API. Below is the list of supported tools:

---

### `get_issue_details`

Get detailed information about a Backlog issue by its issue key.

**Parameters:**
- `issue_key` (str): The issue key in Backlog.
- `issue_title` (str, optional): The title of the Backlog issue, used for logging or reference purposes.
- `timezone` (str, default `"UTC"`): Timezone for datetime formatting.

---

### `get_user_issue_list`

Retrieve a list of issues assigned to the current user.

This tool automatically determines the current user's ID and returns only issues assigned to that user. No parameters are required.

## Running the Server Locally

### 1. Get your Backlog API key

1. Log in to your Backlog workspace
2. Go to **Personal Settings** → **API**
3. Generate a new API key
4. Copy the API key for use in configuration

### 2. Create and configure the `.env` file

Create a `.env` file in the root directory and add the following environment variables:

```env
# Backlog API Settings
BACKLOG_API_KEY=your_backlog_api_key_here
BACKLOG_DOMAIN=your-space.backlog.com
```

> **Important:**
> - Replace `your_backlog_api_key_here` with your actual Backlog API key
> - Replace `your-space.backlog.com` with your actual Backlog domain

### 3. Start the server

After configuring `.env`, run:

```bash
mise mcp
```

The server will run using stdio transport and communicate directly with MCP clients.

---

## Benefits of API Key Authentication

1. **Simplified Setup**: No OAuth flow required - just use your API key
2. **Better Performance**: Direct API calls without token introspection overhead  
3. **Easier Debugging**: Clear error messages and straightforward authentication
4. **Reduced Dependencies**: No JWT libraries or OAuth server needed
5. **Personal Use Optimized**: Perfect for individual developers and personal projects

---

## Migration from OAuth Version

If you're migrating from the OAuth version:

1. **Backup your current setup**
2. **Get your Backlog API key** (see step 1 above)
3. **Update your `.env` file** with new format (see step 2 above)
4. **Remove OAuth-related files** (if any)
5. **Test the connection** with your Backlog workspace

The migration preserves all existing MCP tools and functionality while simplifying the authentication process.

### Tag for deployment

1. MCP Resource only:
`mcp.v2.0.0-dev`

2. Both of Resource + Auth:
`v2.0.0-dev`
