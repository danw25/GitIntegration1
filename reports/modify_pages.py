"""
Script to modify existing pages in report directories.
Changes displayName in page.json and name in visual.json files.
"""

import os
import json
import secrets
from pathlib import Path


def generate_unique_id(length=20):
    """Generate a unique hex ID."""
    return secrets.token_hex(length // 2)


def modify_page_json(page_json_path, new_display_name=None):
    """
    Modify page.json file.

    Args:
        page_json_path: Path to page.json file
        new_display_name: New display name (if None, generates from page number)

    Returns:
        True if modified, False otherwise
    """
    if not page_json_path.exists():
        return False

    with open(page_json_path, 'r', encoding='utf-8') as f:
        page_data = json.load(f)

    # Update display name
    old_name = page_data.get('displayName', '')
    if new_display_name:
        page_data['displayName'] = new_display_name
    else:
        # Keep existing pattern but ensure it's updated
        page_data['displayName'] = f"Modified {old_name}"

    with open(page_json_path, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, indent=2, ensure_ascii=False)

    return True


def modify_visual_json(visual_json_path, new_name=None):
    """
    Modify visual.json file.

    Args:
        visual_json_path: Path to visual.json file
        new_name: New name (if None, generates unique ID)

    Returns:
        True if modified, False otherwise
    """
    if not visual_json_path.exists():
        return False

    with open(visual_json_path, 'r', encoding='utf-8') as f:
        visual_data = json.load(f)

    # Update name
    if new_name:
        visual_data['name'] = new_name
    else:
        # Generate new unique ID
        visual_data['name'] = generate_unique_id(20)

    with open(visual_json_path, 'w', encoding='utf-8') as f:
        json.dump(visual_data, f, indent=2, ensure_ascii=False)

    return True


def modify_pages_in_report(report_path, modify_display_names=True, modify_visual_names=True,
                           max_pages=None, page_name_prefix="Modified Page"):
    """
    Modify pages in a report directory.

    Args:
        report_path: Path to the report directory
        modify_display_names: Whether to modify page displayNames
        modify_visual_names: Whether to modify visual names
        max_pages: Maximum number of pages to modify (None = all)
        page_name_prefix: Prefix for new page names

    Returns:
        Tuple of (pages_modified, visuals_modified)
    """
    definition_dir = report_path / "definition"
    if not definition_dir.exists():
        return 0, 0

    pages_dir = definition_dir / "pages"
    if not pages_dir.exists():
        return 0, 0

    # Get all page directories
    page_dirs = [d for d in pages_dir.iterdir()
                 if d.is_dir() and not d.name in ['pages.json']]

    if max_pages:
        page_dirs = sorted(page_dirs)[:max_pages]

    pages_modified = 0
    visuals_modified = 0

    for idx, page_dir in enumerate(sorted(page_dirs), 1):
        # Modify page.json
        if modify_display_names:
            page_json_path = page_dir / "page.json"
            if page_json_path.exists():
                new_display_name = f"{page_name_prefix} {idx}"
                if modify_page_json(page_json_path, new_display_name):
                    pages_modified += 1

        # Modify visual.json files
        if modify_visual_names:
            visuals_dir = page_dir / "visuals"
            if visuals_dir.exists():
                for visual_dir in visuals_dir.iterdir():
                    if visual_dir.is_dir():
                        visual_json_path = visual_dir / "visual.json"
                        if modify_visual_json(visual_json_path):
                            visuals_modified += 1

    return pages_modified, visuals_modified


def process_reports(directory=".", max_reports=None, max_pages_per_report=None,
                    modify_display_names=True, modify_visual_names=True,
                    page_name_prefix="Modified Page"):
    """
    Process report directories and modify their pages.

    Args:
        directory: Directory to search for reports
        max_reports: Maximum number of reports to process
        max_pages_per_report: Maximum pages to modify per report
        modify_display_names: Whether to modify page displayNames
        modify_visual_names: Whether to modify visual names
        page_name_prefix: Prefix for new page names
    """
    directory_path = Path(directory).resolve()

    # Find all .Report directories
    report_dirs = [d for d in directory_path.iterdir()
                   if d.is_dir() and d.name.endswith('.Report')]

    if not report_dirs:
        print("No report directories found (directories ending with .Report)")
        return

    if max_reports:
        report_dirs = sorted(report_dirs)[:max_reports]
        print(f"Processing {len(report_dirs)} report(s) (limited to {max_reports})...")
    else:
        print(f"Processing {len(report_dirs)} report(s)...")

    total_pages_modified = 0
    total_visuals_modified = 0
    reports_modified = 0
    failed_reports = []

    for report_dir in sorted(report_dirs):
        try:
            pages_mod, visuals_mod = modify_pages_in_report(
                report_dir,
                modify_display_names=modify_display_names,
                modify_visual_names=modify_visual_names,
                max_pages=max_pages_per_report,
                page_name_prefix=page_name_prefix
            )

            if pages_mod > 0 or visuals_mod > 0:
                reports_modified += 1
                total_pages_modified += pages_mod
                total_visuals_modified += visuals_mod
        except Exception as e:
            failed_reports.append((report_dir.name, str(e)))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Reports modified: {reports_modified}/{len(report_dirs)}")
    print(f"Total pages modified: {total_pages_modified}")
    print(f"Total visuals modified: {total_visuals_modified}")

    if failed_reports:
        print(f"\nFailed reports ({len(failed_reports)}):")
        for report_name, error in failed_reports:
            print(f"  - {report_name}: {error}")


if __name__ == "__main__":
    import sys

    print("Modify Pages in Reports")
    print("=" * 70)

    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("\nUsage:")
        print("  python modify_pages.py [options]")
        print("\nOptions:")
        print("  --reports N         - Process only N reports")
        print("  --pages N           - Modify only N pages per report")
        print("  --prefix PREFIX     - Use PREFIX for page names (default: 'Modified Page')")
        print("  --skip-pages        - Don't modify page displayNames")
        print("  --skip-visuals      - Don't modify visual names")
        print("  --dir PATH          - Target directory (default: current)")
        print("\nExamples:")
        print('  python modify_pages.py')
        print('  python modify_pages.py --reports 5 --pages 10')
        print('  python modify_pages.py --prefix "Updated Page"')
        print('  python modify_pages.py --skip-visuals --reports 20')
        sys.exit(0)

    # Parse arguments
    target_dir = "."
    max_reports = None
    max_pages = None
    modify_display_names = True
    modify_visual_names = True
    page_name_prefix = "Modified Page"

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--reports' and i + 1 < len(sys.argv):
            max_reports = int(sys.argv[i + 1])
            i += 2
        elif arg == '--pages' and i + 1 < len(sys.argv):
            max_pages = int(sys.argv[i + 1])
            i += 2
        elif arg == '--prefix' and i + 1 < len(sys.argv):
            page_name_prefix = sys.argv[i + 1]
            i += 2
        elif arg == '--dir' and i + 1 < len(sys.argv):
            target_dir = sys.argv[i + 1]
            i += 2
        elif arg == '--skip-pages':
            modify_display_names = False
            i += 1
        elif arg == '--skip-visuals':
            modify_visual_names = False
            i += 1
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information")
            sys.exit(1)

    print()
    process_reports(
        directory=target_dir,
        max_reports=max_reports,
        max_pages_per_report=max_pages,
        modify_display_names=modify_display_names,
        modify_visual_names=modify_visual_names,
        page_name_prefix=page_name_prefix
    )
