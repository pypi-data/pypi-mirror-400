"""
Utility functions for the Target Questions Generator Agent.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import traceback
import pandas as pd
from dataclasses import asdict

from .models import (
    AgentInputsResult, DomainInfo, MLApproachInfo, 
    DatasetInsights, DatasetColumnInsight
)

logger = logging.getLogger(__name__)


def prepare_agents_input_by_sql(
    conn: Any,
    customer_id: str,
    auth_service_base_url: str,
    project_name: str,
    table_name: str,
    mappings: Dict[str, Any],
    use_case: str,
    ml_approach: str,
    experiment_type: Optional[str] = None,
    schema: Optional[str] = None
) -> AgentInputsResult:
    """
    Prepare inputs for agent operations by fetching domain, usecase, dataset insights from database.
    
    Args:
        conn: Database connection object
        customer_id: ID of the customer
        auth_service_base_url: Base URL for authentication service
        project_name: Name of the project
        table_name: Name of the table to analyze
        mappings: Column mappings provided by the user
        use_case: Business use case name
        ml_approach: Selected ML approach
        experiment_type: Type of experiment (optional)
        schema: Database schema (optional)
        
    Returns:
        AgentInputsResult containing all prepared inputs and any failures
    """
    result = AgentInputsResult()
    
    try:
        # Clean and validate mappings
        cleaned_mappings = _clean_mappings(mappings)
        
        # Get domain and use case info
        result.domain_info, result.usecase_info = _get_domain_and_usecase_info(
            conn, customer_id, use_case, result
        )
        
        # Get ML approach info
        result.ml_approach = _get_ml_approach_info(ml_approach, result)
        
        # Get required columns
        result.required_columns = _get_required_columns(conn, project_name, result)
        
        # Get dataset insights
        dataset_insights = _get_dataset_insights(conn, project_name, table_name, result)
        if dataset_insights:
            result.dataset_insights = dataset_insights
        
        # Get column insights
        result.dataset_column_insights = _get_column_insights(
            conn, project_name, table_name, cleaned_mappings, 
            result.required_columns, result
        )
        
    except Exception as e:
        error_msg = f"Unexpected error in prepare_agents_input: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result.failed_operations["prepare_agents_input"] = error_msg
    
    return result


def prepare_agents_input_by_df(
    df: pd.DataFrame,
    customer_id: str,
    project_name: str,
    mappings: Dict[str, Any],
    use_case: str,
    ml_approach: str,
    experiment_type: Optional[str] = None,
    schema: Optional[str] = None
) -> AgentInputsResult:
    """
    Prepare inputs for agent operations using a pandas DataFrame.
    
    Args:
        df: pandas DataFrame containing the data
        customer_id: ID of the customer
        project_name: Name of the project
        mappings: Column mappings provided by the user
        use_case: Business use case name
        ml_approach: Selected ML approach
        experiment_type: Type of experiment (optional)
        schema: Database schema (optional, for compatibility)
        
    Returns:
        AgentInputsResult containing all prepared inputs and any failures
    """
    result = AgentInputsResult()
    
    try:
        # Clean and validate mappings
        cleaned_mappings = _clean_mappings(mappings)
        
        # Get ML approach info
        result.ml_approach = _get_ml_approach_info(ml_approach, result)
        
        # Get dataset insights from DataFrame
        result.dataset_insights = _get_dataset_insights_from_df(df, result)
        
        # Get column insights from DataFrame
        result.dataset_column_insights = _get_column_insights_from_df(
            df, cleaned_mappings, result
        )
        
        # For DataFrame mode, we may not have domain/usecase info
        # These would need to be provided separately or fetched from another source
        result.domain_info = DomainInfo()
        result.usecase_info = {"use_case": use_case}
        
    except Exception as e:
        error_msg = f"Unexpected error in prepare_agents_input_by_df: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result.failed_operations["prepare_agents_input_by_df"] = error_msg
    
    return result


def _clean_mappings(mappings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and validate the column mappings.
    
    Args:
        mappings: Raw column mappings
        
    Returns:
        Cleaned and validated mappings
    """
    cleaned = mappings.copy()
    keys_to_drop = ['primary_category', 'categories_present']
    
    try:
        # If mappings is a string, try to evaluate it
        if isinstance(mappings, str):
            try:
                import ast
                cleaned = ast.literal_eval(mappings)
                if not isinstance(cleaned, dict):
                    logger.warning(f"String evaluation resulted in {type(cleaned)}, not a dictionary")
                    cleaned = {}
            except (ValueError, SyntaxError) as e:
                logger.warning(f"Failed to convert string to dictionary: {e}")
                cleaned = {}
        
        # Remove unwanted keys
        for key in list(cleaned.keys()):
            if key.lower() in keys_to_drop:
                del cleaned[key]
                
    except Exception as e:
        logger.error(f"Error cleaning mappings: {str(e)}")
        logger.error(traceback.format_exc())
        cleaned = {}
        
    return cleaned


