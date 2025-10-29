import os
import json
from typing import Optional
import requests
from textblob import TextBlob
from langdetect import detect, LangDetectException
from google.cloud import translate_v2

# Initialize Google Translate client
translate_client = translate_v2.Client()

# Supported languages: German (de) and Spanish (es)
SUPPORTED_LANGUAGES = ['de', 'es']

class SentimentAnalyzer:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect language of the text"""
        try:
            lang = detect(text)
            return lang if lang in SUPPORTED_LANGUAGES else None
        except LangDetectException:
            return None
    
    def translate_to_english(self, text: str, source_language: str) -> str:
        """Translate text to English using Google Translate"""
        try:
            result = translate_client.translate_text(
                text,
                source_language=source_language,
                target_language='en'
            )
            return result['translatedText']
        except Exception as e:
            print(f"[v0] Translation error: {e}")
            return text
    
    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of text using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            'sentiment': sentiment,
            'polarity': round(polarity, 2),
            'subjectivity': round(blob.sentiment.subjectivity, 2)
        }
    
    def process_comment(self, comment_text: str) -> Optional[dict]:
        """Process a single comment: detect language, translate, analyze sentiment"""
        # Detect language
        lang = self.detect_language(comment_text)
        if not lang:
            return None
        
        print(f"[v0] Detected language: {lang}")
        
        # Translate to English
        translated_text = self.translate_to_english(comment_text, lang)
        print(f"[v0] Translated text: {translated_text}")
        
        # Analyze sentiment
        sentiment_result = self.analyze_sentiment(translated_text)
        
        return {
            'original_text': comment_text,
            'detected_language': lang,
            'translated_text': translated_text,
            'sentiment_analysis': sentiment_result
        }
    
    def get_pr_comments(self, repo: str, pr_number: int) -> list:
        """Fetch all review comments from a PR"""
        url = f'https://api.github.com/repos/{repo}/pulls/{pr_number}/comments'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[v0] Error fetching comments: {response.status_code}")
            return []
    
    def post_sentiment_comment(self, repo: str, pr_number: int, analysis_results: list):
        """Post sentiment analysis summary as a comment on the PR"""
        if not analysis_results:
            return
        
        # Build comment body
        comment_body = "## Sentiment Analysis Report\n\n"
        comment_body += "| Original | Language | Sentiment | Polarity |\n"
        comment_body += "|----------|----------|-----------|----------|\n"
        
        for result in analysis_results:
            original = result['original_text'][:50] + "..." if len(result['original_text']) > 50 else result['original_text']
            lang_name = "German" if result['detected_language'] == 'de' else "Spanish"
            sentiment = result['sentiment_analysis']['sentiment'].upper()
            polarity = result['sentiment_analysis']['polarity']
            
            comment_body += f"| {original} | {lang_name} | {sentiment} | {polarity} |\n"
        
        # Post comment
        url = f'https://api.github.com/repos/{repo}/issues/{pr_number}/comments'
        payload = {'body': comment_body}
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 201:
            print(f"[v0] Comment posted successfully")
        else:
            print(f"[v0] Error posting comment: {response.status_code}")

def main():
    """Main function to run sentiment analysis on PR comments"""
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    github_repository = os.getenv('GITHUB_REPOSITORY')
    github_event_path = os.getenv('GITHUB_EVENT_PATH')
    
    if not all([github_token, github_repository, github_event_path]):
        print("[v0] Missing required environment variables")
        return
    
    # Parse GitHub event
    with open(github_event_path, 'r') as f:
        event = json.load(f)
    
    pr_number = event.get('pull_request', {}).get('number')
    if not pr_number:
        print("[v0] No PR number found in event")
        return
    
    print(f"[v0] Processing PR #{pr_number} in {github_repository}")
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer(github_token)
    
    # Get PR comments
    comments = analyzer.get_pr_comments(github_repository, pr_number)
    print(f"[v0] Found {len(comments)} comments")
    
    # Analyze comments
    analysis_results = []
    for comment in comments:
        result = analyzer.process_comment(comment['body'])
        if result:
            analysis_results.append(result)
            print(f"[v0] Analyzed: {result['sentiment_analysis']['sentiment']}")
    
    # Post summary comment
    if analysis_results:
        analyzer.post_sentiment_comment(github_repository, pr_number, analysis_results)
    else:
        print("[v0] No non-English comments found to analyze")

if __name__ == '__main__':
    main()
