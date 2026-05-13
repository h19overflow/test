# Risk Auditor: AI-Powered Recruitment Pipeline

An automated, transparent, and bias-aware recruitment pipeline built with **LangGraph**. This system processes candidate resumes against job descriptions, generates structured scoring rubrics, audits for potential bias, and produces comprehensive hiring summaries.

## Overview

The Risk Auditor pipeline automates the complex task of evaluating candidates while maintaining a rigorous audit trail. By using a graph-based orchestration, it ensures each stage—from initial scoring to final bias review—is executed consistently and with full observability.

## Key Features

- **Automated Candidate Scoring**: Leverages LLMs to evaluate resumes against dynamically generated rubrics.
- **Bias Audit Stage**: Explicitly checks scoring patterns for potential gender, racial, or institutional bias before finalization.
- **Artifact Preservation**: Saves full LLM call logs, rubrics, and intermediate scores for compliance and review.
- **Hiring Summaries**: Generates human-readable markdown summaries for recruitment teams.
- **Type-Safe Schemas**: Utilizes Pydantic for robust data validation across the entire pipeline.

## Project Structure

- `src/risk_auditor/`: Core package containing the LangGraph definition and state management.
  - `nodes/`: Functional units of the graph (Scoring, Bias Audit, Summaries, etc.).
  - `schemas.py`: Data models for candidates, rubrics, and audit results.
- `data/`: Input resumes and job description files.
- `docs/`: Technical specifications and architectural documentation.
- `validate.py`: High-level entry point for running and validating the pipeline.

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd Test
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY to .env
   ```

### Usage

Run the full validation and audit pipeline:
```bash
python validate.py
```

Results will be generated in the root directory:
- `candidate_scores.json`: Detailed scoring breakdown.
- `bias_audit.json`: Findings from the fairness audit.
- `hiring_summaries.md`: Final recommendation summaries.
