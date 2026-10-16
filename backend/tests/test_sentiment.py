import pytest
from app.scoring.sentiment import LocalSentimentAnalyzer

def test_sentiment_analysis_positive():
    analyzer = LocalSentimentAnalyzer()
    res = analyzer.analyze_text("This series is an absolute masterpiece with brilliant stellar cinematography!")
    assert res["positive"] > res["negative"]
    assert res["compound"] > 0.0

def test_sentiment_analysis_negative():
    analyzer = LocalSentimentAnalyzer()
    res = analyzer.analyze_text("Terrible awful film with dull slow pacing and unwatchable plot-holes.")
    assert res["negative"] > res["positive"]
    assert res["compound"] < 0.0

def test_sentiment_analysis_negation():
    analyzer = LocalSentimentAnalyzer()
    res = analyzer.analyze_text("The movie was not amazing, it was really bad.")
    assert res["negative"] > 0
