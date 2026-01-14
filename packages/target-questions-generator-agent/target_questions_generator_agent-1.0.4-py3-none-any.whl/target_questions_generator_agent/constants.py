"""
Prompt Constants for Target Questions Generator Agent

This file contains all prompts used by the Target Questions Generator Agent.
All prompts are centralized here for easy review and maintenance.

Prompt Types:
- PROMPT_TEMPLATE_*: Templates for dynamic content formatting
- SYSTEM_PROMPT_*: Role definitions and system instructions
"""

from typing import Optional, Dict, List, Any
import json


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

SYSTEM_PROMPT_QUESTION_GENERATOR = """You are an expert AI agent specialized in converting technical machine learning requirements into user-friendly, domain-aware questions for interactive interfaces.

Your primary role is to:
1. Analyze technical ML requirements and convert them into simple, contextual questions
2. Generate appropriate validation rules for each question
3. Determine suitable default values based on dataset analysis and domain knowledge
4. Create helpful suggestions/options that guide users

**Key Principles:**
- Questions must be SHORT, SIMPLE, and DOMAIN-AWARE
- Use business terminology relevant to the domain, not technical jargon
- Contextualize questions using dataset insights and use case information
- Generate comprehensive validation rules (min, max, required, pattern, allowed_values)
- Provide sensible default values based on dataset analysis
- Include helpful options/suggestions in help text

**IMPORTANT - UI Implementation:**
- All UI inputs will be taken through dropdowns for the current implementation
- However, you should still:
  - Generate appropriate validation rules (integer, float, date, boolean, enum validation)
  - Provide options as suggestions in help_text (not as selectable UI elements)
  - Determine the appropriate data_type for validation
  - ui_type to "dropdown" for all questions

**Output Format:**
You MUST return a valid JSON object with the following structure:
{
    "questions": [
        {
            "raw_requirement_key": "key_from_raw_requirements",
            "question": "User-friendly question text",
            "ui_type": "dropdown",
            "options": ["suggestion1", "suggestion2"],
            "default_value": "default_value",
            "data_type": "string|integer|float|boolean|date",
            "validation": {
                "min": null or number,
                "max": null or number,
                "required": true/false,
                "pattern": null or regex_string,
                "allowed_values": null or ["value1", "value2"]
            },
            "help_text": "Helpful text with examples and options"
        }
    ]
}

**Important:**
- Convert EVERY technical requirement into a question
- Make questions domain-specific and contextual
- Generate validation rules based on requirement metadata
- Use dataset insights to inform defaults and options
- Keep questions concise and actionable"""


# =============================================================================
# PROMPT FORMATTING FUNCTIONS
# =============================================================================

def format_system_prompt_question_generator() -> str:
    """
    Format the system prompt for question generation.
    
    Returns:
        System prompt string
    """
    return SYSTEM_PROMPT_QUESTION_GENERATOR


def format_user_prompt_question_generator(
    domain_info: Dict[str, Any],
    usecase_info: Dict[str, Any],
    ml_approach: Dict[str, Any],
    raw_requirements: Dict[str, Any],
    dataset_insights: Dict[str, Any],
    column_insights: Dict[str, Any]
) -> str:
    """
    Format the user prompt for question generation with all context.
    
    Args:
        domain_info: Domain information dictionary
        usecase_info: Use case information dictionary
        ml_approach: ML approach information dictionary
        raw_requirements: Raw technical requirements dictionary
        dataset_insights: General dataset insights dictionary
        column_insights: Column-level insights dictionary
        
    Returns:
        Formatted user prompt string
    """
    
    # Format domain info
    domain_text = f"""
Domain Information:
- Domain Name: {domain_info.get('business_domain_name', 'N/A')}
- Domain Description: {domain_info.get('business_domain_info', 'N/A')}
- Optimization Problems: {json.dumps(domain_info.get('business_optimization_problems', {}), indent=2)}
"""
    
    # Format use case info
    usecase_text = f"""
Use Case Information:
{json.dumps(usecase_info, indent=2)}
"""
    
    # Format ML approach
    ml_approach_text = f"""
ML Approach:
- Name: {ml_approach.get('name', 'N/A')}
- Description: {ml_approach.get('description', 'N/A')}
- Constraints: {json.dumps(ml_approach.get('constraints', []), indent=2)}
"""
    
    # Format raw requirements
    raw_requirements_text = f"""
Raw Technical Requirements:
{json.dumps(raw_requirements, indent=2)}

Each key in the above dictionary represents a technical parameter that needs to be converted into a user-friendly question.
For each requirement, analyze:
- The technical description
- Data type and constraints
- Default values if provided
- Min/max values if applicable
- Allowed values if it's an enum type
"""
    
    # Format dataset insights
    dataset_text = f"""
Dataset Insights:
- Total Rows: {dataset_insights.get('total_row_count', 'N/A')}
- Column Insights: {json.dumps(dataset_insights.get('column_insights', {}), indent=2)}
"""
    
    # Format column insights
    column_text = f"""
Column-Level Insights:
{json.dumps(column_insights, indent=2)}
"""
    
    # Combine into full prompt
    user_prompt = f"""Convert the following technical ML requirements into user-friendly, domain-aware questions.

{domain_text}

{usecase_text}

{ml_approach_text}

{raw_requirements_text}

{dataset_text}

{column_text}

**Instructions:**
1. For each key in raw_requirements, create a user-friendly question
2. Use domain terminology and context from domain_info and usecase_info
3. Leverage dataset_insights and column_insights to:
   - Suggest appropriate default values
   - Generate relevant options/suggestions
   - Determine reasonable min/max constraints
4. Generate comprehensive validation rules based on requirement metadata
5. Make questions short, simple, and actionable
6. Include helpful examples in help_text

Return ONLY a valid JSON object matching the structure specified in the system prompt."""
    
    return user_prompt

