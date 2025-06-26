import nltk
from collections import Counter, defaultdict
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

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
    Only includes words/phrases that appear more than once
    Groups word variations using stemming (work/works/working etc.)
    Returns a tuple of (word_freq_dict, bigram_freq_dict)
    """
    if not text:
        return {}, {}
    
    # Clean and tokenize text
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove punctuation
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords and short words
    stop_words = set(stopwords.words('english'))
    
    # Add common Bible words that aren't meaningful for analysis
    bible_stop_words = {'said', 'say', 'says', 'came', 'come', 'went', 'go', 'one', 'two', 'three', 'shall', 'will', 'let', 'may', 'might', 'would', 'could', 'should'}
    stop_words.update(bible_stop_words)
    
    filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    # Stem words to group variations
    stemmer = PorterStemmer()
    stem_to_words = defaultdict(list)
    
    for word in filtered_tokens:
        stem = stemmer.stem(word)
        stem_to_words[stem].append(word)
    
    # Count occurrences by stem, choose most common form as representative
    stem_counts = {}
    representative_words = {}
    
    for stem, words in stem_to_words.items():
        total_count = len(words)
        if total_count > 1:  # Only include words that appear more than once
            # Choose the most common form of the word as representative
            word_counter = Counter(words)
            most_common_word = word_counter.most_common(1)[0][0]
            stem_counts[stem] = total_count
            representative_words[stem] = most_common_word
    
    # Create word frequency dict using representative words
    word_freq_dict = {}
    for stem, count in Counter(stem_counts).most_common(20):
        word_freq_dict[representative_words[stem]] = count
    
    # Bigram frequency analysis (only bigrams that appear more than once)
    bigrams = []
    for i in range(len(filtered_tokens) - 1):
        bigram = f"{filtered_tokens[i]} {filtered_tokens[i + 1]}"
        bigrams.append(bigram)
    
    bigram_freq = Counter(bigrams)
    # Only include bigrams that appear more than once
    bigram_freq_dict = {bigram: count for bigram, count in bigram_freq.most_common(20) if count > 1}
    
    return word_freq_dict, bigram_freq_dict
