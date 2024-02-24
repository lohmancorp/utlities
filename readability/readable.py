import sys
import requests
from bs4 import BeautifulSoup
import textstat
import requests.packages.urllib3
import os
import certifi
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, regexp_tokenize
from nltk.corpus import stopwords
import re  # Regular expressions for text cleaning
from collections import Counter

# Set SSL_CERT_FILE environment variable
os.environ['SSL_CERT_FILE'] = certifi.where()

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('cmudict', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
from nltk.corpus import cmudict
from nltk.corpus import wordnet as wn
syllable_dict = cmudict.dict()

def count_syllables(word):
    """Return the number of syllables in a word."""
    word = word.lower()
    if word in syllable_dict:
        return max([len(list(y for y in x if y[-1].isdigit())) for x in syllable_dict[word]])
    else:
        return textstat.syllable_count(word)

def scrape_text_from_url(url):
    """Scrape the text content from the given URL, skipping SSL certificate verification."""
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script, style, and other non-relevant tags
        for script_or_style in soup(["script", "style", "noscript", "iframe", "footer", "header", "nav"]):
            script_or_style.decompose()
        
        text = ' '.join(soup.stripped_strings)
        return clean_text(text)  # Clean the text to remove non-relevant patterns
    except Exception as e:
        print(f"Error fetching URL content: {e}")
        sys.exit(1)

def clean_text(text):
    """Remove URLs, script snippets, and other non-readable patterns."""
    text = re.sub(r'https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'<!--.*?-->|<[^>]+>', '', text, flags=re.DOTALL)  # Remove comments and tags
    return text

def find_alternate_words(word):
    """Find simpler synonyms for a complex word using WordNet."""
    synonyms = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonym = lemma.name().replace('_', ' ')
            if synonym.lower() != word.lower():
                synonyms.add(synonym)
    return list(synonyms)[:3]  # Return up to 3 synonyms

def analyze_technical_terms(text):
    """Analyze the text for technical terms based on frequency."""
    stop_words = set(stopwords.words('english'))
    words = regexp_tokenize(text.lower(), pattern=r"\s|[\.,;'\-!\(\)\[\]{}]", gaps=True)  # Improved tokenization
    words = [word for word in words if word.isalpha() and word not in stop_words]
    
    freq_table = Counter(words)
    technical_terms = {word for word, count in freq_table.items() if count > 1}  # Example criterion
    
    return technical_terms

def calculate_readability_scores(text):
    scores = {
        'Flesch Reading Ease': textstat.flesch_reading_ease(text),
        'Flesch-Kincaid Grade Level': textstat.flesch_kincaid_grade(text),
        'Gunning Fog Index': textstat.gunning_fog(text),
        'SMOG Index': textstat.smog_index(text),
        'Coleman-Liau Index': textstat.coleman_liau_index(text),
        'Automated Readability Index (ARI)': textstat.automated_readability_index(text),
        'Dale-Chall Readability Score': textstat.dale_chall_readability_score(text),
        'LIX': textstat.lix(text),
        'FORCAST (Estimated Grade Level)': textstat.text_standard(text, float_output=True)
    }
    return scores

def print_scores_with_explanations(scores, technical_terms, text):
    # Calculate technical terms density
    total_words = len(word_tokenize(text))
    technical_words_count = sum(word in technical_terms for word in word_tokenize(text.lower()))
    technical_density = technical_words_count / total_words if total_words > 0 else 0

    # Define adjusted outcomes based on technical density
    def adjust_outcome(outcome):
        if technical_density > 0.2:  # Example threshold, adjust based on analysis
            if outcome == "Too Difficult":
                return "Needs work"
            elif outcome == "Needs work":
                return "Positive"
        return outcome

    outcomes = {
        'Flesch Reading Ease': lambda x: adjust_outcome("Positive" if x >= 60 else "Needs work" if 40 <= x <= 49 else "Too Difficult"),
        'Flesch-Kincaid Grade Level': lambda x: adjust_outcome("Positive" if x <= 10 else "Needs work" if 11 <= x <= 12 else "Too Difficult"),
        'Gunning Fog Index': lambda x: adjust_outcome("Positive" if x <= 11 else "Needs work" if 12 <= x <= 13 else "Too Difficult"),
        'SMOG Index': lambda x: adjust_outcome("Positive" if x <= 11 else "Needs work" if 12 <= x <= 13 else "Too Difficult"),
        'Coleman-Liau Index': lambda x: adjust_outcome("Positive" if x <= 11 else "Needs work" if 12 <= x <= 13 else "Too Difficult"),
        'Automated Readability Index (ARI)': lambda x: adjust_outcome("Positive" if x <= 11 else "Needs work" if 12 <= x <= 13 else "Too Difficult"),
        'Dale-Chall Readability Score': lambda x: adjust_outcome("Positive" if x <= 8 else "Needs work" if 8.0 < x <= 8.9 else "Too Difficult"),
        'LIX': lambda x: adjust_outcome("Positive" if x <= 40 else "Needs work" if 41 <= x <= 59 else "Too Difficult"),
        'FORCAST (Estimated Grade Level)': lambda x: adjust_outcome("Positive" if x <= 11 else "Needs work" if 12 <= x <= 13 else "Too Difficult"),
    }

    print("\nReadability Scores and Interpretations:\n")
    for score_name, score_value in scores.items():
        outcome = outcomes[score_name](score_value)
        print(f"{score_name}: {score_value} ({outcome})")

    print(f"\nTechnical Term Density: {technical_density:.2%}")
    print(f"Identified technical terms: {', '.join(sorted(technical_terms))}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    text = scrape_text_from_url(url)
    technical_terms = analyze_technical_terms(text)
    scores = calculate_readability_scores(text)

    # Adjust the print function call to include technical_terms and text
    print_scores_with_explanations(scores, technical_terms, text)
