import nltk
from collections import Counter
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def analyze_text(text):
    """
    Analyze text for word frequency and bigram frequency
    Returns a tuple of (word_freq_dict, bigram_freq_dict)
    """
    if not text:
        return {}, {}
    
    # Clean and tokenize text
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove punctuation
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    # Word frequency analysis
    word_freq = Counter(filtered_tokens)
    
    # Bigram frequency analysis
    bigrams = []
    for i in range(len(filtered_tokens) - 1):
        bigram = f"{filtered_tokens[i]} {filtered_tokens[i + 1]}"
        bigrams.append(bigram)
    
    bigram_freq = Counter(bigrams)
    
    # Convert to regular dictionaries and get top 20 for each
    word_freq_dict = dict(word_freq.most_common(20))
    bigram_freq_dict = dict(bigram_freq.most_common(20))
    
    return word_freq_dict, bigram_freq_dict
