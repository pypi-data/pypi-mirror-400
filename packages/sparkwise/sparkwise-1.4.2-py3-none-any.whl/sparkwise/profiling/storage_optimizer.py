"""
Storage Optimization Analyzer for Fabric Spark.

Provides insights into:
- Small file problems in Delta tables
- VACUUM recommendations with ROI calculations
- Partition effectiveness analysis
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, sum as _sum, avg, max as _max, min as _min, lit
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Dict, List, Optional, Tuple
import re

console = Console()


class StorageOptimizer:
    """Analyzes storage patterns and provides optimization recommendations."""
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """Initialize storage optimizer."""
        self.spark = spark or SparkSession.getActiveSession()
        if not self.spark:
            raise RuntimeError("No active Spark session found")
    
    def analyze_table_files(self, table_path: str) -> Dict:
        """
        Analyze file structure of a Delta table.
        
        Args:
            table_path: Path to Delta table (e.g., "Tables/mytable" or full path)
        
        Returns:
            Dictionary with file statistics
        """
        try:
            # Read Delta table metadata
            delta_log_path = f"{table_path}/_delta_log"
            
            # Use describe detail to get file-level info
            detail_df = self.spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`")
            
            # Get basic stats
            stats = detail_df.select(
                "numFiles", 
                "sizeInBytes",
                "partitionColumns"
            ).first()
            
            if not stats:
                return {"error": "Could not read table metadata"}
            
            num_files = stats["numFiles"] if stats["numFiles"] else 0
            size_bytes = stats["sizeInBytes"] if stats["sizeInBytes"] else 0
            partition_cols = stats["partitionColumns"] if stats["partitionColumns"] else []
            
            # Calculate averages
            avg_file_size_mb = (size_bytes / num_files / 1024 / 1024) if num_files > 0 else 0
            total_size_gb = size_bytes / 1024 / 1024 / 1024
            
            # Estimate small files (conservative: <10MB)
            # In real implementation, would query file-level metadata
            estimated_small_files = 0
            if avg_file_size_mb < 50:  # If average is small, likely many small files
                # Rough estimation: files below average are "small"
                estimated_small_files = int(num_files * 0.4)  # Conservative estimate
            
            return {
                "num_files": num_files,
                "total_size_gb": round(total_size_gb, 2),
                "avg_file_size_mb": round(avg_file_size_mb, 2),
                "estimated_small_files": estimated_small_files,
                "partition_columns": partition_cols,
                "is_partitioned": len(partition_cols) > 0
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def detect_small_files(self, table_path: str, threshold_mb: int = 10) -> Dict:
        """
        Detect small file problem in Delta table.
        
        Args:
            table_path: Path to Delta table
            threshold_mb: File size threshold in MB (default 10MB)
        
        Returns:
            Analysis with small file metrics and recommendations
        """
        console.print(f"\n[bold cyan]🔍 Analyzing File Structure: {table_path}[/bold cyan]\n")
        
        stats = self.analyze_table_files(table_path)
        
        if "error" in stats:
            console.print(f"[red]❌ Error: {stats['error']}[/red]")
            return stats
        
        # Display table statistics
        table = Table(
            title="📊 Table File Statistics",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")
        table.add_column("Status", justify="center")
        
        # File count
        file_status = "🟢 Good" if stats["num_files"] < 1000 else "🟡 High" if stats["num_files"] < 10000 else "🔴 Critical"
        table.add_row("Total Files", f"{stats['num_files']:,}", file_status)
        
        # File size
        table.add_row("Total Size", f"{stats['total_size_gb']:.2f} GB", "")
        
        # Average file size
        avg_status = "🟢 Good" if stats["avg_file_size_mb"] >= 128 else "🟡 Small" if stats["avg_file_size_mb"] >= 32 else "🔴 Too Small"
        table.add_row("Avg File Size", f"{stats['avg_file_size_mb']:.2f} MB", avg_status)
        
        # Small files estimate
        if stats["estimated_small_files"] > 0:
            small_pct = (stats["estimated_small_files"] / stats["num_files"] * 100) if stats["num_files"] > 0 else 0
            small_status = "🔴 Problem" if small_pct > 30 else "🟡 Warning" if small_pct > 10 else "🟢 OK"
            table.add_row(
                f"Files < {threshold_mb}MB (est.)", 
                f"{stats['estimated_small_files']:,} ({small_pct:.1f}%)", 
                small_status
            )
        
        # Partitioning
        if stats["is_partitioned"]:
            part_cols = ", ".join(stats["partition_columns"])
            table.add_row("Partitioned By", part_cols, "✅")
        else:
            table.add_row("Partitioned", "No", "ℹ️")
        
        console.print(table)
        
        # Recommendations
        self._print_small_file_recommendations(stats, threshold_mb)
        
        return stats
    
    def _print_small_file_recommendations(self, stats: Dict, threshold_mb: int):
        """Print recommendations for small file problem."""
        recommendations = []
        
        # Small file problem
        if stats["estimated_small_files"] > 100 or stats["avg_file_size_mb"] < 32:
            recommendations.append("**🔥 HIGH PRIORITY: Small File Problem Detected**")
            recommendations.append("")
            recommendations.append("**Immediate Actions:**")
            recommendations.append("1. Run OPTIMIZE to compact files:")
            recommendations.append("   ```python")
            recommendations.append(f"   spark.sql(\"OPTIMIZE delta.`{stats.get('path', 'table_path')}`\")")
            recommendations.append("   ```")
            recommendations.append("")
            recommendations.append("2. Enable Auto-Optimize for future writes:")
            recommendations.append("   ```python")
            recommendations.append("   spark.conf.set('spark.databricks.delta.optimizeWrite.enabled', 'true')")
            recommendations.append("   spark.conf.set('spark.databricks.delta.autoCompact.enabled', 'true')")
            recommendations.append("   ```")
            recommendations.append("")
        
        # High file count
        if stats["num_files"] > 10000:
            recommendations.append("**⚠️ High File Count**")
            recommendations.append(f"• {stats['num_files']:,} files detected")
            recommendations.append("• Target: <1,000 files for optimal performance")
            recommendations.append(f"• Potential improvement: {int((1 - 1000/stats['num_files']) * 100)}% fewer files")
            recommendations.append("")
        
        # Optimal file size guidance
        if stats["avg_file_size_mb"] < 128:
            target_size = 128 if not stats["is_partitioned"] else 128
            recommendations.append("**💡 Optimal File Size: 128MB - 1GB**")
            recommendations.append(f"• Current average: {stats['avg_file_size_mb']:.1f} MB")
            recommendations.append(f"• Target: {target_size} MB minimum")
            recommendations.append("")
        
        # Partitioning advice
        if not stats["is_partitioned"] and stats["total_size_gb"] > 10:
            recommendations.append("**🎯 Consider Partitioning**")
            recommendations.append("• Table size > 10GB, partitioning may improve query performance")
            recommendations.append("• Choose columns frequently used in WHERE clauses")
            recommendations.append("• Avoid high-cardinality columns (e.g., timestamp)")
            recommendations.append("")
        
        if recommendations:
            panel = Panel(
                "\n".join(recommendations),
                title="💡 Optimization Recommendations",
                border_style="yellow",
                padding=(1, 2)
            )
            console.print(panel)
    
    def calculate_vacuum_roi(
        self, 
        table_path: str, 
        retention_hours: int = 168,
        storage_cost_per_gb: float = 0.023
    ) -> Dict:
        """
        Calculate ROI for running VACUUM on a Delta table.
        
        Args:
            table_path: Path to Delta table
            retention_hours: Retention period in hours (default 168 = 7 days)
            storage_cost_per_gb: Storage cost per GB per month (default $0.023 for OneLake)
        
        Returns:
            Dictionary with vacuum ROI analysis
        """
        console.print(f"\n[bold cyan]🗑️ VACUUM ROI Analysis: {table_path}[/bold cyan]\n")
        
        try:
            # Get table history to estimate deletable files
            history_df = self.spark.sql(f"DESCRIBE HISTORY delta.`{table_path}`")
            
            # Count operations that create removable files
            removable_ops = history_df.filter(
                col("operation").isin(["DELETE", "UPDATE", "MERGE", "WRITE"])
            ).count()
            
            # Get current size
            detail_df = self.spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`")
            current_stats = detail_df.first()
            
            current_size_gb = (current_stats["sizeInBytes"] / 1024 / 1024 / 1024) if current_stats["sizeInBytes"] else 0
            
            # Estimate reclaimable space (conservative: 10-30% based on operations)
            if removable_ops > 20:
                reclaim_pct = 30
            elif removable_ops > 10:
                reclaim_pct = 20
            elif removable_ops > 5:
                reclaim_pct = 10
            else:
                reclaim_pct = 5
            
            reclaimable_gb = current_size_gb * (reclaim_pct / 100)
            monthly_savings = reclaimable_gb * storage_cost_per_gb
            annual_savings = monthly_savings * 12
            
            # Estimate compute cost for VACUUM (rough: $0.50-2.00 depending on size)
            if current_size_gb < 10:
                vacuum_cost = 0.50
            elif current_size_gb < 100:
                vacuum_cost = 1.00
            elif current_size_gb < 1000:
                vacuum_cost = 2.00
            else:
                vacuum_cost = 5.00
            
            # Calculate ROI
            months_to_break_even = vacuum_cost / monthly_savings if monthly_savings > 0 else float('inf')
            is_worth_it = months_to_break_even <= 3  # Worth it if breaks even in 3 months
            
            # Display results
            table = Table(
                title="💰 VACUUM Cost-Benefit Analysis",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan"
            )
            
            table.add_column("Metric", style="bold")
            table.add_column("Value", justify="right")
            
            table.add_row("Current Size", f"{current_size_gb:.2f} GB")
            table.add_row("Removable Operations", f"{removable_ops:,}")
            table.add_row("", "")
            table.add_row("[bold]Estimated Reclaimable[/bold]", f"[bold]{reclaimable_gb:.2f} GB ({reclaim_pct}%)[/bold]")
            table.add_row("Monthly Storage Savings", f"[green]${monthly_savings:.2f}[/green]")
            table.add_row("Annual Savings", f"[green]${annual_savings:.2f}[/green]")
            table.add_row("", "")
            table.add_row("Est. VACUUM Compute Cost", f"[yellow]${vacuum_cost:.2f}[/yellow]")
            table.add_row("", "")
            
            if is_worth_it:
                verdict = f"[bold green]✅ Yes ({months_to_break_even:.1f} months to break even)[/bold green]"
            elif months_to_break_even < float('inf'):
                verdict = f"[yellow]⚠️ Marginal ({months_to_break_even:.1f} months to break even)[/yellow]"
            else:
                verdict = "[red]❌ Not recommended (no savings)[/red]"
            
            table.add_row("[bold]Worth Running?[/bold]", verdict)
            
            console.print(table)
            
            # Print command
            if is_worth_it:
                console.print(f"\n[bold green]✅ Recommended Action:[/bold green]")
                console.print(f"[dim]spark.sql(\"VACUUM delta.`{table_path}` RETAIN {retention_hours} HOURS\")[/dim]\n")
            
            return {
                "current_size_gb": round(current_size_gb, 2),
                "reclaimable_gb": round(reclaimable_gb, 2),
                "monthly_savings": round(monthly_savings, 2),
                "annual_savings": round(annual_savings, 2),
                "vacuum_cost": vacuum_cost,
                "months_to_break_even": round(months_to_break_even, 1),
                "is_worth_it": is_worth_it
            }
            
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
            return {"error": str(e)}
    
    def analyze_partition_effectiveness(
        self, 
        table_path: str,
        sample_queries: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze partition effectiveness for a Delta table.
        
        Args:
            table_path: Path to Delta table
            sample_queries: Optional list of representative queries to analyze
        
        Returns:
            Partition effectiveness analysis
        """
        console.print(f"\n[bold cyan]📂 Partition Effectiveness Analysis: {table_path}[/bold cyan]\n")
        
        try:
            # Get table details
            detail_df = self.spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`")
            stats = detail_df.first()
            
            partition_cols = stats["partitionColumns"] if stats["partitionColumns"] else []
            
            if not partition_cols or len(partition_cols) == 0:
                console.print("[yellow]ℹ️ Table is not partitioned[/yellow]\n")
                console.print("Consider partitioning if:")
                console.print("  • Table size > 10GB")
                console.print("  • Queries frequently filter on specific columns")
                console.print("  • Data has natural time/category boundaries\n")
                return {"is_partitioned": False}
            
            # Read table to analyze partitions
            df = self.spark.read.format("delta").load(table_path)
            total_rows = df.count()
            
            # Analyze partition distribution
            partition_stats = df.groupBy(*partition_cols).agg(
                count(lit(1)).alias("row_count")
            ).select(
                _sum("row_count").alias("total_rows"),
                count(lit(1)).alias("partition_count"),
                avg("row_count").alias("avg_rows_per_partition"),
                _max("row_count").alias("max_rows_per_partition"),
                _min("row_count").alias("min_rows_per_partition")
            ).first()
            
            partition_count = partition_stats["partition_count"]
            avg_rows = partition_stats["avg_rows_per_partition"]
            max_rows = partition_stats["max_rows_per_partition"]
            min_rows = partition_stats["min_rows_per_partition"]
            
            # Calculate skew
            skew_ratio = max_rows / avg_rows if avg_rows > 0 else 0
            
            # Display results
            table = Table(
                title="📊 Partition Statistics",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan"
            )
            
            table.add_column("Metric", style="bold")
            table.add_column("Value", justify="right")
            table.add_column("Status", justify="center")
            
            table.add_row("Partition Columns", ", ".join(partition_cols), "")
            table.add_row("Total Partitions", f"{partition_count:,}", "")
            table.add_row("Total Rows", f"{total_rows:,}", "")
            table.add_row("", "", "")
            
            # Partition count assessment
            if partition_count < 10:
                count_status = "🟡 Too Few"
            elif partition_count < 1000:
                count_status = "🟢 Good"
            elif partition_count < 10000:
                count_status = "🟡 High"
            else:
                count_status = "🔴 Too Many"
            
            table.add_row("Partition Count", f"{partition_count:,}", count_status)
            table.add_row("Avg Rows/Partition", f"{avg_rows:,.0f}", "")
            table.add_row("Max Rows/Partition", f"{max_rows:,}", "")
            table.add_row("Min Rows/Partition", f"{min_rows:,}", "")
            table.add_row("", "", "")
            
            # Skew assessment
            if skew_ratio > 10:
                skew_status = "🔴 High Skew"
            elif skew_ratio > 3:
                skew_status = "🟡 Moderate Skew"
            else:
                skew_status = "🟢 Balanced"
            
            table.add_row("Skew Ratio", f"{skew_ratio:.1f}x", skew_status)
            
            console.print(table)
            
            # Recommendations
            self._print_partition_recommendations(
                partition_cols, 
                partition_count, 
                skew_ratio,
                total_rows
            )
            
            return {
                "is_partitioned": True,
                "partition_columns": partition_cols,
                "partition_count": partition_count,
                "total_rows": total_rows,
                "avg_rows_per_partition": int(avg_rows),
                "skew_ratio": round(skew_ratio, 2)
            }
            
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
            return {"error": str(e)}
    
    def _print_partition_recommendations(
        self, 
        partition_cols: List[str], 
        partition_count: int,
        skew_ratio: float,
        total_rows: int
    ):
        """Print partition-related recommendations."""
        recommendations = []
        
        # Too many partitions
        if partition_count > 10000:
            recommendations.append("**🔴 CRITICAL: Too Many Partitions**")
            recommendations.append(f"• {partition_count:,} partitions detected")
            recommendations.append("• Target: <1,000 partitions for optimal performance")
            recommendations.append("• **Action:** Re-partition with coarser granularity")
            recommendations.append("  - Consider date ranges instead of individual dates")
            recommendations.append("  - Combine low-cardinality columns")
            recommendations.append("")
        
        # Too few partitions
        elif partition_count < 10 and total_rows > 1000000:
            recommendations.append("**🟡 Under-Partitioned**")
            recommendations.append(f"• Only {partition_count} partitions for {total_rows:,} rows")
            recommendations.append("• Consider finer-grained partitioning")
            recommendations.append("")
        
        # High skew
        if skew_ratio > 10:
            recommendations.append("**⚠️ High Partition Skew Detected**")
            recommendations.append(f"• Max partition is {skew_ratio:.1f}x larger than average")
            recommendations.append("• **Impact:** Some queries will be much slower")
            recommendations.append("• **Solutions:**")
            recommendations.append("  - Add secondary partition column")
            recommendations.append("  - Use Z-Order instead of partitioning")
            recommendations.append("  - Consider bucketing for uniform distribution")
            recommendations.append("")
        
        # General best practices
        recommendations.append("**💡 Partition Best Practices**")
        recommendations.append("✅ **Good Partition Columns:**")
        recommendations.append("  • Date/time columns (year, month, day)")
        recommendations.append("  • Low-cardinality categories (region, department)")
        recommendations.append("  • Frequently filtered columns")
        recommendations.append("")
        recommendations.append("❌ **Avoid:**")
        recommendations.append("  • High-cardinality columns (user_id, timestamp)")
        recommendations.append("  • Rarely filtered columns")
        recommendations.append("  • Creating >10,000 partitions")
        recommendations.append("")
        recommendations.append("🎯 **Alternative: Z-Order**")
        recommendations.append("  • Better for multi-column filtering")
        recommendations.append("  • No partition overhead")
        recommendations.append("  ```python")
        recommendations.append(f"  spark.sql(\"OPTIMIZE delta.`table` ZORDER BY (col1, col2)\")")
        recommendations.append("  ```")
        
        if recommendations:
            panel = Panel(
                "\n".join(recommendations),
                title="💡 Partition Optimization Recommendations",
                border_style="yellow",
                padding=(1, 2)
            )
            console.print(panel)


