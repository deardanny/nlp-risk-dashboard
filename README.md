# NLP-Powered Risk Management Dashboard

An in-house NLP and LLM platform developed at Kimberly-Clark (Yuhan-Kimberly) AI Labs (2021–2024) to turn consumer feedback into product insights and earlier quality-risk signals.

[Case study and dashboard demo](https://hdjang.com/projects/risk/)

## Results reported in the project poster

| Measure | Reported result |
| --- | --- |
| Product-attribute and sentiment classification accuracy | Vendor **60%** → RoBERTa **80%** → GPT-4o **90%** |
| Annual external spend | Approximately **US$500,000 → US$33,000**, or **93% lower** |
| Issue-response cycle through completed factory correction | Approximately **90 days → 3 days** |

Led implementation, training, maintenance, and ad hoc analysis. Presented the platform to US/APAC leadership for planned expansion.

These are project-reported results from *Consumer Insights & Risk Management: From Consumer Reviews to Business Insights and Faster Action*, by Daniel (Heedong) Jang. The poster cites presenter records and the dashboard guide (2024). Annual external spend compares historical vendor-platform fees with estimated crawling costs on the same USD basis; it excludes internal labor and cloud costs. The 90-to-3-day measure covers the issue-response cycle through completed factory correction, not model inference time. The figures describe the project evaluation; the public notebooks do not include the original evaluation data.

## Overview

The pipeline monitors diaper brand mentions across Korean parenting communities and e-commerce review platforms, extracts sentiment and risk signals, and surfaces weekly insights to marketing and sales teams.

## Pipeline Components

| Notebook | English version | Description |
|---|---|---|
| [brand-classification](brand-classification.ipynb) | [English](brand-classification_en.ipynb) | Reads collected community posts from Snowflake, detects brand mentions via keyword matching, flags leakage and contamination risk signals |
| [trend-analysis](trend-analysis.ipynb) | [English](trend-analysis_en.ipynb) | Extracts trending consumer topics from non-brand posts using GPT-4 keyword extraction |
| [weekly-brand-summary](weekly-brand-summary.ipynb) | [English](weekly-brand-summary_en.ipynb) | Generates weekly GPT-4 summaries of brand-related discussions per brand |
| [internal-review-analysis](internal-review-analysis.ipynb) | [English](internal-review-analysis_en.ipynb.ipynb) | Analyzes internal product reviews: extracts satisfaction/dissatisfaction keywords, generates property scores and summaries, detects risk keywords |
| [competitor-review-analysis](competitor-review-analysis.ipynb) | [English](competitor-review-analysis_en.ipynb) | Same analysis pipeline applied to competitor brand reviews |

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
