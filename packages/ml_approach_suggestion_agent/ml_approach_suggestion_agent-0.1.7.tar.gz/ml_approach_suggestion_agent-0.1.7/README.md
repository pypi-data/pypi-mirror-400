# ml_approach_suggestion_agent

An AI-powered agent that analyzes a dataset and use case to recommend the most appropriate machine learning methodology.

## Description

This agent takes a detailed description of a business domain, a specific use case, and information about the dataset—including column descriptions, insights, and target variable details—to suggest the best ML approach. It uses a large language model to:

1.  **Analyze** the relationship between the use case and the target variable.
2.  **Evaluate** the characteristics of the data (especially the target column).
3.  **Recommend** the most suitable methodology from a predefined list: `Classification`, `Regression`, `Forecasting`, `Clustering`, or `No-ML`.
4.  **Provide** a clear justification for its recommendation.

This helps data scientists and analysts quickly and confidently choose the right path for their modeling efforts, saving time and reducing the risk of starting with an incorrect approach.

## Key Features

-   **Intelligent Use Case Analysis**: Leverages an LLM to understand the core objective of the business problem.
-   **Target-Aware Recommendation**: Places special emphasis on the nature of the target variable to guide its decision.
-   **Context-Driven Suggestions**: Considers the entire data context, including domain and column descriptions, to make an informed choice.
-   **Accelerates Model Planning**: Provides a validated starting point for ML projects, ensuring alignment between the problem and the proposed solution.

## Installation

### Prerequisites

-   [**uv**](https://docs.astral.sh/uv/getting-started/installation/) – A fast Python package and environment manager.
    -   For a quick setup on macOS/Linux, you can use:
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
-   [**Git**](https://git-scm.com/)

### Steps

1.  **Clone the `methodology_selection_agent` repository:**
    ```bash
    git clone https://github.com/stepfnAI/ml_approach_suggestion_agent.git
    cd ml_approach_suggestion_agent
    git switch main
    ```

2.  **Create a virtual environment and install dependencies:**
    This command creates a `.venv` folder in the current directory and installs all required packages.
    ```bash
    uv sync --extra dev
    source .venv/bin/activate
    ```

## Configuration

You can configure the agent by creating a `.env` file in the project root or by exporting environment variables in your shell. Settings loaded via `export` will override those in a `.env` file.

### Available Settings

| Environment Variable            | Description                                  | Default  |
| ------------------------------- | -------------------------------------------- | -------- |
| `OPENAI_API_KEY`                | **(Required)** Your OpenAI API key.          | *None*   |
| `METHODOLOGY_AI_PROVIDER`       | AI provider for methodology suggestions.     | `openai` |
| `METHODOLOGY_AI_MODEL`          | AI model for methodology suggestions.        | `gpt-4o` |
| `METHODOLOGY_TEMPERATURE`       | AI model temperature (e.g., `0.0` to `0.5`). | `0.3`    |
| `METHODOLOGY_MAX_TOKENS`        | Maximum tokens for the AI response.          | `4000`   |

---

### Method 1: Using a `.env` File (Recommended)

Create a `.env` file in the root directory to store API keys and project-wide defaults.

#### Example `.env` file:

```dotenv
# .env

# --- Required Settings ---
OPENAI_API_KEY="sk-your-api-key-here"

# --- Optional Overrides ---
# Use a different model
METHODOLOGY_AI_MODEL="gpt-4o-mini"

# Use a lower temperature for more deterministic responses
METHODOLOGY_TEMPERATURE=0.1
```

---

### Method 2: Using `export` Commands

Use `export` in your terminal for temporary settings or in CI/CD environments.

#### Example `export` commands:

```bash
# Set the environment variables for the current terminal session
export OPENAI_API_KEY="sk-your-api-key-here"
export METHODOLOGY_AI_MODEL="gpt-4o-mini"
```

## Testing

To run the test suite, use the following command from the root of the project directory:

```bash
pytest -s
```

## Usage

### Running the Example Script

To see a quick demonstration, run the provided example script. This will execute the agent with pre-defined data and print the recommended methodology.

```bash
python examples/basic_usage.py
```

### Using as a Library

Integrate the `MLApproachDecisionAgent` directly into your Python applications to get methodology recommendations programmatically.

```python
import logging
from ml_approach_suggestion_agent.agent import MLApproachDecisionAgent

# Configure logging
logging.basicConfig(level=logging.INFO)

# 1. Define the domain, use case, and data context
domain_name = "Mortgage Loan Servicing"
domain_description = "Managing mortgage loans from post-origination to payoff, including payment collection, escrow management, and compliance for domestic and international loans."
use_case = "To predict the likelihood of a borrower becoming delinquent on their mortgage payment within the next 60 days using their demographic and financial data to enable proactive intervention."

column_descriptions = {
    "CreditScore": "Borrower's credit score from credit bureau sources",
    "EmploymentStatus": "Current employment status (e.g., employed, self-employed, unemployed)",
    # ... other column descriptions
}

column_insights = {
  "table_info": { "row_count": 50000 },
  "table_columns_info": {
    "CreditScore": { "data_type": "Int64", "min_max_value": [350, 850] },
    "EmploymentStatus": { "data_type": "string", "distinct_count": 5 },
    # ... other column insights
  }
}

target_column_name = "IsDelinquent"
target_column_insights = {
    "Target Column Description": "A binary categorical flag indicating if the borrower has missed one or more mortgage payments in the last 60 days.",
    "Data Type": "Integer (or Boolean)",
    "Value Distribution": {
      "0 (Not Delinquent)": "92%",
      "1 (Delinquent)": "8%"
    }
}

# 2. Prepare the task data payload
task_data = {
    "domain_name": domain_name,
    "domain_description": domain_description,
    "use_case": use_case,
    "column_descriptions": column_descriptions,
    "column_insights": column_insights,
    "target_column_name": target_column_name,
    "target_column_insights": target_column_insights
}

# 3. Initialize and execute the agent
agent = MLApproachDecisionAgent()
result = agent(task_data)

# 4. Print the suggested methodology
if result["success"]:
    print("Successfully suggested an approach:")
    print(result["result"]["approach"].model_dump_json(indent=4))
    print(f"Cost summary: {result['result']['cost_summary']}")
else:
    print("Failed to suggest an approach.")

```

### Example Output

The agent returns a JSON object containing the recommended methodology and a detailed explanation for the choice.

*(Note: The actual output may vary slightly based on the LLM's response.)*

```json
{
    "recommended": "Classification",
    "description": "The goal is to predict the likelihood of a borrower becoming delinquent on their mortgage payment within the next 60 days. This is a binary outcome (delinquent or not delinquent), making classification the appropriate methodology. The target variable is categorical, and the available demographic and financial data can be used as features to train a classification model."
}
```
