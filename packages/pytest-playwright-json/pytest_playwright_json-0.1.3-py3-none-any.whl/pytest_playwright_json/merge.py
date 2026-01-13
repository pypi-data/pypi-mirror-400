"""Merge multiple Playwright JSON reports into a single report"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import PlaywrightReport, Stats, Config


def merge_reports(
    report_paths: List[str],
    output_path: str,
    verbose: bool = False
) -> None:
    """Merge multiple Playwright JSON reports into a single report
    
    Args:
        report_paths: List of paths to JSON report files to merge
        output_path: Path where the merged report will be written
        verbose: Print detailed information about the merge process
    """
    if not report_paths:
        print("Error: No report files provided", file=sys.stderr)
        sys.exit(1)
    
    # Load all reports
    reports: List[dict] = []
    report_files = []  # Track which file each report came from
    for report_path in report_paths:
        path = Path(report_path)
        if not path.exists():
            print(f"Warning: Report not found: {report_path}", file=sys.stderr)
            continue
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                reports.append(data)
                report_files.append(report_path)
                if verbose:
                    print(f"Loaded: {report_path}")
                    # Show stats from this file
                    if "stats" in data and isinstance(data["stats"], dict):
                        stats = data["stats"]
                        expected = stats.get("expected", 0) or 0
                        unexpected = stats.get("unexpected", 0) or 0
                        skipped = stats.get("skipped", 0) or 0
                        flaky = stats.get("flaky", 0) or 0
                        duration = stats.get("duration", 0.0) or 0.0
                        total = int(expected) + int(unexpected) + int(skipped)
                        print(f"  Stats: total={total} (expected={expected}, unexpected={unexpected}, skipped={skipped}, flaky={flaky}, duration={duration:.2f}s)")
                    else:
                        print(f"  Warning: No stats found or stats is not a dict")
        except Exception as e:
            print(f"Error loading {report_path}: {e}", file=sys.stderr)
            continue
    
    if not reports:
        print("Error: No valid reports found to merge", file=sys.stderr)
        sys.exit(1)
    
    if verbose:
        print(f"\nMerging {len(reports)} reports...")
    
    # Merge suites
    all_suites: List[dict] = []
    all_errors: List[dict] = []
    
    # Merge stats (Playwright format uses expected/unexpected, not passed/failed)
    merged_stats = {
        "expected": 0,
        "unexpected": 0,
        "skipped": 0,
        "flaky": 0,
        "duration": 0.0
    }
    
    config: Optional[dict] = None
    metadata: Optional[dict] = None
    earliest_start_time: Optional[str] = None
    
    for idx, report in enumerate(reports):
        report_path = report_files[idx] if idx < len(report_files) else "unknown"
        # Use config from first report
        if config is None:
            config = report.get("config", {})
            # Remove shard info from merged config
            if isinstance(config, dict) and "shard" in config:
                config = config.copy()
                del config["shard"]
        
        # Merge suites
        if "suites" in report and isinstance(report["suites"], list):
            all_suites.extend(report["suites"])
        
        # Merge errors
        if "errors" in report and isinstance(report["errors"], list):
            all_errors.extend(report["errors"])
        
        # Merge stats (Playwright format)
        if "stats" in report:
            stats = report["stats"]
            if isinstance(stats, dict):
                expected = stats.get("expected", 0) or 0
                unexpected = stats.get("unexpected", 0) or 0
                skipped = stats.get("skipped", 0) or 0
                flaky = stats.get("flaky", 0) or 0
                duration = stats.get("duration", 0.0) or 0.0
                
                merged_stats["expected"] += int(expected)
                merged_stats["unexpected"] += int(unexpected)
                merged_stats["skipped"] += int(skipped)
                merged_stats["flaky"] += int(flaky)
                merged_stats["duration"] += float(duration)
                
                if verbose:
                    print(f"  Stats from {report_path}: expected={expected}, unexpected={unexpected}, skipped={skipped}, flaky={flaky}, duration={duration}")
                
                # Track earliest start time
                start_time = stats.get("startTime")
                if start_time:
                    if earliest_start_time is None or start_time < earliest_start_time:
                        earliest_start_time = start_time
            elif verbose:
                print(f"  Warning: stats is not a dict in {report_path}: {type(stats)}")
        
        # Use metadata from first report
        if metadata is None and "metadata" in report:
            metadata = report.get("metadata")
    
    # Set start time to earliest
    if earliest_start_time:
        merged_stats["startTime"] = earliest_start_time
    else:
        merged_stats["startTime"] = datetime.now().isoformat()
    
    # Create merged report
    merged_report = {
        "config": config or {},
        "suites": all_suites,
        "stats": merged_stats,
        "errors": all_errors
    }
    
    # Add metadata if available
    if metadata:
        merged_report["metadata"] = metadata
    
    # Write merged report
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(merged_report, f, indent=2)
    
    # Calculate total for display (expected + unexpected + skipped)
    total_tests = merged_stats["expected"] + merged_stats["unexpected"] + merged_stats["skipped"]
    
    print(f"✅ Merged {len(reports)} reports into {output_path}")
    print(f"📊 Total tests: {total_tests} (passed: {merged_stats['expected']}, failed: {merged_stats['unexpected']}, skipped: {merged_stats['skipped']}, flaky: {merged_stats['flaky']})")
    print(f"⏱️  Total duration: {merged_stats['duration']:.2f}s")


def find_report_files(directory: str, pattern: str = "report*.json") -> List[str]:
    """Find all report JSON files in a directory recursively
    
    Args:
        directory: Directory to search
        pattern: Filename pattern to match (default: "report*.json" to match report.json, report-1.json, etc.)
    
    Returns:
        List of paths to report files
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    # Find all JSON files that match the pattern (report.json, report-1.json, etc.)
    reports = []
    for path in dir_path.rglob("*.json"):
        if path.is_file():
            # Match files that start with "report" (report.json, report-1.json, report-2.json, etc.)
            if path.name.startswith("report") and path.name.endswith(".json"):
                reports.append(path)
    
    return sorted([str(r) for r in reports])


