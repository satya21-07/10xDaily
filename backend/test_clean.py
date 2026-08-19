import re

text1 = "Vishnu (; Sanskrit: विष्णु, lit. 'All Pervasive', IAST: Viṣṇu, pronounced [ʋɪʂɳʊ]), also known as Narayana and Hari, is one of the principal deities of Hinduism."
text2 = "Shiva (Sanskrit: शिव, lit. 'The Auspicious One', IAST: Śiva, pronounced [ɕɪʋɐ]), also known as Mahadeva..."
text3 = "Brahma (; Sanskrit: ब्रह्मा, IAST: Brahmā) is a Hindu god..."

def clean_intro(text):
    # Remove parenthesis containing linguistic or phonetic metadata
    cleaned = re.sub(r'\s*\([^)]*(?:Sanskrit:|IAST:|pronounced|lit\.|also spelled)[^)]*\)', '', text)
    # Remove any standalone bracketed pronunciation guides
    cleaned = re.sub(r'\s*\[[^\]]+\]', '', cleaned)
    # Remove empty parenthesis (that might be left if we had multiple or something)
    cleaned = re.sub(r'\s*\(\s*[;,\s]*\)', '', cleaned)
    # Clean up double commas
    cleaned = re.sub(r',\s*,', ',', cleaned)
    # Fix space before comma
    cleaned = re.sub(r'\s+,', ',', cleaned)
    # Fix comma after period if it happens
    cleaned = re.sub(r'\.\s*,', '.', cleaned)
    return cleaned

print(clean_intro(text1))
print(clean_intro(text2))
print(clean_intro(text3))
