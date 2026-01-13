# Materials Project MCP Server

An MCP (Model Context Protocol) server that provides access to the [Materials Project](https://materialsproject.org/) database for querying material properties, crystal structures, and phase diagrams.

## Features

- **fetch_full_material_data**: Search materials by formula, elements, band gap, stability, etc.
- **get_structure_details**: Get crystal structure with lattice parameters and atomic sites
- **search_materials_by_property**: Search by specific property ranges (band gap, bulk modulus, etc.)
- **get_phase_diagram_info**: Get phase diagram entries for a chemical system
- **compare_materials**: Compare multiple materials side by side

## Installation

### From PyPI (Recommended)

```bash
pip install mcp-materials-project
```

### From Source

```bash
git clone https://github.com/luffysolution-svg/mcp-materials-project.git
cd mcp-materials-project
pip install -r requirements.txt
```

## Configuration

1. Get your API key from [Materials Project](https://materialsproject.org/api)

2. Set the environment variable:
```bash
# Windows
set MP_API_KEY=your_api_key_here

# Linux/macOS
export MP_API_KEY=your_api_key_here
```

### Claude Code Configuration

Add to your `~/.claude/settings.json` or project `.mcp.json`:

```json
{
  "mcpServers": {
    "materials-project": {
      "command": "mcp-materials-project",
      "env": {
        "MP_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Or run directly:

```bash
claude mcp add materials-project -- mcp-materials-project
```

Then set the environment variable `MP_API_KEY` in your shell or add it to the config.

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "materials-project": {
      "command": "mcp-materials-project",
      "env": {
        "MP_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Usage Examples

Once configured, you can ask Claude:

- "Search for stable materials containing Li and O with band gap > 2 eV"
- "Get the crystal structure of mp-149 (Silicon)"
- "Compare mp-149, mp-2534, and mp-22862"
- "Show me the phase diagram for the Li-Fe-O system"

## License

MIT
