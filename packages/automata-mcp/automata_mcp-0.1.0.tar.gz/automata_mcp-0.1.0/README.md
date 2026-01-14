# Automata MCP

A Model Context Protocol (MCP) server that provides browser automation capabilities using Playwright.

## Features

- 🌐 Full browser automation through MCP
- 🎯 Smart element detection and interaction
- 📝 Text extraction and form filling
- 🔍 Web scraping capabilities
- 🚀 Easy integration with Claude Desktop

## Installation

```bash
pip install automata-mcp
```

The package will automatically install Playwright and download the Chromium browser on first run.

## Usage with Claude Desktop

Add to your Claude Desktop config file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "automata": {
      "command": "automata-mcp"
    }
  }
}
```

Restart Claude Desktop and the browser automation tools will be available.

## Available Tools

- `open_browser` - Opens browser and navigates to URL
- `navigate_to` - Navigate to a new URL
- `get_actionable_elements` - Get list of clickable elements
- `click_element` - Click an element
- `type_text` - Type into input fields
- `extract_text_from_page` - Extract all visible text
- `get_element_text` - Get text from specific element
- `scroll_page` - Scroll in any direction
- `finish` - Close browser and cleanup

## Example Prompts for Claude

- "Open amazon.com and search for wireless headphones"
- "Go to wikipedia.org and extract the main article text"
- "Navigate to example.com and click the login button"

## Development

```bash
git clone https://github.com/yourusername/automata-mcp
cd automata-mcp
pip install -e ".[dev]"
```

## License

MIT License
