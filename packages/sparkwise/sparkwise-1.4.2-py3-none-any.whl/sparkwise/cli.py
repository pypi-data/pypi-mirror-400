"""Command-line interface for sparkwise."""

import argparse
import sys
from typing import Optional

from sparkwise.core.advisor import FabricAdvisor
from sparkwise.config_qa import ask


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="sparkwise - The automated technical fellow for your Fabric Spark workloads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sparkwise analyze              Run full analysis
  sparkwise quick                Run quick health check
  sparkwise config shuffle       Search for shuffle-related configs
  sparkwise explain spark.sql.adaptive.enabled
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run comprehensive analysis')
    analyze_parser.add_argument(
        '--export',
        type=str,
        help='Export results to JSON file'
    )
    
    # Quick check command
    subparsers.add_parser('quick', help='Run quick health check')
    
    # Config search command
    config_parser = subparsers.add_parser('config', help='Search configuration documentation')
    config_parser.add_argument('keyword', type=str, help='Configuration keyword to search')
    
    # Explain command
    explain_parser = subparsers.add_parser('explain', help='Explain a configuration parameter')
    explain_parser.add_argument('param', type=str, help='Configuration parameter name')
    
    # Profile commands
    profile_parser = subparsers.add_parser('profile', help='Profile Spark session and resources')
    profile_subparsers = profile_parser.add_subparsers(dest='profile_command', help='Profile type')
    
    # Session profile
    session_parser = profile_subparsers.add_parser('session', help='Profile Spark session configuration')
    session_parser.add_argument('--export', type=str, help='Export profile to JSON file')
    
    # Executor profile
    profile_subparsers.add_parser('executors', help='Profile executor metrics and utilization')
    
    # Job profile
    job_parser = profile_subparsers.add_parser('jobs', help='Profile job execution metrics')
    job_parser.add_argument('--max-jobs', type=int, default=10, help='Maximum jobs to analyze')
    
    # Resource profile
    profile_subparsers.add_parser('resources', help='Profile resource allocation and utilization')
    
    # Bottleneck analysis
    profile_subparsers.add_parser('bottlenecks', help='Analyze performance bottlenecks')
    
    # Predict command (scalability)
    predict_parser = subparsers.add_parser('predict', help='Predict scalability and capacity recommendations')
    predict_parser.add_argument('--runs-per-month', type=int, default=100, help='Expected job runs per month for ROI calculation')
    
    # Timeline command
    subparsers.add_parser('timeline', help='Show stage execution timeline')
    
    # Efficiency command
    efficiency_parser = subparsers.add_parser('efficiency', help='Analyze compute efficiency and waste')
    efficiency_parser.add_argument('--runs-per-month', type=int, default=100, help='Expected job runs per month for cost projections')
    
    # Skew detection command
    skew_parser = subparsers.add_parser('skew', help='Detect data skew and provide mitigation strategies')
    skew_parser.add_argument('--type', choices=['task', 'partition', 'join'], default='task',
                            help='Type of skew analysis: task (duration variance), partition (data distribution), join (join skew)')
    
    # Query plan analysis command
    query_parser = subparsers.add_parser('query', help='Analyze SQL query plans for optimization opportunities')
    query_parser.add_argument('--dataframe', type=str, help='DataFrame variable name to analyze (interactive mode)')
    
    # Storage optimization commands
    storage_parser = subparsers.add_parser('storage', help='Analyze storage optimization opportunities')
    storage_subparsers = storage_parser.add_subparsers(dest='storage_command', help='Storage analysis type')
    
    # Full storage analysis
    storage_full = storage_subparsers.add_parser('analyze', help='Run comprehensive storage analysis')
    storage_full.add_argument('table_path', type=str, help='Path to Delta table')
    
    # Small files check
    small_files = storage_subparsers.add_parser('small-files', help='Detect small file problems')
    small_files.add_argument('table_path', type=str, help='Path to Delta table')
    small_files.add_argument('--threshold', type=int, default=10, help='File size threshold in MB (default: 10)')
    
    # VACUUM ROI
    vacuum = storage_subparsers.add_parser('vacuum-roi', help='Calculate VACUUM return on investment')
    vacuum.add_argument('table_path', type=str, help='Path to Delta table')
    vacuum.add_argument('--retention-hours', type=int, default=168, help='Retention period in hours (default: 168 = 7 days)')
    
    # Partition effectiveness
    partitions = storage_subparsers.add_parser('partitions', help='Analyze partition effectiveness')
    partitions.add_argument('table_path', type=str, help='Path to Delta table')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'analyze':
            advisor = FabricAdvisor()
            advisor.analyze(export_path=args.export)
            return 0
        
        elif args.command == 'quick':
            advisor = FabricAdvisor()
            advisor.quick_check()
            return 0
        
        elif args.command == 'config':
            ask.search(args.keyword)
            return 0
        
        elif args.command == 'explain':
            ask.config(args.param)
            return 0
        
        elif args.command == 'profile':
            if not args.profile_command:
                parser.parse_args(['profile', '-h'])
                return 1
            
            if args.profile_command == 'session':
                from sparkwise.profiling.session_profiler import SessionProfiler
                profiler = SessionProfiler()
                profiler.profile(export_path=args.export if hasattr(args, 'export') else None)
                return 0
            
            elif args.profile_command == 'executors':
                from sparkwise.profiling.executor_profiler import ExecutorProfiler
                profiler = ExecutorProfiler()
                profiler.profile()
                return 0
            
            elif args.profile_command == 'jobs':
                from sparkwise.profiling.job_profiler import JobProfiler
                profiler = JobProfiler()
                max_jobs = args.max_jobs if hasattr(args, 'max_jobs') else 10
                profiler.profile(max_jobs=max_jobs)
                return 0
            
            elif args.profile_command == 'resources':
                from sparkwise.profiling.resource_profiler import ResourceProfiler
                profiler = ResourceProfiler()
                profiler.profile()
                return 0
            
            elif args.profile_command == 'bottlenecks':
                from sparkwise.profiling.job_profiler import JobProfiler
                profiler = JobProfiler()
                profiler.analyze_bottlenecks()
                return 0
            
            else:
                parser.parse_args(['profile', '-h'])
                return 1
        
        elif args.command == 'predict':
            from sparkwise.profiling.scalability_predictor import predict_scalability
            predict_scalability(runs_per_month=args.runs_per_month)
            return 0
        
        elif args.command == 'timeline':
            from sparkwise.profiling.stage_timeline import show_timeline
            show_timeline()
            return 0
        
        elif args.command == 'efficiency':
            from sparkwise.profiling.efficiency_analyzer import analyze_efficiency
            analyze_efficiency(runs_per_month=args.runs_per_month)
            return 0
        
        elif args.command == 'skew':
            from sparkwise.core.advanced_skew_detector import detect_skew
            detect_skew()
            return 0
        
        elif args.command == 'query':
            print("Query plan analysis requires an active DataFrame.")
            print("Usage: In your Fabric notebook, run:")
            print("  from sparkwise import analyze_query")
            print("  results = analyze_query(your_dataframe)")
            return 0
        
        elif args.command == 'storage':
            if not args.storage_command:
                parser.print_help()
                return 1
            
            if args.storage_command == 'analyze':
                from sparkwise.profiling.storage_optimizer import analyze_storage
                analyze_storage(args.table_path)
                return 0
            
            elif args.storage_command == 'small-files':
                from sparkwise.profiling.storage_optimizer import check_small_files
                check_small_files(args.table_path, args.threshold)
                return 0
            
            elif args.storage_command == 'vacuum-roi':
                from sparkwise.profiling.storage_optimizer import vacuum_roi
                vacuum_roi(args.table_path, args.retention_hours)
                return 0
            
            elif args.storage_command == 'partitions':
                from sparkwise.profiling.storage_optimizer import check_partitions
                check_partitions(args.table_path)
                return 0
        
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
