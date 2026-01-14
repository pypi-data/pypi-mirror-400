# Materials Project MCP Server

An MCP (Model Context Protocol) server that provides access to the [Materials Project](https://materialsproject.org/) database for querying material properties, crystal structures, and phase diagrams.

[![PyPI version](https://badge.fury.io/py/mcp-materials-project.svg)](https://pypi.org/project/mcp-materials-project/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### 🔍 Available Tools

- **fetch_full_material_data**: Search materials by formula, elements, band gap, stability, and more
- **get_structure_details**: Get detailed crystal structure with lattice parameters and atomic positions
- **search_materials_by_property**: Search by specific property ranges (band gap, bulk modulus, density, etc.)
- **get_phase_diagram_info**: Get phase diagram entries and stability information for chemical systems
- **compare_materials**: Compare multiple materials side by side with key properties
- **export_to_excel**: Export material data to professionally formatted Excel files

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

### 1. Get API Key

Get your free API key from [Materials Project](https://materialsproject.org/api)

### 2. Set Environment Variable

```bash
# Windows
set MP_API_KEY=your_api_key_here

# Linux/macOS
export MP_API_KEY=your_api_key_here
```

### 3. Configure MCP Client

#### Claude Code Configuration

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

#### Claude Desktop Configuration

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

Once configured, you can interact with the Materials Project database through natural language:

### Search Materials

```
"Search for stable materials containing Li and O with band gap > 2 eV"
"Find all materials with silicon and oxygen"
"Show me magnetic materials in the Fe-O system"
```

### Get Structure Details

```
"Get the crystal structure of mp-149 (Silicon)"
"What's the lattice parameters of mp-2534?"
"Show me the atomic positions in mp-22862"
```

### Property-based Search

```
"Find materials with band gap between 1.5 and 3.0 eV"
"Search for materials with density > 5 g/cm³"
"Show materials with bulk modulus > 200 GPa"
```

### Compare Materials

```
"Compare mp-149, mp-2534, and mp-22862"
"What are the differences between these silicon polymorphs: mp-149, mp-157"
```

### Phase Diagrams

```
"Show me the phase diagram for the Li-Fe-O system"
"What are the stable phases in the Si-O chemical system?"
```

### Export to Excel

```
"Export silicon materials to Excel"
"Export all stable materials with band gap > 2 eV to Excel file named 'semiconductors.xlsx'"
"Search for Fe-O magnetic materials and export to Excel"
```

## Data Available

The server provides access to comprehensive material properties including:

- **Thermodynamic**: Formation energy, energy above hull, stability
- **Electronic**: Band gap, band structure, DOS
- **Mechanical**: Bulk modulus, shear modulus, elastic constants
- **Magnetic**: Magnetization, magnetic ordering
- **Structural**: Crystal structure, symmetry, lattice parameters
- **Chemical**: Composition, elements, formula

## License

MIT License - see [LICENSE](LICENSE) file for details

## Links

- **PyPI**: https://pypi.org/project/mcp-materials-project/
- **GitHub**: https://github.com/luffysolution-svg/mcp-materials-project
- **Materials Project**: https://materialsproject.org/
