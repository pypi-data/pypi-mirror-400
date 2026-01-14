"""
Tests for the Target Questions Generator Agent.
"""
import pytest
import json
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

from target_questions_generator_agent.agent import TargetQuestionsGeneratorAgent
from target_questions_generator_agent.models import (
    TargetQuestionsGeneratorInput,
    DomainInfo,
    MLApproachInfo,
    DatasetInsights,
    DatasetColumnInsight
)


class TestTargetQuestionsGeneratorAgent:
    """Test cases for the Target Questions Generator Agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        return TargetQuestionsGeneratorAgent()
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input data."""
        domain_info = DomainInfo(
            business_domain_name="E-commerce",
            business_domain_info="Online retail platform",
            business_optimization_problems={"churn": "Customer retention"}
        )
        
        ml_approach = MLApproachInfo(
            name="binary_classification",
            description="Binary classification for churn prediction",
            constraints=["Must handle imbalanced data"]
        )
        
        dataset_insights = DatasetInsights(
            total_row_count=1000,
            column_insights={
                "customer_id": DatasetColumnInsight(
                    column_name="customer_id",
                    data_type="string",
                    unique_values=1000
                )
            }
        )
        
        raw_requirements = {
            "max_depth": {
                "type": "integer",
                "description": "Maximum depth of the decision tree",
                "default": 10,
                "min": 1,
                "max": 100
            },
            "learning_rate": {
                "type": "float",
                "description": "Learning rate for optimization",
                "default": 0.1,
                "min": 0.0,
                "max": 1.0
            }
        }
        
        return TargetQuestionsGeneratorInput(
            domain_info=domain_info,
            usecase_info={"name": "churn_prediction", "description": "Predict customer churn"},
            ml_approach=ml_approach,
            raw_requirements=raw_requirements,
            dataset_insights=dataset_insights,
            dataset_column_insights={}
        )
    
    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly."""
        assert agent is not None
        assert agent.ai_handler is not None
        assert agent.config is not None
        assert agent.logger is not None
    
    @patch('target_questions_generator_agent.agent.SFNAIHandler')
    def test_generate_questions_mock(self, mock_handler_class, agent, sample_input):
        """Test question generation with mocked LLM response."""
        # Mock LLM response
        mock_response = {
            "questions": [
                {
                    "raw_requirement_key": "max_depth",
                    "question": "What is the maximum depth for the decision tree?",
                    "ui_type": "text",
                    "options": ["5", "10", "15", "20"],
                    "default_value": "10",
                    "data_type": "integer",
                    "validation": {
                        "min": 1,
                        "max": 100,
                        "required": True,
                        "pattern": None,
                        "allowed_values": None
                    },
                    "help_text": "Enter a value between 1 and 100. Suggested values: 5, 10, 15, 20"
                }
            ]
        }
        
        # Setup mock
        mock_handler = MagicMock()
        mock_handler.route_to.return_value = (json.dumps(mock_response), {"cost": 0.01})
        mock_handler_class.return_value = mock_handler
        agent.ai_handler = mock_handler
        
        # Call method
        result = agent.generate_questions(sample_input)
        
        # Assertions
        assert result is not None
        assert len(result.questions) > 0
        assert result.status == "success"
    
    def test_validate_answers(self, agent):
        """Test batch validation of user answers."""
        questions = [
            {
                "raw_requirement_key": "max_depth",
                "data_type": "integer",
                "validation": {
                    "min": 1,
                    "max": 100,
                    "required": True
                }
            }
        ]
        
        user_answers = {
            "max_depth": "10"
        }
        
        result = agent.validate_answers(questions, user_answers)
        
        assert result is not None
        assert result.all_valid is True
        assert len(result.validation_results) == 1
        assert result.validated_answers["max_depth"] == 10
    
    def test_validate_answers_invalid(self, agent):
        """Test validation with invalid answers."""
        questions = [
            {
                "raw_requirement_key": "max_depth",
                "data_type": "integer",
                "validation": {
                    "min": 1,
                    "max": 100,
                    "required": True
                }
            }
        ]
        
        user_answers = {
            "max_depth": "150"  # Exceeds max
        }
        
        result = agent.validate_answers(questions, user_answers)
        
        assert result is not None
        assert result.all_valid is False
        assert len(result.errors) > 0
    
    def test_process_llm_response_json(self, agent):
        """Test processing LLM response with JSON."""
        response = '{"questions": [{"key": "test"}]}'
        result = agent._process_llm_response(response)
        assert isinstance(result, dict)
        assert "questions" in result
    
    def test_process_llm_response_code_block(self, agent):
        """Test processing LLM response with code blocks."""
        response = '```json\n{"questions": [{"key": "test"}]}\n```'
        result = agent._process_llm_response(response)
        assert isinstance(result, dict)
        assert "questions" in result

