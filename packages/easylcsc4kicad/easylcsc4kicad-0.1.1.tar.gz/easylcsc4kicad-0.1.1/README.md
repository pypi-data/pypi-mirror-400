# EasyLCSC4KiCad

A CLI tool to search for components on LCSC/EasyEDA and download footprints, symbols, and 3D models directly for KiCad.

## Installation

```bash
pip install easylcsc4kicad
```

Or using uv:

```bash
uv pip install easylcsc4kicad
```

## Usage

### Search

Search for components by keyword.

```bash
# Basic search
easylcsc4kicad search "ESP32-S3"

# Search with pagination
easylcsc4kicad search "STM32F103" --page 1 --page-size 10
```

### Download

Download component footprint, symbol, and 3D models using the LCSC ID.

```bash
# Download a specific component
easylcsc4kicad download C1337258

# Download to a specific directory (default: easylcsc_lib)
easylcsc4kicad download C1337258 -o ./my_libs

# Download multiple components
easylcsc4kicad download C1337258 C2980300

# Download without generating footprint or symbol
easylcsc4kicad download C1337258 --no-footprint --no-symbol
```

## Generated Files

The tool generates KiCad files in the specified output directory:

```
output_dir/
├── footprint/
│   ├── component_name.kicad_mod
│   └── packages3d/
│       └── component_name.step
└── symbol/
    └── component_name.kicad_sym
```