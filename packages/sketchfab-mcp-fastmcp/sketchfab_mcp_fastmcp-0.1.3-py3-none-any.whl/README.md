[![Add to Cursor](https://fastmcp.me/badges/cursor_dark.svg)](https://fastmcp.me/MCP/Details/1607/sketchfab)
[![Add to VS Code](https://fastmcp.me/badges/vscode_dark.svg)](https://fastmcp.me/MCP/Details/1607/sketchfab)
[![Add to Claude](https://fastmcp.me/badges/claude_dark.svg)](https://fastmcp.me/MCP/Details/1607/sketchfab)
[![Add to ChatGPT](https://fastmcp.me/badges/chatgpt_dark.svg)](https://fastmcp.me/MCP/Details/1607/sketchfab)
[![Add to Codex](https://fastmcp.me/badges/codex_dark.svg)](https://fastmcp.me/MCP/Details/1607/sketchfab)
[![Add to Gemini](https://fastmcp.me/badges/gemini_dark.svg)](https://fastmcp.me/MCP/Details/1607/sketchfab)

# Sketchfab MCP

A microservice for interacting with the Sketchfab API using MCP (Model Control Protocol).

## Features

- Search for downloadable models on Sketchfab
- Download a model from Sketchfab given a UID

## Environment Variables

- `SKETCHFAB_API_TOKEN`: Your Sketchfab API token

## How to use

1. Create an Sketchfab account: https://sketchfab.com/
1. You can find your Sketchfab API Token at: https://sketchfab.com/settings/password
3. Add the following MCP server as a command in Cursor:

```bash
env SKETCHFAB_API_TOKEN=PLACEHOLDER uvx sketchfab-mcp
```

## Running with Docker

```bash
docker build -t sketchfab-mcp .
docker run -it --rm -p 8000:8000 -e SKETCHFAB_API_TOKEN=PLACEHOLDER sketchfab-mcp
```
