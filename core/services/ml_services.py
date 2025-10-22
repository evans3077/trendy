import spacy
from textblob import TextBlob

nlp = spacy.load('en_core_web_sm')

def extract_keywords(text):
    doc = nlp(text)
    return list({chunk.text for chunk in doc.noun_chunks})[:5]

def analyze_sentiment(text):
    blob = TextBlob(text)
    return (blob.sentiment.polarity + 1) / 2
