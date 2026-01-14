"""
Target Questions Generator Agent Package

An intelligent agent for converting technical ML requirements into 
user-friendly, domain-aware questions for interactive interfaces.
"""

# Use relative imports (matches target_synthesis_agent pattern)
from .agent import TargetQuestionsGeneratorAgent
from .models import (
    TargetQuestionsGeneratorInput,
    TargetQuestionsGeneratorOutput,
    QuestionItem,
    ValidationRules,
    ValidationResult,
    BatchValidationResult,
    DomainInfo,
    MLApproachInfo,
    DatasetInsights,
    DatasetColumnInsight,
    AgentInputsResult,
    AgentInputsRequest,
    DataFrameInputsRequest
)
from .config import TargetQuestionsGeneratorConfig

__version__ = "1.0.0"
__all__ = [
    "TargetQuestionsGeneratorAgent",
    "TargetQuestionsGeneratorInput",
    "TargetQuestionsGeneratorOutput",
    "QuestionItem",
    "ValidationRules",
    "ValidationResult",
    "BatchValidationResult",
    "DomainInfo",
    "MLApproachInfo",
    "DatasetInsights",
    "DatasetColumnInsight",
    "AgentInputsResult",
    "AgentInputsRequest",
    "DataFrameInputsRequest",
    "TargetQuestionsGeneratorConfig"
]

