"""
Target Questions Generator Agent - Converts technical requirements to user-friendly questions.

This agent uses LLM intelligence to convert technical ML requirements into
domain-aware, contextual questions for interactive user interfaces.
"""

import logging
import sys
import json
import traceback
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import os

# Import sfn_blueprint components (matching target_synthesis_agent pattern)
from sfn_blueprint import (
    SFNAIHandler,
    SFNConfigManager,  # Optional
    WorkflowStorageManager,  # Optional
    Task,  # Optional
    # Note: Do NOT import setup_logger - use manual logging setup instead
)

from .config import TargetQuestionsGeneratorConfig
from .constants import (
    format_system_prompt_question_generator,
    format_user_prompt_question_generator
)
from .models import (
    TargetQuestionsGeneratorInput,
    TargetQuestionsGeneratorOutput,
    ValidationResult,
    BatchValidationResult
)

# Default config (matching pattern from target_synthesis_agent)
DEFAULT_CONFIG = {
    "model": "gpt-4.1-mini",
    "temperature": 0.2,
    "max_retries": 3,
    "timeout": 300,
    "max_tokens": 4000
}


class TargetQuestionsGeneratorAgent:
    """
    Intelligent agent for generating user-friendly questions from technical ML requirements.
    Uses LLM to convert technical parameters into domain-aware, contextual questions.
    """
    
    def __init__(self, config: Optional[TargetQuestionsGeneratorConfig] = None):
        """
        Initialize the agent with configuration.
        
        Args:
            config: Optional TargetQuestionsGeneratorConfig instance. 
                   If not provided, a default will be used.
        """
        # Initialize configuration
        self.config = config or TargetQuestionsGeneratorConfig()
        
        # Set OPENAI_API_KEY environment variable if LLM_API_KEY is set and provider is openai
        # This is needed because sfn_blueprint reads from OPENAI_API_KEY
        if self.config.ai_provider == "openai" and self.config.api_key:
            os.environ["OPENAI_API_KEY"] = self.config.api_key
        
        # Setup logging (matching target_synthesis_agent pattern)
        # Use manual logging setup, NOT setup_logger from sfn_blueprint
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:  # Only add handlers if none exist
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Initialize sfn_blueprint components
        # CENTRALIZED LLM HANDLER - single instance for all LLM calls
        self.ai_handler = SFNAIHandler()
        
        # Optional components (matching target_synthesis_agent)
        # Make config_manager optional - handle if config file doesn't exist
        try:
            self.config_manager = SFNConfigManager()  # Optional
        except Exception as e:
            self.logger.warning(f"Could not initialize config manager: {e}")
            self.config_manager = None
        
        # Optional workflow storage (matching target_synthesis_agent)
        workflow_base_path = "workflows"
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(workflow_base_path, exist_ok=True)
        
        self.workflow_storage = WorkflowStorageManager(
            workflow_base_path=workflow_base_path,
            workflow_id=workflow_id
        )
        
        # Load configuration
        self._load_config()
        
        # Initialize execution tracking
        self.execution_history: List[Dict[str, Any]] = []
        self.current_task: Optional[Task] = None
    
    def _load_config(self) -> None:
        """Load configuration from sfn_blueprint config manager."""
        # Set default config
        self.llm_config = DEFAULT_CONFIG.copy()
        
        try:
            # Try to get config from config manager if available
            if self.config_manager and hasattr(self.config_manager, 'config'):
                model_config = self.config_manager.config.get('model_config', {})
                if model_config:
                    self.llm_config.update(model_config)
                    self.logger.info("Updated configuration with model-specific settings")
            
            self.logger.info(f"Using configuration: {self.llm_config}")
            
        except Exception as e:
            self.logger.warning(f"Could not load external config: {e}")
            # Fall back to default config
            self.llm_config = DEFAULT_CONFIG
    
    def generate_questions(
        self,
        input_data: TargetQuestionsGeneratorInput
    ) -> TargetQuestionsGeneratorOutput:
        """
        Main method: Generate user-friendly questions from technical requirements.
        All logic is LLM-powered - no hardcoded rules.
        
        Args:
            input_data: TargetQuestionsGeneratorInput containing all required inputs
            
        Returns:
            TargetQuestionsGeneratorOutput with generated questions
        """
        try:
            # Format prompts using constants
            system_prompt = format_system_prompt_question_generator()
            user_prompt = format_user_prompt_question_generator(
                domain_info=input_data.domain_info.to_dict(),
                usecase_info=input_data.usecase_info,
                ml_approach=input_data.ml_approach.to_dict(),
                raw_requirements=input_data.raw_requirements,
                dataset_insights=input_data.dataset_insights.to_dict(),
                column_insights=input_data.dataset_column_insights
            )
            
            # CENTRALIZED LLM CALL - using single ai_handler instance
            response, token_cost = self.ai_handler.route_to(
                llm_provider=self.config.ai_provider,
                configuration={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "model": self.config.model_name,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                    "api_key": self.config.api_key
                },
                model=self.config.model_name
            )
            
            # Log token cost (optional, matching pattern from other agents)
            if token_cost:
                self.logger.info(f"Token cost: {token_cost}")
            
            # Process LLM response
            # route_to returns (formatted_response, token_cost_summary)
            # formatted_response should be a string after llm_response_formatter
            # But if it's still a ParsedResponse object, extract text manually
            response_text = response[0] if isinstance(response, tuple) else response
            
            # If response is still a ParsedResponse object, extract text
            if hasattr(response_text, 'output'):
                # Extract from ParsedResponse format
                if hasattr(response_text.output[0], 'content') and len(response_text.output[0].content) > 0:
                    response_text = response_text.output[0].content[0].text
                elif hasattr(response_text, 'choices') and len(response_text.choices) > 0:
                    response_text = response_text.choices[0].message.content
                else:
                    response_text = str(response_text)
            
            parsed_response = self._process_llm_response(response_text)
            
            # Validate with Pydantic model
            return TargetQuestionsGeneratorOutput.model_validate(parsed_response)
            
        except Exception as e:
            self.logger.error(f"Error generating questions: {str(e)}\n{traceback.format_exc()}")
            raise
    
    def _process_llm_response(self, response: Union[str, Dict]) -> Dict[str, Any]:
        """
        Process and validate LLM response.
        
        Handles:
        - JSON parsing from string
        - Code block removal (```json ... ```)
        - Error handling
        - Returns dict ready for Pydantic validation
        
        Args:
            response: LLM response (string or dict)
            
        Returns:
            Dict ready for Pydantic model validation
        """
        try:
            if isinstance(response, dict):
                return response
            
            # Remove code blocks if present
            response_text = str(response).strip()
            if "```json" in response_text:
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif "```" in response_text:
                response_text = response_text.replace("```", "").strip()
            
            # Parse JSON
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {e}")
            self.logger.debug(f"Response text: {response_text[:500]}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        except Exception as e:
            self.logger.error(f"Error processing LLM response: {e}")
            raise
    
    def validate_answers(
        self,
        questions: List[Dict[str, Any]],
        user_answers: Dict[str, str]
    ) -> BatchValidationResult:
        """
        Batch validation method: Validates all user answers when submitted.
        This is rule-based validation (not LLM-based) against LLM-generated validation rules.
        
        Args:
            questions: List of question items (from generate_questions output)
            user_answers: Dictionary of user answers (key: question_key, value: user_input_string)
            
        Returns:
            BatchValidationResult with validation results for all questions
        """
        validation_results = []
        all_valid = True
        errors = []
        validated_answers = {}
        
        try:
            for question in questions:
                question_key = question.get("raw_requirement_key") or question.get("raw_requirement_key", "")
                user_answer = user_answers.get(question_key, "")
                validation_rules = question.get("validation", {})
                data_type = question.get("data_type", "string")
                
                # Validate single answer
                result = self._validate_single_answer(
                    question_key=question_key,
                    user_answer=user_answer,
                    validation_rules=validation_rules,
                    data_type=data_type,
                    required=validation_rules.get("required", True)
                )
                
                validation_results.append(result)
                
                if not result.is_valid:
                    all_valid = False
                    errors.append({
                        "question_key": question_key,
                        "error": result.error_message or "Validation failed"
                    })
                else:
                    validated_answers[question_key] = result.validated_value
            
            overall_status = "success" if all_valid else "error"
            
            return BatchValidationResult(
                overall_status=overall_status,
                validation_results=validation_results,
                all_valid=all_valid,
                errors=errors,
                validated_answers=validated_answers
            )
            
        except Exception as e:
            self.logger.error(f"Error in batch validation: {str(e)}\n{traceback.format_exc()}")
            raise
    
    def _validate_single_answer(
        self,
        question_key: str,
        user_answer: str,
        validation_rules: Dict[str, Any],
        data_type: str,
        required: bool
    ) -> ValidationResult:
        """
        Validate a single user answer against validation rules.
        
        Args:
            question_key: Key of the question
            user_answer: User's text input
            validation_rules: Validation rules from question
            data_type: Expected data type
            required: Whether field is required
            
        Returns:
            ValidationResult
        """
        original_value = user_answer
        validated_value = None
        is_valid = True
        error_message = None
        
        try:
            # Check required
            if required and (not user_answer or user_answer.strip() == ""):
                return ValidationResult(
                    question_key=question_key,
                    is_valid=False,
                    error_message="This field is required",
                    validated_value=None,
                    original_value=original_value
                )
            
            # If not required and empty, return valid with None
            if not required and (not user_answer or user_answer.strip() == ""):
                return ValidationResult(
                    question_key=question_key,
                    is_valid=True,
                    error_message=None,
                    validated_value=None,
                    original_value=original_value
                )
            
            # Type conversion and validation
            if data_type == "integer":
                try:
                    validated_value = int(user_answer)
                    if validation_rules.get("min") is not None and validated_value < validation_rules["min"]:
                        is_valid = False
                        error_message = f"Value must be at least {validation_rules['min']}"
                    if validation_rules.get("max") is not None and validated_value > validation_rules["max"]:
                        is_valid = False
                        error_message = f"Value must be at most {validation_rules['max']}"
                except ValueError:
                    is_valid = False
                    error_message = "Invalid integer value"
                    
            elif data_type == "float":
                try:
                    validated_value = float(user_answer)
                    if validation_rules.get("min") is not None and validated_value < validation_rules["min"]:
                        is_valid = False
                        error_message = f"Value must be at least {validation_rules['min']}"
                    if validation_rules.get("max") is not None and validated_value > validation_rules["max"]:
                        is_valid = False
                        error_message = f"Value must be at most {validation_rules['max']}"
                except ValueError:
                    is_valid = False
                    error_message = "Invalid float value"
                    
            elif data_type == "boolean":
                validated_value = user_answer.lower() in ["true", "1", "yes", "on"]
                
            elif data_type == "date":
                # Basic date validation - could be enhanced
                validated_value = user_answer  # Keep as string for now
                
            else:  # string
                validated_value = user_answer
                # Check pattern if provided
                if validation_rules.get("pattern"):
                    import re
                    if not re.match(validation_rules["pattern"], user_answer):
                        is_valid = False
                        error_message = "Value does not match required pattern"
            
            # Check allowed values if provided
            if validation_rules.get("allowed_values"):
                if validated_value not in validation_rules["allowed_values"]:
                    is_valid = False
                    error_message = f"Value must be one of: {', '.join(validation_rules['allowed_values'])}"
            
            return ValidationResult(
                question_key=question_key,
                is_valid=is_valid,
                error_message=error_message,
                validated_value=validated_value,
                original_value=original_value
            )
            
        except Exception as e:
            self.logger.error(f"Error validating answer for {question_key}: {str(e)}")
            return ValidationResult(
                question_key=question_key,
                is_valid=False,
                error_message=f"Validation error: {str(e)}",
                validated_value=None,
                original_value=original_value
            )

