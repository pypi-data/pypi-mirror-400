"""
Command-line interface for BOAMP Scraper

Usage:
    python -m boamp.cli search "cloud" --limit 10
    python -m boamp.cli search "cybersécurité" --budget-min 100000 --limit 20
    python -m boamp.cli search "aws" --category CLOUD_INFRASTRUCTURE --output tenders.csv
"""

import argparse
import asyncio
import csv
import json
import sys
from typing import List, Optional

from .scraper import TenderScraper
from .models import TenderCategory, Tender


def setup_parser() -> argparse.ArgumentParser:
    """Setup argument parser"""
    parser = argparse.ArgumentParser(
        prog="boamp-scraper",
        description="Scrape French public tenders from BOAMP.fr",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for tenders")
    search_parser.add_argument(
        "keywords", nargs="+", help="Keywords to search for (space-separated)"
    )
    search_parser.add_argument(
        "--category",
        type=str,
        choices=[c.name for c in TenderCategory],
        help="Filter by category",
    )
    search_parser.add_argument(
        "--budget-min", type=int, help="Minimum budget in EUR"
    )
    search_parser.add_argument(
        "--budget-max", type=int, help="Maximum budget in EUR"
    )
    search_parser.add_argument("--region", type=str, help="Filter by region")
    search_parser.add_argument(
        "--limit", type=int, default=50, help="Maximum results (default: 50)"
    )
    search_parser.add_argument(
        "--output",
        type=str,
        help="Output file (CSV or JSON based on extension)",
    )
    search_parser.add_argument(
        "--format",
        type=str,
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )

    # Version command
    subparsers.add_parser("version", help="Show version")

    return parser


def format_table(tenders: List[Tender]) -> str:
    """Format tenders as a table"""
    if not tenders:
        return "No tenders found."

    # Header
    lines = []
    lines.append("=" * 100)
    lines.append(f"{'Title':<50} {'Organisme':<30} {'Budget':>15}")
    lines.append("=" * 100)

    # Rows
    for tender in tenders:
        title = (
            tender.title[:47] + "..." if len(tender.title) > 50 else tender.title
        )
        org = (
            tender.organisme[:27] + "..."
            if len(tender.organisme) > 30
            else tender.organisme
        )
        budget = f"{tender.budget:,}€" if tender.budget > 0 else "N/A"

        lines.append(f"{title:<50} {org:<30} {budget:>15}")

    lines.append("=" * 100)
    lines.append(f"Total: {len(tenders)} tenders")

    return "\n".join(lines)


def format_json(tenders: List[Tender]) -> str:
    """Format tenders as JSON"""
    data = [t.model_dump(mode="json") for t in tenders]
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def save_csv(tenders: List[Tender], output_file: str):
    """Save tenders to CSV file"""
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Title",
                "Organisme",
                "Budget",
                "Category",
                "Region",
                "URL",
                "Date Publication",
            ]
        )

        for tender in tenders:
            writer.writerow(
                [
                    tender.title,
                    tender.organisme,
                    tender.budget,
                    tender.category.value,
                    tender.region or "",
                    tender.url,
                    tender.date_publication.isoformat(),
                ]
            )

    print(f"✅ Saved {len(tenders)} tenders to {output_file}")


def save_json(tenders: List[Tender], output_file: str):
    """Save tenders to JSON file"""
    data = [t.model_dump(mode="json") for t in tenders]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"✅ Saved {len(tenders)} tenders to {output_file}")


async def cmd_search(args):
    """Execute search command"""
    # Parse category
    category = None
    if args.category:
        category = TenderCategory[args.category]

    # Search
    scraper = TenderScraper()
    print(f"🔍 Searching for: {' '.join(args.keywords)}")
    print(f"📊 Limit: {args.limit}")
    if category:
        print(f"📂 Category: {category.value}")
    if args.budget_min:
        print(f"💰 Budget min: {args.budget_min:,}€")
    if args.budget_max:
        print(f"💰 Budget max: {args.budget_max:,}€")
    if args.region:
        print(f"📍 Region: {args.region}")

    print("\n⏳ Scraping BOAMP...\n")

    tenders = await scraper.search_async(
        keywords=args.keywords,
        category=category,
        budget_min=args.budget_min,
        budget_max=args.budget_max,
        region=args.region,
        limit=args.limit,
    )

    # Output
    if args.output:
        # Save to file
        if args.output.endswith(".csv"):
            save_csv(tenders, args.output)
        elif args.output.endswith(".json"):
            save_json(tenders, args.output)
        else:
            print(f"❌ Unknown file extension. Use .csv or .json")
            return 1
    else:
        # Print to stdout
        if args.format == "table":
            print(format_table(tenders))
        elif args.format == "json":
            print(format_json(tenders))
        elif args.format == "csv":
            # Print CSV to stdout
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(
                [
                    "Title",
                    "Organisme",
                    "Budget",
                    "Category",
                    "Region",
                    "URL",
                    "Date Publication",
                ]
            )
            for tender in tenders:
                writer.writerow(
                    [
                        tender.title,
                        tender.organisme,
                        tender.budget,
                        tender.category.value,
                        tender.region or "",
                        tender.url,
                        tender.date_publication.isoformat(),
                    ]
                )
            print(output.getvalue())

    return 0


def cmd_version(args):
    """Execute version command"""
    from . import __version__

    print(f"boamp-scraper v{__version__}")
    return 0


def main():
    """Main CLI entry point"""
    parser = setup_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "search":
            return asyncio.run(cmd_search(args))
        elif args.command == "version":
            return cmd_version(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

