from fuzzywuzzy import fuzz
from unidecode import unidecode

# Test strings with and without diacritics
word_with_diacritics = "Șoșoacă"
word_without_diacritics = "sosoaca"

# Remove diacritics from the word with diacritics
word_with_diacritics_normalized = unidecode(word_with_diacritics)
print(word_with_diacritics_normalized)

# Test similarity between the normalized word and the word without diacritics
similarity_score = fuzz.ratio(word_with_diacritics_normalized.lower(), word_without_diacritics.lower())

print(f"Similarity between '{word_with_diacritics}' and '{word_without_diacritics}': {similarity_score}%")