def _get_domain_and_usecase_info(
    conn: Any, 
    customer_id: str,
    use_case: str,
    result: AgentInputsResult
) -> Tuple[DomainInfo, Dict[str, Any]]:
    """
    Get domain and use case information from database.
    
    Args:
        conn: Database connection
        customer_id: ID of the customer
        use_case: Business use case name
        result: AgentInputsResult to track failures
        
    Returns:
        Tuple of (DomainInfo, usecase_info)
    """
    domain_info = DomainInfo()
    usecase_info = {}
    
    try:
        query = f"""
            SELECT name as domain_name, description, use_case_pack 
            FROM public.domains
            WHERE id IN (
                SELECT domain_id
                FROM public.customer_domain
                WHERE customer_id = {customer_id}
            )
            AND status = 'Completed';
        """
        
        domain_data = _fetch_data(conn, query, fetch="all", mappings=True)
        
        if domain_data:
            domain = domain_data[0]  # Single domain assumption
            domain_info.business_domain_name = domain.get("domain_name")
            domain_info.business_domain_info = domain.get("description")
            
            # Extract use case info
            if "use_case_pack" in domain and "use_case" in domain["use_case_pack"]:
                usecases = domain["use_case_pack"]["use_case"]
                domain_info.business_optimization_problems = {
                    uc["label"]: uc["labels"] for uc in usecases.values()
                }
                
                # Get specific use case info if available
                usecase_info = domain_info.business_optimization_problems.get(use_case, {})
                
    except Exception as e:
        error_msg = f"Failed to get domain and use case info: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result.failed_operations["get_domain_and_usecase_info"] = error_msg
    
    return domain_info, usecase_info


def _get_ml_approach_info(ml_approach: str, result: AgentInputsResult) -> MLApproachInfo:
    """
    Get ML approach information.
    
    Args:
        ml_approach: Name of the ML approach
        result: AgentInputsResult to track failures
        
    Returns:
        MLApproachInfo object
    """
    approach_info = MLApproachInfo(name=ml_approach)
    
    try:
        # This is a placeholder - in a real implementation, you would fetch this from a config or database
        approach_info.description = f"ML approach: {ml_approach}"
        approach_info.constraints = [
            "Must maintain data integrity",
            "Should be compatible with the selected algorithm"
        ]
        
    except Exception as e:
        error_msg = f"Failed to get ML approach info: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result.failed_operations["get_ml_approach_info"] = error_msg
    
    return approach_info


def _get_required_columns(conn: Any, project_name: str, result: AgentInputsResult) -> List[str]:
    """
    Get required columns for the project.
    
    Args:
        conn: Database connection
        project_name: Name of the project
        result: AgentInputsResult to track failures
        
    Returns:
        List of required column names
    """
    required_columns = []
    
    try:
        # This is a placeholder - implement based on your database schema
        # You might query a project configuration table or similar
        pass
        
    except Exception as e:
        error_msg = f"Failed to get required columns: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result.failed_operations["get_required_columns"] = error_msg
    
    return required_columns


def _get_dataset_insights(
    conn: Any, 
    project_name: str, 
    table_name: str,
    result: AgentInputsResult
) -> Optional[DatasetInsights]:
    """
    Get general dataset insights from database.
    
    Args:
        conn: Database connection
        project_name: Name of the project
        table_name: Name of the table
        result: AgentInputsResult to track failures
        
    Returns:
        DatasetInsights object or None
    """
    insights = DatasetInsights()
    
    try:
        # Get row count
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        count_result = _fetch_data(conn, count_query, fetch="one")
        if count_result:
            insights.total_row_count = count_result.get("count", 0)
        
    except Exception as e:
        error_msg = f"Failed to get dataset insights: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result.failed_operations["get_dataset_insights"] = error_msg
        return None
    
    return insights


