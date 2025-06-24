"""
File: src/tools/data_analyzer.py
Purpose: Data analysis tool for processing structured data, generating insights, and creating visualizations
Functionality: Analyzes datasets, performs statistical analysis, generates charts, and provides data summaries
Update Trigger: When new analysis methods are needed, visualization requirements change, or data formats are updated
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional, Union
import json
import tempfile
import os
from datetime import datetime
import re

try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

from ..models import ToolSchema

class DataAnalyzerTool:
    """
    Data analysis tool for processing and analyzing structured data.
    Supports CSV, JSON, and tabular data analysis with visualization capabilities.
    """
    
    def __init__(self):
        self.description = "Analyze structured data, generate insights, and create visualizations"
        self.supported_formats = ["csv", "json", "xlsx", "tsv"]
        
        if not ANALYTICS_AVAILABLE:
            print("Warning: Analytics libraries not available. Data analysis functionality will be limited.")
    
    def get_schema(self) -> ToolSchema:
        """Return the tool schema for the agent to understand how to use this tool."""
        return ToolSchema(
            name="data_analyzer",
            description="Analyze structured data and generate insights",
            parameters={
                "data_source": {
                    "type": "string",
                    "description": "Path to data file or raw data string"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["summary", "correlation", "distribution", "trend", "comparison"],
                    "description": "Type of analysis to perform",
                    "default": "summary"
                },
                "data_format": {
                    "type": "string",
                    "enum": ["csv", "json", "xlsx", "tsv", "auto"],
                    "description": "Format of the input data",
                    "default": "auto"
                },
                "columns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific columns to analyze (optional)",
                    "default": []
                },
                "create_visualization": {
                    "type": "boolean",
                    "description": "Whether to create charts and graphs",
                    "default": True
                },
                "max_rows": {
                    "type": "integer",
                    "description": "Maximum number of rows to process",
                    "minimum": 1,
                    "maximum": 10000,
                    "default": 1000
                }
            },
            required_parameters=["data_source"]
        )
    
    def validate_input(self, data_source: str, **kwargs) -> None:
        """Validate input parameters."""
        if not data_source or not data_source.strip():
            raise ValueError("Data source cannot be empty")
        
        analysis_type = kwargs.get("analysis_type", "summary")
        valid_types = ["summary", "correlation", "distribution", "trend", "comparison"]
        if analysis_type not in valid_types:
            raise ValueError(f"analysis_type must be one of: {valid_types}")
        
        max_rows = kwargs.get("max_rows", 1000)
        if not isinstance(max_rows, int) or max_rows < 1 or max_rows > 10000:
            raise ValueError("max_rows must be an integer between 1 and 10000")
    
    def execute(self, data_source: str, **kwargs) -> Dict[str, Any]:
        """Execute data analysis and return results."""
        # Validate inputs
        self.validate_input(data_source, **kwargs)
        
        if not ANALYTICS_AVAILABLE:
            return {
                "error": "Data analysis not available. Please install required packages: pip install pandas numpy matplotlib",
                "summary": "",
                "insights": [],
                "visualizations": []
            }
        
        try:
            # Load data
            df = self._load_data(data_source, **kwargs)
            
            if df is None or df.empty:
                return {
                    "error": "No data could be loaded or data is empty",
                    "summary": "",
                    "insights": [],
                    "visualizations": []
                }
            
            # Perform analysis
            analysis_type = kwargs.get("analysis_type", "summary")
            analysis_results = self._perform_analysis(df, analysis_type, **kwargs)
            
            # Generate visualizations if requested
            visualizations = []
            if kwargs.get("create_visualization", True):
                visualizations = self._create_visualizations(df, analysis_type, **kwargs)
            
            return {
                "summary": analysis_results.get("summary", ""),
                "insights": analysis_results.get("insights", []),
                "statistics": analysis_results.get("statistics", {}),
                "visualizations": visualizations,
                "data_info": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "data_types": df.dtypes.to_dict() if hasattr(df.dtypes, 'to_dict') else {},
                    "missing_values": df.isnull().sum().to_dict() if hasattr(df, 'isnull') else {}
                },
                "analysis_type": analysis_type,
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Data analysis failed: {str(e)}",
                "summary": "",
                "insights": [],
                "visualizations": []
            }
    
    def _load_data(self, data_source: str, **kwargs):
        """Load data from various sources and formats."""
        if not ANALYTICS_AVAILABLE:
            return None
            
        data_format = kwargs.get("data_format", "auto")
        max_rows = kwargs.get("max_rows", 1000)
        
        try:
            # Check if data_source is a file path or raw data
            if os.path.exists(data_source):
                # Load from file
                if data_format == "auto":
                    data_format = self._detect_format(data_source)
                
                if data_format == "csv":
                    df = pd.read_csv(data_source, nrows=max_rows)
                elif data_format == "json":
                    df = pd.read_json(data_source, lines=True)
                elif data_format == "tsv":
                    df = pd.read_csv(data_source, sep='\t', nrows=max_rows)
                else:
                    raise ValueError(f"Unsupported format: {data_format}")
                    
            else:
                # Treat as raw data string
                if data_format == "json" or self._looks_like_json(data_source):
                    data = json.loads(data_source)
                    df = pd.DataFrame(data)
                else:
                    # Try to parse as CSV
                    from io import StringIO
                    df = pd.read_csv(StringIO(data_source), nrows=max_rows)
            
            # Filter columns if specified
            columns = kwargs.get("columns", [])
            if columns:
                available_columns = [col for col in columns if col in df.columns]
                if available_columns:
                    df = df[available_columns]
            
            return df.head(max_rows) if len(df) > max_rows else df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def _detect_format(self, file_path: str) -> str:
        """Detect file format from extension."""
        extension = os.path.splitext(file_path)[1].lower()
        format_map = {
            '.csv': 'csv',
            '.json': 'json',
            '.tsv': 'tsv',
            '.txt': 'csv'
        }
        return format_map.get(extension, 'csv')
    
    def _looks_like_json(self, data: str) -> bool:
        """Check if string looks like JSON data."""
        try:
            json.loads(data)
            return True
        except:
            return False
    
    def _perform_analysis(self, df, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Perform the requested type of analysis."""
        if analysis_type == "summary":
            return self._summary_analysis(df)
        elif analysis_type == "correlation":
            return self._correlation_analysis(df)
        else:
            return self._summary_analysis(df)  # Default to summary
    
    def _summary_analysis(self, df) -> Dict[str, Any]:
        """Generate basic summary statistics and insights."""
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            categorical_columns = df.select_dtypes(include=['object']).columns
            
            summary = f"Dataset contains {len(df)} rows and {len(df.columns)} columns.\n"
            summary += f"Numeric columns: {len(numeric_columns)}, Categorical columns: {len(categorical_columns)}\n"
            
            insights = []
            statistics = {}
            
            # Basic statistics
            if len(numeric_columns) > 0:
                desc_stats = df[numeric_columns].describe()
                statistics["numeric_summary"] = desc_stats.to_dict()
                insights.append(f"Found {len(numeric_columns)} numeric columns")
            
            if len(categorical_columns) > 0:
                insights.append(f"Found {len(categorical_columns)} categorical columns")
            
            # Missing values analysis
            missing_counts = df.isnull().sum()
            missing_cols = missing_counts[missing_counts > 0]
            if len(missing_cols) > 0:
                insights.append(f"Missing values found in {len(missing_cols)} columns")
            
            return {
                "summary": summary,
                "insights": insights,
                "statistics": statistics
            }
        except Exception as e:
            return {
                "summary": f"Basic analysis completed with {len(df)} rows",
                "insights": [f"Analysis error: {str(e)}"],
                "statistics": {}
            }
    
    def _correlation_analysis(self, df) -> Dict[str, Any]:
        """Analyze correlations between numeric variables."""
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            
            if len(numeric_df.columns) < 2:
                return {
                    "summary": "Insufficient numeric columns for correlation analysis",
                    "insights": ["Need at least 2 numeric columns for correlation"],
                    "statistics": {}
                }
            
            corr_matrix = numeric_df.corr()
            
            # Find strong correlations
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        strong_corr.append(f"{col1} - {col2}: {corr_val:.3f}")
            
            insights = [f"Found {len(strong_corr)} strong correlations (>0.7)"] + strong_corr
            
            return {
                "summary": f"Correlation analysis of {len(numeric_df.columns)} numeric variables",
                "insights": insights,
                "statistics": {"correlation_matrix": corr_matrix.to_dict()}
            }
        except Exception as e:
            return {
                "summary": "Correlation analysis failed",
                "insights": [f"Error: {str(e)}"],
                "statistics": {}
            }
    
    def _create_visualizations(self, df, analysis_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Create visualizations based on analysis type."""
        if not ANALYTICS_AVAILABLE:
            return []
        
        try:
            visualizations = []
            
            # Create a simple histogram for numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                plt.figure(figsize=(10, 6))
                df[numeric_columns[0]].hist(bins=20)
                plt.title(f"Distribution of {numeric_columns[0]}")
                plt.xlabel(numeric_columns[0])
                plt.ylabel("Frequency")
                
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
                plt.close()
                
                visualizations.append({
                    "type": "histogram",
                    "title": f"Distribution of {numeric_columns[0]}",
                    "file_path": temp_file.name,
                    "description": f"Histogram showing the distribution of values in {numeric_columns[0]}"
                })
            
            return visualizations
            
        except Exception as e:
            print(f"Error creating visualizations: {e}")
            return []
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """Alternative entry point for backward compatibility."""
        data_source = kwargs.get("data_source", "")
        return self.execute(data_source, **kwargs)
