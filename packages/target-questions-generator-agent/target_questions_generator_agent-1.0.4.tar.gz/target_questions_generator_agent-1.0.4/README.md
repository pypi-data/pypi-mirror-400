# Target Questions Generator Agent

An intelligent AI-powered agent for converting technical machine learning requirements into user-friendly, domain-aware questions for interactive interfaces.

## 🚀 Features

- **AI-Powered Question Generation**: Leverages advanced LLM models to convert technical parameters into contextual questions
- **Domain-Aware**: Questions are contextualized using domain knowledge and use case information
- **Dataset-Informed**: Uses dataset insights to generate appropriate defaults and suggestions
- **Comprehensive Validation**: Generates validation rules for each question
- **Multiple Data Sources**: Works with both SQL databases and pandas DataFrames
- **100% LLM-Powered**: All question generation logic is handled by LLM, ensuring dynamic and intelligent conversion

## 📦 Installation

### Prerequisites
- Python 3.11+
- Git
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/stepfnAI/target_questions_generator_agent.git
   cd target_questions_generator_agent/
   git checkout dev
   ```

2. **Set up the virtual environment and install dependencies**
   ```bash
   uv venv --python=3.11 venv
   source venv/bin/activate
   uv pip install -e ".[dev]"
   ```

3. **Clone and install the blueprint dependency**
   ```bash
   cd ..
   git clone https://github.com/stepfnAI/sfn_blueprint.git
   cd sfn_blueprint
   git switch dev
   uv pip install -e .
   cd ../target_questions_generator_agent
   ```

4. **Set up environment variables**
   ```bash
   # Copy the template and fill in your values
   cp env.template .env
   
   # Edit .env file with your actual API key
   # Or set environment variables directly:
   export LLM_PROVIDER="openai"  # Optional (default: openai)
   export LLM_MODEL="gpt-4.1-mini"  # Optional (default: gpt-4.1-mini)
   export LLM_API_KEY="your_llm_api_key"  # REQUIRED
   ```

## 🛠️ Usage

### Basic Usage

```python
from target_questions_generator_agent import TargetQuestionsGeneratorAgent
from target_questions_generator_agent.models import (
    TargetQuestionsGeneratorInput,
    DomainInfo,
    MLApproachInfo,
    DatasetInsights
)

# Initialize agent
agent = TargetQuestionsGeneratorAgent()

# Prepare input data
input_data = TargetQuestionsGeneratorInput(
    domain_info=DomainInfo(
        business_domain_name="E-commerce",
        business_domain_info="Online retail platform"
    ),
    usecase_info={"name": "churn_prediction"},
    ml_approach=MLApproachInfo(name="binary_classification"),
    raw_requirements={
        "max_depth": {
            "type": "integer",
            "description": "Maximum depth of decision tree",
            "default": 10,
            "min": 1,
            "max": 100
        }
    },
    dataset_insights=DatasetInsights(total_row_count=1000),
    dataset_column_insights={}
)

# Generate questions
result = agent.generate_questions(input_data)

# Access generated questions
for question in result.questions:
    print(f"Question: {question.question}")
    print(f"Default: {question.default_value}")
    print(f"Validation: {question.validation}")
```

### Running the Example

```bash
python examples/basic_usage.py
```

## 🧪 Testing

Run the complete test suite:
```bash
pytest tests/ -s
```

Or run individual test files:
```bash
pytest tests/test_agent.py -s
```

## 🏗️ Architecture

The Target Questions Generator Agent is built with a modular architecture:

- **Core Components**:
  - `agent.py`: Main agent class with centralized LLM calls
  - `models.py`: Data models and schemas (Pydantic)
  - `utils.py`: Utility functions for input preparation
  - `constants.py`: Prompt templates and formatting functions
  - `config.py`: Configuration settings

- **Dependencies**:
  - `sfn-blueprint`: Core framework and utilities (centralized LLM handling)
  - `pandas`: Data manipulation
  - `pydantic`: Data validation and models
  - `scikit-learn`: ML utilities

## 📋 Workflow Integration

This agent is part of the ML workflow pipeline:

1. **Methodology Suggestion Agent** → Outputs ML approach + raw technical requirements
2. **Target Question Generator Agent** → Converts requirements to user-friendly questions
3. **Target Prep Agent** → Uses user answers to prepare targets

## 🔧 Configuration

The agent can be configured via environment variables or a config object:

```python
from target_questions_generator_agent.config import TargetQuestionsGeneratorConfig

config = TargetQuestionsGeneratorConfig(
    ai_provider="openai",
    model_name="gpt-4",
    temperature=0.2,
    max_tokens=4000
)

agent = TargetQuestionsGeneratorAgent(config=config)
```

## 📝 Output Format

The agent returns structured questions with:

- **Question text**: User-friendly, domain-aware question
- **UI type**: Input type (currently "text")
- **Options**: Suggested values for help text
- **Default value**: Prefilled default based on dataset/domain
- **Data type**: string, integer, float, boolean, date
- **Validation rules**: min, max, required, pattern, allowed_values
- **Help text**: Contextual help with examples

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built using the `sfn-blueprint` framework
- Follows patterns from `target_synthesis_agent` and other agents in the ecosystem

