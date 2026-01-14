# gnosys-treeshell

Tree-based navigation MCP for the GNOSYS compound intelligence ecosystem.

## Overview

gnosys-treeshell provides a TreeShell interface to all GNOSYS MCPs. Instead of loading 20+ individual MCP tools (consuming ~14k tokens), you load one TreeShell (~1.4k tokens) and navigate to what you need.

## Installation

```bash
pip install gnosys-treeshell
```

## MCP Configuration

Add to your Claude Code `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gnosys-treeshell": {
      "command": "gnosys-treeshell"
    }
  }
}
```

## Usage

The TreeShell provides these core commands:

```
nav                               # Show tree structure
jump <coordinate>                 # Navigate to node
<coordinate>.exec {"args"}        # Jump and execute with args
```

### Available Actions

| Coordinate | Action | Description |
|------------|--------|-------------|
| 0.0.1 | discover_server_actions | Find available actions from servers |
| 0.0.2 | execute_action | Execute a specific action |
| 0.0.3 | get_action_details | Get detailed info about an action |
| 0.0.5 | manage_servers | Manage MCP server connections |
| 0.0.6 | search_documentation | Search server action docs |
| 0.0.7 | search_mcp_catalog | Search offline catalog |

### Example

```
# Discover what's available
discover_server_actions.exec {"user_query": "session tracking"}

# Get details on a specific action
get_action_details.exec {"server_name": "starlog", "action_name": "orient"}

# Execute an action
execute_action.exec {"server_name": "starlog", "action_name": "orient", "body_schema": {"path": "/my/project"}}
```

## Part of GNOSYS

This package is part of the [GNOSYS](https://github.com/sancovp/gnosys) compound intelligence system for Claude Code.

## License

GNOSYS Personal Builder License (GPBL) v1.0
