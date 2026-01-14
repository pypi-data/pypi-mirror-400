"""
Data models for the Target Questions Generator Agent.

This module defines all Pydantic models and dataclasses used for:
- Input data structures
- Output question structures
- Validation structures
"""

from typing import List, Dict, Any, Optional, Union, TypedDict
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# =============================================================================
# INPUT MODELS
# =============================================================================

@dataclass
class DomainInfo:
    """Domain information for the customer."""
    business_domain_name: Optional[str] = None
    business_domain_info: Optional[str] = None
    # business_optimization_problems: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "business_domain_name": self.business_domain_name,
            "business_domain_info": self.business_domain_info,
            # "business_optimization_problems": self.business_optimization_problems
        }


@dataclass
class MLApproachInfo:
    """Machine learning approach information."""
    name: Optional[str] = None
    description: Optional[str] = None
    # constraints: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            # "constraints": self.constraints
        }


@dataclass
class DatasetColumnInsight:
    """Insights about a dataset column."""
    column_name: str
    data_type: Optional[str] = None
    unique_values: Optional[int] = None
    missing_percentage: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    mode: Optional[Any] = None
    std_dev: Optional[float] = None


@dataclass
class DatasetInsights:
    """General insights about the dataset."""
    total_row_count: Optional[int] = None
    column_insights: Dict[str, DatasetColumnInsight] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_row_count": self.total_row_count,
            "column_insights": {
                col: {
                    "data_type": insight.data_type,
                    "unique_values": insight.unique_values,
                    "missing_percentage": insight.missing_percentage,
                    "min_value": insight.min_value,
                    "max_value": insight.max_value,
                    "mean": insight.mean,
                    "median": insight.median,
                    "mode": insight.mode,
                    "std_dev": insight.std_dev
                }
                for col, insight in self.column_insights.items()
            }
        }


class TargetQuestionsGeneratorInput(BaseModel):
    """Input structure for the Target Questions Generator Agent."""
    
    domain_info: DomainInfo = Field(..., description="Domain information")
    usecase_info: Dict[str, Any] = Field(..., description="Use case information (name, description)")
    ml_approach: MLApproachInfo = Field(..., description="ML approach information")
    raw_requirements: Dict[str, Any] = Field(..., description="Raw technical requirements dictionary")
    dataset_insights: DatasetInsights = Field(..., description="General dataset insights")
    dataset_column_insights: Dict[str, Any] = Field(default_factory=dict, description="Column-level insights")


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class ValidationRules(BaseModel):
    """Validation rules for a question input."""
    
    min: Optional[float] = Field(None, description="Minimum value (for numeric types)")
    max: Optional[float] = Field(None, description="Maximum value (for numeric types)")
    required: bool = Field(True, description="Whether the field is required")
    pattern: Optional[str] = Field(None, description="Regex pattern for string validation")
    allowed_values: Optional[List[str]] = Field(None, description="List of allowed values (for enum types)")

    @field_validator("allowed_values", mode="before")
    @classmethod
    def normalize_allowed_values(cls, v):
        if v is None:
            return v
        if isinstance(v, list):
            return [str(item) for item in v]
        return v
    

class QuestionItem(BaseModel):
    """Individual question structure for user-friendly question generation."""
    
    raw_requirement_key: str = Field(..., description="Key from raw technical requirements")
    question: str = Field(..., description="User-friendly, domain-aware question text")
    ui_type: str = Field(default="dropdown", description="UI input type (currently always 'text')")
    options: List[str] = Field(default_factory=list, description="Suggested options for help text")
    default_value: str = Field(default="", description="Prefilled default value")
    data_type: str = Field(..., description="Data type: 'string', 'integer', 'float', 'boolean', 'date'")
    validation: ValidationRules = Field(..., description="Validation rules for this question")
    help_text: str = Field(..., description="Help text including options as examples")


class TargetQuestionsGeneratorOutput(BaseModel):
    """Complete output structure from the Target Questions Generator Agent."""
    
    questions: List[QuestionItem] = Field(..., description="List of generated questions")
    status: str = Field(default="success", description="Status: 'success' or 'error'")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    failed_operations: Optional[Dict[str, str]] = Field(None, description="Failed operations tracking")


# =============================================================================
# VALIDATION MODELS
# =============================================================================

class ValidationResult(BaseModel):
    """Result of validating a single user answer."""
    
    question_key: str = Field(..., description="Key of the question being validated")
    is_valid: bool = Field(..., description="Whether the answer is valid")
    error_message: Optional[str] = Field(None, description="Error message if invalid")
    validated_value: Any = Field(..., description="Validated and converted value")
    original_value: str = Field(..., description="Original user input text")


class BatchValidationResult(BaseModel):
    """Results of batch validation for all questions."""
    
    overall_status: str = Field(..., description="Overall status: 'success' or 'error'")
    validation_results: List[ValidationResult] = Field(..., description="Individual validation results")
    all_valid: bool = Field(..., description="Whether all answers are valid")
    errors: List[Dict[str, str]] = Field(default_factory=list, description="List of errors if any")
    validated_answers: Dict[str, Any] = Field(..., description="Dictionary of validated answers (key: question_key, value: validated_value)")


# =============================================================================
# UTILITY MODELS (for input preparation)
# =============================================================================

@dataclass
class AgentInputsResult:
    """Result of preparing agent inputs."""
    # Main data
    domain_info: DomainInfo = field(default_factory=DomainInfo)
    usecase_info: Dict[str, Any] = field(default_factory=dict)
    ml_approach: MLApproachInfo = field(default_factory=MLApproachInfo)
    required_columns: List[str] = field(default_factory=list)
    dataset_column_insights: Dict[str, Any] = field(default_factory=dict)
    dataset_insights: DatasetInsights = field(default_factory=DatasetInsights)
    
    # Tracking failed operations
    failed_operations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain_info": self.domain_info.to_dict(),
            "usecase_info": self.usecase_info,
            "ml_approach": self.ml_approach.to_dict(),
            "required_columns": self.required_columns,
            "dataset_column_insights": self.dataset_column_insights,
            "dataset_insights": self.dataset_insights.to_dict(),
            "failed_operations": self.failed_operations
        }


class AgentInputsRequest(TypedDict, total=False):
    """Input parameters for prepare_agents_input function."""
    conn: Any  # Database connection
    auth_service_base_url: str
    project_name: str
    schema: Optional[str] = None
    table_name: str
    mappings: Dict[str, Any]
    use_case: str
    ml_approach: str
    experiment_type: Optional[str] = None


@dataclass
class DataFrameInputsRequest:
    """Input parameters for prepare_agents_input function using DataFrame."""
    df: Any  # pandas DataFrame
    customer_id: str
    project_name: str
    mappings: Dict[str, Any]
    use_case: str
    ml_approach: str
    experiment_type: Optional[str] = None
    schema: Optional[str] = None  # Optional for compatibility

