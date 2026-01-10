#!/usr/bin/env python3
"""
Command-line utility for outlier detection in SOUL_SENSE_EXAM

Usage:
    python scripts/outlier_analysis.py --user <username> [--method ensemble]
    python scripts/outlier_analysis.py --age-group <age_group> [--method iqr]
    python scripts/outlier_analysis.py --global [--method zscore]
    python scripts/outlier_analysis.py --inconsistency <username> [--days 30]
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import get_session
from app.outlier_detection import OutlierDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def format_output(result: dict, output_format: str = "text") -> str:
    """Format output in requested format"""
    if output_format == "json":
        return json.dumps(result, indent=2, default=str)
    else:
        return format_text_output(result)


def format_text_output(result: dict) -> str:
    """Format output as readable text"""
    output = []
    
    if "error" in result:
        output.append(f"❌ Error: {result['error']}")
        return "\n".join(output)
    
    # Header
    if "username" in result:
        output.append(f"\n📊 Outlier Detection Report for User: {result['username']}")
    elif "age_group" in result:
        output.append(f"\n📊 Outlier Detection Report for Age Group: {result['age_group']}")
    elif "scope" in result:
        output.append(f"\n📊 {result['scope'].upper()} Outlier Detection Report")
    
    output.append("=" * 60)
    
    # Summary Statistics
    if "statistics" in result:
        stats = result["statistics"]
        output.append("\n📈 Statistics:")
        output.append(f"   Mean Score:       {stats['mean_score']:.2f}")
        output.append(f"   Median Score:     {stats['median_score']:.2f}")
        output.append(f"   Std Dev:          {stats['std_dev']:.2f}")
        output.append(f"   Range:            {stats['min_score']:.0f} - {stats['max_score']:.0f}")
    
    # Overall Results
    output.append(f"\n📍 Detection Method: {result.get('detection_method', 'ensemble')}")
    output.append(f"   Total Scores:     {result.get('total_scores', 'N/A')}")
    output.append(f"   Outliers Found:   {result.get('outlier_count', 0)}")
    
    if result.get('outlier_count', 0) > 0:
        output.append(f"   Outlier %:        {(result['outlier_count'] / result['total_scores'] * 100):.1f}%")
    
    # Method-specific details
    if result.get('method') == 'zscore':
        output.append(f"\n   Z-Score Mean:     {result.get('mean', 'N/A'):.2f}")
        output.append(f"   Z-Score Std Dev:  {result.get('std_dev', 'N/A'):.2f}")
        output.append(f"   Threshold:        {result.get('threshold', 'N/A')}")
    
    elif result.get('method') == 'iqr':
        output.append(f"\n   Q1:               {result.get('q1', 'N/A'):.2f}")
        output.append(f"   Q3:               {result.get('q3', 'N/A'):.2f}")
        output.append(f"   IQR:              {result.get('iqr', 'N/A'):.2f}")
        output.append(f"   Lower Bound:      {result.get('lower_bound', 'N/A'):.2f}")
        output.append(f"   Upper Bound:      {result.get('upper_bound', 'N/A'):.2f}")
    
    elif result.get('method') == 'ensemble':
        output.append(f"\n   Methods Used:     {', '.join(result.get('methods_used', []))}")
        output.append(f"   Consensus Level:  {result.get('consensus_threshold', 0.5) * 100:.0f}%")
    
    # Outlier Details
    if result.get('outlier_details'):
        output.append("\n⚠️  Outlier Details:")
        output.append("-" * 60)
        for i, outlier in enumerate(result['outlier_details'], 1):
            output.append(f"\n   Outlier #{i}:")
            output.append(f"      Score ID:      {outlier['score_id']}")
            if 'username' in outlier:
                output.append(f"      Username:      {outlier['username']}")
            output.append(f"      Score Value:   {outlier['score_value']}")
            output.append(f"      Age:           {outlier.get('age', 'N/A')}")
            output.append(f"      Age Group:     {outlier.get('age_group', 'N/A')}")
            output.append(f"      Timestamp:     {outlier.get('timestamp', 'N/A')}")
    
    output.append("\n" + "=" * 60)
    
    return "\n".join(output)


def analyze_user(args) -> None:
    """Analyze outliers for a specific user"""
    session = get_session()
    try:
        detector = OutlierDetector()
        
        logger.info(f"Analyzing outliers for user: {args.user}")
        result = detector.detect_outliers_for_user(
            session,
            args.user,
            method=args.method
        )
        
        print(format_output(result, args.format))
        
        if args.inconsistency:
            logger.info(f"Analyzing inconsistency patterns for user: {args.user}")
            inconsistency = detector.detect_inconsistency_patterns(
                session,
                args.user,
                time_window_days=args.days
            )
            # Format inconsistency result
            if args.format == "json":
                print("\n" + json.dumps(inconsistency, indent=2, default=str))
            else:
                output = ["\n📊 Scoring Inconsistency Analysis Report"]
                output.append("=" * 60)
                
                if "error" in inconsistency:
                    output.append(f"❌ Error: {inconsistency['error']}")
                else:
                    output.append(f"\nUser:                     {inconsistency['username']}")
                    output.append(f"Time Window:              {inconsistency['time_window_days']} days")
                    output.append(f"Scores in Window:         {inconsistency['total_scores_in_window']}")
                    output.append(f"Inconsistent Transitions: {inconsistency['inconsistent_transitions']}")
                    output.append(f"Mean Change:              {inconsistency['mean_change']:.2f}")
                    output.append(f"Std Dev of Change:        {inconsistency['std_change']:.2f}")
                    output.append(f"Coefficient of Variation: {inconsistency['coefficient_of_variation']:.2f}%")
                    output.append(f"Highly Inconsistent:      {'Yes' if inconsistency['is_highly_inconsistent'] else 'No'}")
                    
                    if inconsistency['inconsistency_details']:
                        output.append("\n⚠️  Inconsistent Score Changes:")
                        output.append("-" * 60)
                        for i, detail in enumerate(inconsistency['inconsistency_details'], 1):
                            output.append(f"\nTransition #{i}:")
                            output.append(f"   From {detail['between_scores'][0]} to {detail['between_scores'][1]}")
                            output.append(f"   Change: {detail['change']:+.0f}")
                            output.append(f"   Between: {detail['timestamp_1']} and {detail['timestamp_2']}")
                
                output.append("\n" + "=" * 60)
                print("\n".join(output))
    
    finally:
        session.close()


def analyze_age_group(args) -> None:
    """Analyze outliers for a specific age group"""
    session = get_session()
    try:
        detector = OutlierDetector()
        
        logger.info(f"Analyzing outliers for age group: {args.age_group}")
        result = detector.detect_outliers_by_age_group(
            session,
            args.age_group,
            method=args.method
        )
        
        print(format_output(result, args.format))
    
    finally:
        session.close()


def analyze_global(args) -> None:
    """Analyze outliers globally"""
    session = get_session()
    try:
        detector = OutlierDetector()
        
        logger.info("Performing global outlier analysis")
        result = detector.detect_outliers_global(
            session,
            method=args.method
        )
        
        print(format_output(result, args.format))
    
    finally:
        session.close()


def analyze_inconsistency(args) -> None:
    """Analyze scoring inconsistency patterns"""
    session = get_session()
    try:
        detector = OutlierDetector()
        
        logger.info(f"Analyzing inconsistency patterns for user: {args.user}")
        result = detector.detect_inconsistency_patterns(
            session,
            args.user,
            time_window_days=args.days
        )
        
        # Format for text output
        if args.format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            output = ["\n📊 Scoring Inconsistency Analysis Report"]
            output.append("=" * 60)
            
            if "error" in result:
                output.append(f"❌ Error: {result['error']}")
            else:
                output.append(f"\nUser:                     {result['username']}")
                output.append(f"Time Window:              {result['time_window_days']} days")
                output.append(f"Scores in Window:         {result['total_scores_in_window']}")
                output.append(f"Inconsistent Transitions: {result['inconsistent_transitions']}")
                output.append(f"Mean Change:              {result['mean_change']:.2f}")
                output.append(f"Std Dev of Change:        {result['std_change']:.2f}")
                output.append(f"Coefficient of Variation: {result['coefficient_of_variation']:.2f}%")
                output.append(f"Highly Inconsistent:      {'Yes' if result['is_highly_inconsistent'] else 'No'}")
                
                if result['inconsistency_details']:
                    output.append("\n⚠️  Inconsistent Score Changes:")
                    output.append("-" * 60)
                    for i, detail in enumerate(result['inconsistency_details'], 1):
                        output.append(f"\nTransition #{i}:")
                        output.append(f"   From {detail['between_scores'][0]} to {detail['between_scores'][1]}")
                        output.append(f"   Change: {detail['change']:+.0f}")
                        output.append(f"   Between: {detail['timestamp_1']} and {detail['timestamp_2']}")
            
            output.append("\n" + "=" * 60)
            print("\n".join(output))
    
    finally:
        session.close()


def get_statistics(args) -> None:
    """Get statistical summary"""
    session = get_session()
    try:
        detector = OutlierDetector()
        
        if args.age_group:
            logger.info(f"Getting statistics for age group: {args.age_group}")
            result = detector.get_statistical_summary(session, age_group=args.age_group)
        else:
            logger.info("Getting global statistics")
            result = detector.get_statistical_summary(session)
        
        if args.format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            output = ["\n📊 Statistical Summary"]
            output.append("=" * 60)
            if "error" not in result:
                output.append(f"\nScope:    {result['scope']}")
                output.append(f"Count:    {result['count']}")
                output.append(f"Mean:     {result['mean']:.2f}")
                output.append(f"Median:   {result['median']:.2f}")
                output.append(f"Std Dev:  {result['std_dev']:.2f}")
                output.append(f"Min:      {result['min']:.0f}")
                output.append(f"Max:      {result['max']:.0f}")
                output.append(f"Q1:       {result['q1']:.2f}")
                output.append(f"Q3:       {result['q3']:.2f}")
                output.append(f"IQR:      {result['iqr']:.2f}")
            else:
                output.append(f"Error: {result['error']}")
            output.append("=" * 60)
            print("\n".join(output))
    
    finally:
        session.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Outlier Detection Analysis Tool for SOUL_SENSE_EXAM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze user scores
  python scripts/outlier_analysis.py --user john_doe --method ensemble
  
  # Analyze age group
  python scripts/outlier_analysis.py --age-group "18-25" --method iqr
  
  # Global analysis
  python scripts/outlier_analysis.py --global --method zscore
  
  # Check scoring inconsistency
  python scripts/outlier_analysis.py --inconsistency john_doe --days 30
  
  # Get statistics
  python scripts/outlier_analysis.py --stats --age-group "26-35"
        """
    )
    
    # Detection method
    parser.add_argument(
        '--method',
        choices=['zscore', 'iqr', 'modified_zscore', 'mad', 'ensemble'],
        default='ensemble',
        help='Outlier detection method (default: ensemble)'
    )
    
    # Output format
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    # Analysis modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--user',
        help='Analyze outliers for specific user'
    )
    group.add_argument(
        '--age-group',
        help='Analyze outliers for specific age group'
    )
    group.add_argument(
        '--global-analysis',
        dest='global_analysis',
        action='store_true',
        help='Perform global outlier analysis'
    )
    group.add_argument(
        '--inconsistency',
        metavar='USERNAME',
        help='Analyze scoring inconsistency patterns for user'
    )
    group.add_argument(
        '--stats',
        action='store_true',
        help='Get statistical summary'
    )
    
    # Additional options
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Time window in days (for inconsistency analysis)'
    )
    parser.add_argument(
        '--include-inconsistency',
        action='store_true',
        help='Include inconsistency analysis with user analysis'
    )
    
    args = parser.parse_args()
    
    try:
        if args.user:
            args.inconsistency = args.include_inconsistency
            analyze_user(args)
        elif args.age_group:
            analyze_age_group(args)
        elif args.global_analysis:
            analyze_global(args)
        elif args.inconsistency:
            args.user = args.inconsistency
            analyze_inconsistency(args)
        elif args.stats:
            get_statistics(args)
    
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