def _get_column_insights(
    conn: Any,
    project_name: str,
    table_name: str,
    mappings: Dict[str, Any],
    required_columns: List[str],
    result: AgentInputsResult
) -> Dict[str, Any]:
    """
    Get column-level insights from database.
    
    Args:
        conn: Database connection
        project_name: Name of the project
        table_name: Name of the table
        mappings: Column mappings
        required_columns: List of required columns
        result: AgentInputsResult to track failures
        
    Returns:
        Dictionary of column insights
    """
    column_insights = {}
    
    try:
        # Get all columns to analyze
        columns_to_analyze = list(mappings.values()) + required_columns
        
        for col in columns_to_analyze:
            if not col:
                continue
                
            try:
                # Get basic stats
                stats_query = f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(DISTINCT {col}) as unique_count,
                        COUNT(*) - COUNT({col}) as null_count,
                        MIN({col}) as min_val,
                        MAX({col}) as max_val,
                        AVG({col}) as avg_val
                    FROM {table_name}
                """
                
                stats = _fetch_data(conn, stats_query, fetch="one")
                
                if stats:
                    total = stats.get("total_count", 0)
                    null_count = stats.get("null_count", 0)
                    
                    column_insights[col] = {
                        "data_type": "unknown",  # Would need to query schema
                        "unique_values": stats.get("unique_count", 0),
                        "missing_percentage": (null_count / total) if total > 0 else 0.0,
                        "min_value": stats.get("min_val"),
                        "max_value": stats.get("max_val"),
                        "mean": stats.get("avg_val")
                    }
                    
            except Exception as col_error:
                logger.warning(f"Failed to get insights for column {col}: {str(col_error)}")
                continue
                
    except Exception as e:
        error_msg = f"Failed to get column insights: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result.failed_operations["get_column_insights"] = error_msg
    
    return column_insights


def _get_dataset_insights_from_df(df: pd.DataFrame, result: AgentInputsResult) -> DatasetInsights:
    """
    Get dataset insights from a pandas DataFrame.
    
    Args:
        df: pandas DataFrame
        result: AgentInputsResult to track failures
        
    Returns:
        DatasetInsights object
    """
    insights = DatasetInsights()
    
    try:
        insights.total_row_count = len(df)
        
        # Build column insights
        for col in df.columns:
            col_insight = DatasetColumnInsight(column_name=col)
            col_insight.data_type = str(df[col].dtype)
            col_insight.unique_values = df[col].nunique()
            col_insight.missing_percentage = (df[col].isna().sum() / len(df)) * 100
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_insight.min_value = float(df[col].min())
                col_insight.max_value = float(df[col].max())
                col_insight.mean = float(df[col].mean())
                col_insight.median = float(df[col].median())
                col_insight.std_dev = float(df[col].std())
            
            insights.column_insights[col] = col_insight
            
    except Exception as e:
        error_msg = f"Failed to get dataset insights from DataFrame: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result.failed_operations["get_dataset_insights_from_df"] = error_msg
    
    return insights


def _get_column_insights_from_df(
    df: pd.DataFrame,
    mappings: Dict[str, Any],
    result: AgentInputsResult
) -> Dict[str, Any]:
    """
    Get column-level insights from a pandas DataFrame.
    
    Args:
        df: pandas DataFrame
        mappings: Column mappings
        result: AgentInputsResult to track failures
        
    Returns:
        Dictionary of column insights
    """
    column_insights = {}
    
    try:
        columns_to_analyze = list(mappings.values())
        
        for col in columns_to_analyze:
            if col not in df.columns:
                continue
                
            try:
                col_series = df[col]
                total = len(col_series)
                
                column_insights[col] = {
                    "data_type": str(col_series.dtype),
                    "unique_values": col_series.nunique(),
                    "missing_percentage": (col_series.isna().sum() / total) * 100 if total > 0 else 0.0,
                }
                
                if pd.api.types.is_numeric_dtype(col_series):
                    column_insights[col].update({
                        "min_value": float(col_series.min()),
                        "max_value": float(col_series.max()),
                        "mean": float(col_series.mean()),
                        "median": float(col_series.median()),
                        "std_dev": float(col_series.std())
                    })
                    
            except Exception as col_error:
                logger.warning(f"Failed to get insights for column {col}: {str(col_error)}")
                continue
                
    except Exception as e:
        error_msg = f"Failed to get column insights from DataFrame: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        result.failed_operations["get_column_insights_from_df"] = error_msg
    
    return column_insights


def _fetch_data(conn: Any, query: str, fetch: str = "all", mappings: bool = False) -> Any:
    """
    Fetch data from database connection.
    
    Args:
        conn: Database connection
        query: SQL query string
        fetch: "all" or "one"
        mappings: Whether to use mappings for result
        
    Returns:
        Query results
    """
    try:
        if hasattr(conn, 'execute'):
            result = conn.execute(query)
            if fetch == "one":
                row = result.fetchone()
                if row and hasattr(row, '_mapping'):
                    return dict(row._mapping) if mappings else row
                elif row:
                    return dict(row) if mappings else row
                return None
            else:
                rows = result.fetchall()
                if rows and hasattr(rows[0], '_mapping'):
                    return [dict(row._mapping) for row in rows] if mappings else rows
                elif rows:
                    return [dict(row) for row in rows] if mappings else rows
                return []
        else:
            # Fallback for other connection types
            cursor = conn.cursor()
            cursor.execute(query)
            if fetch == "one":
                return cursor.fetchone()
            else:
                return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise

