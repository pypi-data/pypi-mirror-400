# Materials Project MCP Server

An MCP (Model Context Protocol) server that provides access to the [Materials Project](https://materialsproject.org/) database for querying material properties, crystal structures, and phase diagrams.

**Also includes Claude Code Skills** for direct terminal access via slash commands!

[![PyPI version](https://badge.fury.io/py/mcp-materials-project.svg)](https://pypi.org/project/mcp-materials-project/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Two Ways to Use

### 1. MCP Server (for Claude Desktop/Code)
Use as an MCP server for natural language queries through Claude

### 2. Skills (for Claude Code CLI)
Use as slash commands (`/materials-search`, `/materials-export`, `/materials-compare`) directly in your terminal

---

## Features

### 🔍 Available Tools

- **fetch_full_material_data**: Search materials by formula, elements, band gap, stability, and more
- **get_structure_details**: Get detailed crystal structure with lattice parameters and atomic positions
- **search_materials_by_property**: Search by specific property ranges (band gap, bulk modulus, density, etc.)
- **get_phase_diagram_info**: Get phase diagram entries and stability information for chemical systems
- **compare_materials**: Compare multiple materials side by side with key properties
- **export_to_excel**: Export material data to professionally formatted Excel files
  - **NEW**: Supports horizontal comparison format for multiple materials
  - Automatically uses comparison format when exporting 2+ materials with comma-separated IDs

### 📊 Excel Export Formats

#### MCP Server: Horizontal Comparison Format (Always)
- **Layout**: Properties as rows, materials as columns
- **Best for**: Side-by-side comparison and detailed analysis
- **Includes**: 30+ key properties (band gap, stability, elasticity, magnetism, dielectric, surface properties, etc.)
- **Works for**: Single material or multiple materials

#### Skills Scripts: Dual Format
- **Horizontal Comparison**: Triggered by comma-separated material IDs (e.g., `--material-ids mp-149,mp-390`)
- **Vertical List**: Triggered by single material ID or search criteria
- **Includes**: 14 basic properties only

### 📋 Data Comparison: MCP Server vs Skills Scripts

| Feature | MCP Server | Skills Scripts |
|---------|-----------|----------------|
| **Data Fields** | 60+ comprehensive fields | 14 basic fields |
| **Excel Format** | Horizontal comparison (always) | Horizontal comparison + Vertical list |
| **Use Case** | Deep research, full analysis | Quick queries, simple comparisons |
| **Properties Included** | All thermodynamic, electronic, mechanical, magnetic, dielectric, surface properties + structure details | Basic properties only (ID, formula, band gap, stability, density, symmetry) |
| **File Size** | Larger (complete data) | Smaller (essential data) |
| **Performance** | Slower (more data) | Faster (less data) |

**Recommendation**:
- Use **Skills scripts** for quick screening and simple comparisons
- Use **MCP server** for comprehensive research and detailed analysis
- Combine both: Screen with Skills, then get full data with MCP server

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
"Export and compare mp-149, mp-390, and mp-672 to Excel"
"Compare these materials in Excel: mp-2534, mp-22862"
```

**Note**: MCP server always uses horizontal comparison format (properties as rows, materials as columns) for optimal side-by-side analysis.

## Data Available

The server provides access to comprehensive material properties including:

- **Thermodynamic**: Formation energy, energy above hull, stability
- **Electronic**: Band gap, band structure, DOS
- **Mechanical**: Bulk modulus, shear modulus, elastic constants
- **Magnetic**: Magnetization, magnetic ordering
- **Structural**: Crystal structure, symmetry, lattice parameters
- **Chemical**: Composition, elements, formula

## 🎮 Using Skills (Claude Code CLI)

For direct terminal access with slash commands, see the [Skills README](skills/README.md).

### Quick Start

```bash
# Install dependencies
pip install mp-api pandas openpyxl

# Set API key
export MP_API_KEY=your_api_key_here

# Copy skills configuration
cp skills/skills.json .claude/skills.json

# Use in Claude Code
/materials-search --formula Si
/materials-export --band-gap-min 1.0 --band-gap-max 3.0 --stable
/materials-compare mp-149 mp-2534
```

**Available Skills:**
- `/materials-search` - Search materials database
- `/materials-export` - Export to Excel
- `/materials-compare` - Compare materials

See [skills/README.md](skills/README.md) for detailed documentation.

---

## License

MIT License - see [LICENSE](LICENSE) file for details

## Links

- **PyPI**: https://pypi.org/project/mcp-materials-project/
- **GitHub**: https://github.com/luffysolution-svg/mcp-materials-project
- **Materials Project**: https://materialsproject.org/
