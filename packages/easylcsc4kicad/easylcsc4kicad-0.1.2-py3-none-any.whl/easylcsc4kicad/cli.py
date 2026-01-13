"""
CLI for EasyLCSC4KiCAD.

Command-line interface for searching LCSC and EasyEDA components.
"""

import argparse
import json
import logging
import sys

from easylcsc4kicad import __version__
from easylcsc4kicad.download import download_component
from easylcsc4kicad.models import Component, SearchResult
from easylcsc4kicad.search import (
    get_by_lcsc_id,
    search,
    search_3d_models,
    search_footprints,
    search_symbols,
)


def setup_logging(level: str) -> None:
    """Configure logging based on verbosity level."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )


def format_component_table(component: Component) -> str:
    """Format a single component as a table row."""
    lines = []
    lines.append(f"  UUID:         {component.uuid}")
    lines.append(f"  Title:        {component.title}")
    if component.lcsc_id:
        lines.append(f"  LCSC ID:      {component.lcsc_id}")
    if component.manufacturer:
        lines.append(f"  Manufacturer: {component.manufacturer}")
    if component.category:
        lines.append(f"  Category:     {component.category}")
    if component.description:
        lines.append(f"  Description:  {component.description[:80]}...")
    if component.datasheet_url:
        lines.append(f"  Datasheet:    {component.datasheet_url}")
    if component.attributes:
        lines.append("  Attributes:")
        for key, value in sorted(component.attributes.items()):
            if key not in [
                "Datasheet",
                "Manufacturer",
                "Supplier Part",
                "Manufacturer Part",
            ]:  # Skip redundant
                # Clean up values
                clean_value = str(value).strip()
                if clean_value:
                    lines.append(f"    {key:<20}: {clean_value}")
    if component.symbols:
        lines.append(f"  Symbols:      {len(component.symbols)}")
        for sym in component.symbols[:3]:
            lines.append(f"    - {sym.title} ({sym.uuid[:16]}...)")
    if component.footprints:
        lines.append(f"  Footprints:   {len(component.footprints)}")
        for fp in component.footprints[:3]:
            lines.append(f"    - {fp.title} ({fp.uuid[:16]}...)")
    return "\n".join(lines)


def format_results_table(result: SearchResult) -> str:
    """Format search results as a table."""
    lines = []
    lines.append(
        f"Found {result.total} results (page {result.page}/{result.total_pages})"
    )
    lines.append("-" * 60)

    for i, comp in enumerate(result.results, 1):
        lines.append(f"\n[{i}] {comp.title}")
        lines.append(format_component_table(comp))

    if result.has_next:
        lines.append(f"\n... use --page {result.page + 1} for more results")

    return "\n".join(lines)


def format_component_json(component: Component) -> str:
    """Format a component as JSON."""
    data = {
        "uuid": component.uuid,
        "title": component.title,
        "lcsc_id": component.lcsc_id,
        "description": component.description,
        "datasheet_url": component.datasheet_url,
        "manufacturer": component.manufacturer,
        "category": component.category,
        "attributes": component.attributes,
        "symbols": [
            {"uuid": s.uuid, "title": s.title, "prefix": s.prefix}
            for s in component.symbols
        ],
        "footprints": [
            {"uuid": f.uuid, "title": f.title, "datasheet_url": f.datasheet_url}
            for f in component.footprints
        ],
    }
    return json.dumps(data, indent=2)


def format_results_json(result: SearchResult) -> str:
    """Format search results as JSON."""
    data = {
        "total": result.total,
        "page": result.page,
        "items_per_page": result.items_per_page,
        "total_pages": result.total_pages,
        "results": [
            {
                "uuid": comp.uuid,
                "title": comp.title,
                "lcsc_id": comp.lcsc_id,
                "description": comp.description,
                "manufacturer": comp.manufacturer,
                "category": comp.category,
            }
            for comp in result.results
        ],
    }
    return json.dumps(data, indent=2)


def cmd_search(args: argparse.Namespace) -> int:
    """Handle search command."""
    # Determine search function based on type
    if args.type == "footprint":
        result = search_footprints(args.keyword, args.page, args.page_size)
    elif args.type == "symbol":
        result = search_symbols(args.keyword, args.page, args.page_size)
    elif args.type == "3d":
        result = search_3d_models(args.keyword, args.page, args.page_size)
    else:
        result = search(
            args.keyword,
            source=args.source,
            page=args.page,
            page_size=args.page_size,
            component_type=args.type,
        )

    if result.total == 0:
        print(f"No results found for '{args.keyword}'")
        return 1

    if args.json:
        print(format_results_json(result))
    else:
        print(format_results_table(result))

    return 0


def cmd_get(args: argparse.Namespace) -> int:
    """Handle get command."""
    identifier = args.identifier

    # Validate LCSC ID format
    # LCSC IDs start with 'C' followed by digits
    if not (identifier.startswith("C") and identifier[1:].isdigit()):
        print(f"Invalid LCSC ID: {identifier}")
        print("The 'get' command only supports LCSC component IDs (e.g. C12345)")
        return 1

    component = get_by_lcsc_id(identifier)

    if component is None:
        print(f"Component not found: {identifier}")
        return 1

    if args.json:
        print(format_component_json(component))
    else:
        print(f"Component: {component.title}")
        print("-" * 40)
        print(format_component_table(component))

    return 0


def cmd_download(args: argparse.Namespace) -> int:
    """Handle download command."""
    # Parse models argument
    models = args.models if args.models else ["STEP"]
    if models == []:
        models = []  # --models with no args means no 3D models

    success_count = 0
    fail_count = 0

    for component_id in args.component_ids:
        result = download_component(
            component_id=component_id,
            output_dir=args.output,
            footprint_lib=args.footprint_lib,
            symbol_lib=args.symbol_lib,
            model_dir=args.model_dir,
            model_base_variable=args.model_base_variable,
            models=models,
            create_footprint_flag=args.footprint,
            create_symbol_flag=args.symbol,
            skip_existing=args.skip_existing,
        )

        if result["success"]:
            success_count += 1
            print(f"✓ {component_id}")
            if result["footprint"]:
                print(f"  Footprint: {result['footprint']}")
            if result["symbol"]:
                print(f"  Symbol: {result['symbol']}")
            if result["datasheet"]:
                print(f"  Datasheet: {result['datasheet']}")
        else:
            fail_count += 1
            print(f"✗ {component_id}: {result.get('error', 'Unknown error')}")

    print(f"\nDownloaded: {success_count}, Failed: {fail_count}")
    return 0 if fail_count == 0 else 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="easylcsc4kicad",
        description="Search LCSC and EasyEDA for schematics and footprints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  easylcsc4kicad search ESP32-S3
  easylcsc4kicad search "USB Type-C" --source lcsc --json
  easylcsc4kicad search 0603 --type footprint
  easylcsc4kicad get C1337258
""",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search for components",
        description="Search LCSC and EasyEDA for components",
    )
    search_parser.add_argument(
        "keyword",
        help="Search keyword",
    )
    search_parser.add_argument(
        "--source",
        choices=["all", "lcsc", "easyeda"],
        default="all",
        help="Search source (default: all)",
    )
    search_parser.add_argument(
        "--type",
        choices=["device", "symbol", "footprint", "3d"],
        default="device",
        help="Component type to search (default: device)",
    )
    search_parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="Page number (default: 1)",
    )
    search_parser.add_argument(
        "--page-size",
        type=int,
        default=20,
        dest="page_size",
        help="Results per page (default: 20)",
    )
    search_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # Get command
    get_parser = subparsers.add_parser(
        "get",
        help="Get component by LCSC ID",
        description="Retrieve component details by LCSC part number",
    )
    get_parser.add_argument(
        "identifier",
        help="LCSC part number (e.g., C1337258)",
    )
    get_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # Download command
    download_parser = subparsers.add_parser(
        "download",
        help="Download KiCad footprint, symbol, and 3D model",
        description="Download component files from LCSC/EasyEDA",
    )
    download_parser.add_argument(
        "component_ids",
        metavar="LCSC_ID",
        nargs="+",
        help="LCSC part numbers (e.g., C1337258)",
    )
    download_parser.add_argument(
        "-o",
        "--output",
        default="easylcsc_lib",
        help="Output directory (default: easylcsc_lib)",
    )
    download_parser.add_argument(
        "--no-footprint",
        dest="footprint",
        action="store_false",
        help="Skip footprint generation",
    )
    download_parser.add_argument(
        "--no-symbol",
        dest="symbol",
        action="store_false",
        help="Skip symbol generation",
    )
    download_parser.add_argument(
        "--models",
        nargs="*",
        choices=["STEP", "WRL"],
        default=["STEP"],
        help="3D model formats (default: STEP). Use --models alone for none",
    )
    download_parser.add_argument(
        "--footprint-lib",
        dest="footprint_lib",
        default="footprint",
        help="Footprint library name (default: footprint)",
    )
    download_parser.add_argument(
        "--symbol-lib",
        dest="symbol_lib",
        default=None,
        help="Symbol library name (default: component name)",
    )
    download_parser.add_argument(
        "--model-dir",
        dest="model_dir",
        default="packages3d",
        help="3D model directory (default: packages3d)",
    )
    download_parser.add_argument(
        "--model-base-variable",
        dest="model_base_variable",
        default="",
        help="KiCad path variable for 3D models",
    )
    download_parser.add_argument(
        "--skip-existing",
        dest="skip_existing",
        action="store_true",
        help="Skip already existing files",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Setup logging
    log_level = "DEBUG" if args.verbose else "WARNING"
    setup_logging(log_level)

    # Dispatch to command handler
    if args.command == "search":
        return cmd_search(args)
    elif args.command == "get":
        return cmd_get(args)
    elif args.command == "download":
        return cmd_download(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
