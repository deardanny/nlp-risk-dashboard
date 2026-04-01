# NLP-Powered Risk Management Dashboard

An end-to-end NLP pipeline built at Kimberly-Clark AI Labs (2021–2024) to replace a $420,000/year third-party social listening vendor with an in-house GPT-4 powered system.

## Results
- 60% → 92% classification accuracy (upgraded from RoBERTa to fine-tuned GPT-4)
- 90% reduction in vendor costs
- Adopted by APAC and US teams as a regional standard

## Overview

The pipeline monitors diaper brand mentions across Korean parenting communities and e-commerce review platforms, extracts sentiment and risk signals, and surfaces weekly insights to marketing and sales teams.

## Pipeline Components

| File | Description |
|------|-------------|
| `brand-classification` | Crawls community posts, detects brand mentions via keyword matching, flags leakage and contamination risk signals |
| `trend-analysis` | Extracts trending consumer topics from non-brand posts using GPT-4 keyword extraction |
| `weekly-brand-summary` | Generates weekly GPT-4 summaries of brand-related discussions per brand |
| `internal-review-analysis` | Analyzes internal product reviews: extracts satisfaction/dissatisfaction keywords, generates property scores and summaries, detects risk keywords |
| `competitor-review-analysis` | Same analysis pipeline applied to competitor brand reviews |

Each component has an `_en` version using English-transliterated keywords for readability. The original pipeline ran on Korean community data.

## Tech Stack
- Python, OpenAI GPT-4 API
- Snowflake, Azure Databricks
- Pandas, scikit-learn
- Google Translate API

## Architecture
```
Community Posts (NaverCafe)          E-commerce Reviews (Coupang)
         │                                      │
         ▼                                      ▼
brand-classification.ipynb        internal-review-analysis.ipynb
trend-analysis.ipynb              competitor-review-analysis.ipynb
         │                                      │
         ▼                                      ▼
weekly-brand-summary.ipynb        Property Scores + Risk Flags
         │                                      │
         └──────────────┬───────────────────────┘
                        ▼
                  Snowflake DWH
                        │
                        ▼
                  Power BI Dashboard
```

## Environment Variables

Set the following before running any notebook:
```bash
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_DATABASE=your_database
export SNOWFLAKE_SCHEMA=your_schema
export SNOWFLAKE_WAREHOUSE=your_warehouse
export OPENAI_API_KEY=your_openai_key
```

## Note
All table names, database credentials, and proprietary schema details have been anonymized. Model logic, feature engineering, and pipeline architecture are fully preserved.

## Timeline
Built and maintained at Kimberly-Clark AI Labs, Seoul · 2021–2024
