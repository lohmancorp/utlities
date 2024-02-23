import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
import heapq

# Reading text from a file
with open('test-text.txt', 'r') as file:
    text = file.read()

stopWords = set(stopwords.words("english"))
words = word_tokenize(text)

# Creating a frequency table to keep the score of each word
freqTable = dict()
for word in words:
    word = word.lower()
    if word in stopWords:
        continue
    if word in freqTable:
        freqTable[word] += 1
    else:
        freqTable[word] = 1

# Creating a dictionary to keep the score of each sentence
sentences = sent_tokenize(text)
sentenceValue = dict()

for sentence in sentences:
    for word, freq in freqTable.items():
        if word in sentence.lower():
            if sentence in sentenceValue:
                sentenceValue[sentence] += freq
            else:
                sentenceValue[sentence] = freq

sumValues = 0
for sentence in sentenceValue:
    sumValues += sentenceValue[sentence]

# Average value of a sentence from the original text
average = int(sumValues / len(sentenceValue))

# Selecting top N sentences for the summary
n = 3  # Adjust N based on your preference
top_sentences = heapq.nlargest(n, sentenceValue, key=sentenceValue.get)
summary = ' '.join(top_sentences)

print("Summary:\n", summary)

# Sentiment Analysis
sia = SentimentIntensityAnalyzer()
sentiment_score = sia.polarity_scores(summary)

# Human-readable sentiment summary
if sentiment_score['compound'] >= 0.05:
    sentiment_summary = "Overall, the sentiment is Positive."
elif sentiment_score['compound'] <= -0.05:
    sentiment_summary = "Overall, the sentiment is Negative."
else:
    sentiment_summary = "Overall, the sentiment is Neutral."

print("\nSentiment Score:", sentiment_score)
print(sentiment_summary)

# Categorizing sentences based on their individual sentiment
positive_sentences = []
neutral_sentences = []
negative_sentences = []

for sentence in sentences:
    sentence_score = sia.polarity_scores(sentence)['compound']
    if sentence_score >= 0.05:
        positive_sentences.append(sentence)
    elif sentence_score <= -0.05:
        negative_sentences.append(sentence)
    else:
        neutral_sentences.append(sentence)

# Output categorized sentences
print("\nPositive Sentences:")
for sentence in positive_sentences:
    print("- ", sentence)

print("\nNeutral Sentences:")
for sentence in neutral_sentences:
    print("- ", sentence)

print("\nNegative Sentences:")
for sentence in negative_sentences:
    print("- ", sentence)