def analyze_storage(table_path: str) -> None:
    """
    Run comprehensive storage analysis on a Delta table.
    
    Args:
        table_path: Path to Delta table
    """
    optimizer = StorageOptimizer()
    
    console.print("\n" + "="*80)
    console.print("[bold cyan]🗄️ STORAGE OPTIMIZATION ANALYSIS[/bold cyan]")
    console.print("="*80)
    
    # Run all analyses
    optimizer.detect_small_files(table_path)
    optimizer.calculate_vacuum_roi(table_path)
    optimizer.analyze_partition_effectiveness(table_path)
    
    console.print("\n" + "="*80 + "\n")


def check_small_files(table_path: str, threshold_mb: int = 10) -> Dict:
    """Convenience function for small file detection."""
    optimizer = StorageOptimizer()
    return optimizer.detect_small_files(table_path, threshold_mb)


def vacuum_roi(table_path: str, retention_hours: int = 168) -> Dict:
    """Convenience function for VACUUM ROI analysis."""
    optimizer = StorageOptimizer()
    return optimizer.calculate_vacuum_roi(table_path, retention_hours)


def check_partitions(table_path: str) -> Dict:
    """Convenience function for partition effectiveness analysis."""
    optimizer = StorageOptimizer()
    return optimizer.analyze_partition_effectiveness(table_path)
