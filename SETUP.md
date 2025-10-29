# GitHub Sentiment Analysis Bot

A bot that analyzes sentiment in non-English code review comments (German & Spanish), translates them to English, and posts sentiment analysis reports on PRs.

## Features

- Detects German and Spanish comments
- Translates comments to English before analysis
- Performs sentiment analysis (positive/negative/neutral)
- Posts sentiment summary as PR comments
- Runs automatically on pull requests

## Setup Instructions

### 1. Prerequisites

- GitHub repository with Actions enabled
- Google Cloud Translation API credentials (for translation)

### 2. Google Cloud Setup

1. Create a Google Cloud project
2. Enable the Translation API
3. Create a service account with Translation API access
4. Download the JSON credentials file

### 3. Add Secrets to GitHub

Go to your repository Settings → Secrets and add:

- `GOOGLE_CLOUD_CREDENTIALS`: Paste the entire JSON content from your Google Cloud credentials file

### 4. Add Files to Your Repository

1. Copy `sentiment_analyzer.py` to your repo root
2. Copy `requirements.txt` to your repo root
3. Copy `.github/workflows/sentiment-analysis.yml` to `.github/workflows/` directory

### 5. Commit and Push

\`\`\`bash
git add sentiment_analyzer.py requirements.txt .github/workflows/sentiment-analysis.yml
git commit -m "Add sentiment analysis bot"
git push
\`\`\`

### 6. Test

Create a pull request with a German or Spanish comment to trigger the bot. It will automatically analyze and post results.

## Supported Languages

- **German** (de)
- **Spanish** (es)

## How It Works

1. Bot triggers on PR creation or review comments
2. Fetches all comments from the PR
3. Detects language (German/Spanish only)
4. Translates to English
5. Analyzes sentiment using TextBlob
6. Posts a summary table with results

## Sentiment Scores

- **Polarity**: -1.0 (negative) to 1.0 (positive)
- **Subjectivity**: 0.0 (objective) to 1.0 (subjective)
- **Classification**: Positive (>0.1), Negative (<-0.1), Neutral (else)

## Example Output

| Original | Language | Sentiment | Polarity |
|----------|----------|-----------|----------|
| Das ist großartig! | German | POSITIVE | 0.8 |
| Esto es malo | Spanish | NEGATIVE | -0.7 |
