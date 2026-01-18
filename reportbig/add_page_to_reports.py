"""
Script to add a new page with a stacked area chart visual to all report directories.
"""

import os
import json
import secrets
from pathlib import Path


def generate_unique_id(length=20):
    """Generate a unique hex ID for pages and visuals."""
    return secrets.token_hex(length // 2)


def create_page_structure(report_path, page_id, visual_id, page_number):
    """
    Create the page structure with a stacked area chart visual.

    Args:
        report_path: Path to the report directory
        page_id: Unique ID for the new page
        visual_id: Unique ID for the visual
        page_number: Display page number
    """
    pages_dir = report_path / "definition" / "pages"
    page_dir = pages_dir / page_id
    visuals_dir = page_dir / "visuals" / visual_id

    # Create directories
    visuals_dir.mkdir(parents=True, exist_ok=True)

    # Create page.json
    page_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
        "name": page_id,
        "displayName": f"Page {page_number}",
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280
    }

    page_json_path = page_dir / "page.json"
    with open(page_json_path, 'w', encoding='utf-8') as f:
        json.dump(page_json, f, indent=2, ensure_ascii=False)

    # Create visual.json
    visual_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json",
        "name": visual_id,
        "position": {
            "x": 10,
            "y": 0,
            "z": 0,
            "height": 280,
            "width": 280,
            "tabOrder": 0
        },
        "visual": {
            "visualType": "stackedAreaChart",
            "drillFilterOtherVisuals": True
        }
    }

    visual_json_path = visuals_dir / "visual.json"
    with open(visual_json_path, 'w', encoding='utf-8') as f:
        json.dump(visual_json, f, indent=2, ensure_ascii=False)

    return page_id


def update_pages_metadata(report_path, new_page_id):
    """
    Update pages.json to include the new page.

    Args:
        report_path: Path to the report directory
        new_page_id: ID of the new page to add
    """
    pages_json_path = report_path / "definition" / "pages" / "pages.json"

    if not pages_json_path.exists():
        # Create new pages.json if it doesn't exist
        pages_data = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
            "pageOrder": [new_page_id],
            "activePageName": new_page_id
        }
    else:
        with open(pages_json_path, 'r', encoding='utf-8') as f:
            pages_data = json.load(f)

        # Add new page to pageOrder if not already present
        if new_page_id not in pages_data.get("pageOrder", []):
            if "pageOrder" not in pages_data:
                pages_data["pageOrder"] = []
            pages_data["pageOrder"].append(new_page_id)

        # Set as active page
        pages_data["activePageName"] = new_page_id

    with open(pages_json_path, 'w', encoding='utf-8') as f:
        json.dump(pages_data, f, indent=2, ensure_ascii=False)


def add_page_to_report(report_path, pages_to_add=1):
    """
    Add one or more pages to a report directory.

    Args:
        report_path: Path to the report directory
        pages_to_add: Number of pages to add (default: 1)

    Returns:
        Number of pages successfully added
    """
    report_name = report_path.name

    # Check if this is a valid report directory
    definition_dir = report_path / "definition"
    if not definition_dir.exists():
        return 0

    pages_dir = definition_dir / "pages"
    if not pages_dir.exists():
        pages_dir.mkdir(parents=True, exist_ok=True)

    # Determine the current number of pages
    pages_json_path = pages_dir / "pages.json"
    current_page_count = 0
    if pages_json_path.exists():
        with open(pages_json_path, 'r', encoding='utf-8') as f:
            pages_data = json.load(f)
            current_page_count = len(pages_data.get("pageOrder", []))

    pages_added = 0
    for i in range(pages_to_add):
        page_number = current_page_count + i + 1

        # Generate unique IDs
        page_id = generate_unique_id(20)
        visual_id = generate_unique_id(20)

        # Create page structure
        create_page_structure(report_path, page_id, visual_id, page_number)

        # Update pages metadata
        update_pages_metadata(report_path, page_id)

        pages_added += 1

    return pages_added


def process_all_reports(directory=".", pages_to_add=1, max_reports=None):
    """
    Process report directories in the specified directory.

    Args:
        directory: Directory to search for report directories (default: current directory)
        pages_to_add: Number of pages to add to each report (default: 1)
        max_reports: Maximum number of reports to process (default: None, process all)
    """
    directory_path = Path(directory).resolve()

    # Find all .Report directories
    report_dirs = [d for d in directory_path.iterdir()
                   if d.is_dir() and d.name.endswith('.Report')]

    if not report_dirs:
        print("No report directories found (directories ending with .Report)")
        return

    # Limit number of reports if specified
    if max_reports is not None:
        report_dirs = sorted(report_dirs)[:max_reports]
        print(f"Processing {len(report_dirs)} report(s) (limited to {max_reports})...")
    else:
        print(f"Processing {len(report_dirs)} report(s)...")

    success_count = 0
    total_pages_added = 0
    failed_reports = []

    for report_dir in sorted(report_dirs):
        try:
            pages_added = add_page_to_report(report_dir, pages_to_add)
            if pages_added > 0:
                success_count += 1
                total_pages_added += pages_added
        except Exception as e:
            failed_reports.append((report_dir.name, str(e)))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Reports processed: {success_count}/{len(report_dirs)}")
    print(f"Total pages added: {total_pages_added}")

    if failed_reports:
        print(f"\nFailed reports ({len(failed_reports)}):")
        for report_name, error in failed_reports:
            print(f"  - {report_name}: {error}")


if __name__ == "__main__":
    import sys

    print("Add Page(s) to Reports")
    print("=" * 70)

    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("\nUsage:")
        print("  python add_page_to_reports.py [num_pages] [num_reports] [directory]")
        print("\nArguments:")
        print("  num_pages    - Number of pages to add to each report (default: 1)")
        print("  num_reports  - Maximum number of reports to process (default: all)")
        print("  directory    - Directory containing report folders (default: current directory)")
        print("\nExamples:")
        print('  python add_page_to_reports.py                 # Add 1 page to all reports')
        print('  python add_page_to_reports.py 2               # Add 2 pages to all reports')
        print('  python add_page_to_reports.py 2 20            # Add 2 pages to 20 reports')
        print('  python add_page_to_reports.py 5 10 ../reports # Add 5 pages to 10 reports in ../reports')
        sys.exit(0)

    pages_to_add = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    max_reports = int(sys.argv[2]) if len(sys.argv) > 2 else None
    target_dir = sys.argv[3] if len(sys.argv) > 3 else "."

    if pages_to_add < 1:
        print("Error: Number of pages must be at least 1")
        sys.exit(1)

    print()
    process_all_reports(target_dir, pages_to_add, max_reports)