def main():
    """CLI entry point for merge command"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Merge multiple Playwright JSON reports into a single report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge specific report files
  pytest-playwright-json-merge report1.json report2.json report3.json -o merged.json
  
  # Find and merge all reports in a directory (recursive search)
  pytest-playwright-json-merge -d test-results -o merged.json
  
  # Merge reports with verbose output (shows stats from each file)
  pytest-playwright-json-merge -d test-results -o merged.json -v
  
  # Merge reports from GitHub Actions artifacts
  pytest-playwright-json-merge -d combined-test-results -o combined-test-results/report.json -v

What it does:
  - Finds all report*.json files (report.json, report-1.json, report-2.json, etc.)
  - Merges suites, stats, errors, and metadata from all reports
  - Creates a single combined report with aggregated statistics
  - Preserves all test results and attachments references
        """
    )
    
    parser.add_argument(
        "reports",
        nargs="*",
        help="Paths to JSON report files to merge (e.g., report1.json report2.json)"
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        metavar="PATH",
        help="Output path for the merged report (e.g., merged.json or test-results/report.json)"
    )
    
    parser.add_argument(
        "-d", "--directory",
        metavar="DIR",
        help="Directory to recursively search for report*.json files (finds report.json, report-1.json, etc.)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed information including stats from each report file"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.3"
    )
    
    args = parser.parse_args()
    
    # Collect report paths
    report_paths: List[str] = list(args.reports)
    
    # If directory specified, find reports in it
    if args.directory:
        found_reports = find_report_files(args.directory)
        report_paths.extend(found_reports)
        if args.verbose and found_reports:
            print(f"Found {len(found_reports)} reports in {args.directory}")
    
    # Merge reports
    try:
        merge_reports(report_paths, args.output, args.verbose)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

