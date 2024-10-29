import argparse
import glob
import os
import sys
import spacy
from spacy.matcher import Matcher
import re
from collections import defaultdict
import nltk
nltk.download("wordnet", quiet=True)
from nltk.corpus import wordnet as wn
import pyap

nlp = en_core_web_lg.load()
matcher = Matcher(nlp.vocab)
pattern = [
    {"SHAPE": "ddd"},  # Matches digits like house numbers
    {"IS_ALPHA": True},  # Matches words like "Street" or "Avenue"
    {"IS_ALPHA": True, "OP": "?"},  # Optional type like "St", "Ave"
]
matcher.add("ADDRESS", [pattern])

def redact_names(doc):
    redacted = doc.text
    for ent in reversed(doc.ents):
        if ent.label_ in ["PERSON", "ORG"]:
            redacted = redacted[:ent.start_char] + "█" * (ent.end_char - ent.start_char) + redacted[ent.end_char:]
    return redacted

def redact_dates(doc):
    redacted = doc.text
    for ent in reversed(doc.ents):
        if ent.label_ in ["DATE", "TIME"]:
            redacted = redacted[:ent.start_char] + "█" * (ent.end_char - ent.start_char) + redacted[ent.end_char:]
    return redacted
def redact_phones(text):
    phone_pattern = r'\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b'
    return re.sub(phone_pattern, lambda m: "█" * len(m.group()), text)



def redact_addresses(doc, text):
    redacted = text
    

    street_address_ =(
    r"((?:[A-Z\s]+[\n]*){1,2})?"
    r"(\d{1,4} [A-Z\s]{1,40})\n"
    r"([A-Z\s]+,\s*[A-Z]{2})\s*\d{5}"
)
    street_address = re.findall(street_address_, text, re.IGNORECASE)
    for address in street_address:
        full_address = ' '.join(part for part in address if part).strip()
        redacted = redacted.replace(full_address, len(full_address) * "█")
    
    addresses = pyap.parse(text, country='US')

    for address in addresses:
        redacted = redacted.replace(address.full_address, len(address.full_address) * "█")

    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC", "FAC"]:
            redacted = redacted.replace(ent.text, len(ent.text)*"█")
    return redacted
def get_synonyms(concept):
    synonyms = set()
    for syn in wn.synsets(concept):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

def redact_concept(doc, concept):
    synonyms = get_synonyms(concept)
    synonym_docs = [nlp(syn) for syn in synonyms]
    redacted = doc.text
    redacted_sentences = []
    print(nlp("visited").similarity(nlp("visit")))
    for sent in doc.sents:
        redact_sentence = False
        for token in sent:
            print(token)
            for synonym_doc in synonym_docs:
                if token.similarity(synonym_doc) >= 0.65:
                    print(synonym_doc.text)
                    redact_sentence = True
                    break
            if redact_sentence:
                break

        if redact_sentence:
            redacted = redacted.replace(sent.text, "█" * len(sent.text))
            redacted_sentences.append(sent.text)

    return redacted, len(redacted_sentences)

def redact_file(input_file, output_dir, flags, concept):
    with open(input_file, 'r') as f:
        text = f.read()
    
    doc = nlp(text)
    redacted = text
    stats = defaultdict(int)
    
    if 'names' in flags:
        redacted = redact_names(nlp(redacted))
        stats['names'] = len([ent for ent in doc.ents if ent.label_ in ["PERSON", "ORG"]])
    
    if 'dates' in flags:
        redacted = redact_dates(nlp(redacted))
        stats['dates'] = len([ent for ent in doc.ents if ent.label_ in ["DATE", "TIME"]])
    
    if 'phones' in flags:
        redacted = redact_phones(redacted)
        stats['phones'] = len(re.findall(r'\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b', text))
    
    if 'address' in flags:
        redacted = redact_addresses(nlp(redacted), redacted)
        stats['addresses'] = len([ent for ent in doc.ents if ent.label_ in ["GPE", "LOC"]])
    
    if concept:
        redacted, length = redact_concept(nlp(redacted), concept)
        stats['concept'] = length

    output_file = os.path.join(output_dir, os.path.basename(input_file) + '.censored')
    with open(output_file, 'w') as f:
        f.write(redacted)
    
    return stats

def main():
    parser = argparse.ArgumentParser(description="Redact sensitive information from text files.")
    parser.add_argument("--input", required=True, help="Input file pattern (e.g., '*.txt')")
    parser.add_argument("--names", action="store_true", help="Redact names")
    parser.add_argument("--dates", action="store_true", help="Redact dates")
    parser.add_argument("--phones", action="store_true", help="Redact phone numbers")
    parser.add_argument("--address", action="store_true", help="Redact addresses")
    parser.add_argument("--concept", help="Redact sentences containing this concept")
    parser.add_argument("--output", required=True, help="Output directory for redacted files")
    parser.add_argument("--stats", choices=["stderr", "stdout"], help="Where to output statistics")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    flags = [flag for flag in ['names', 'dates', 'phones', 'address'] if getattr(args, flag)]
    input_path = os.path.join(os.getcwd(), "**")   
    total_stats = defaultdict(int)
    print(flags, args.input)
    for input_file in glob.glob(os.path.join(input_path, args.input), recursive=True):
        print(input_file)
        file_stats = redact_file(input_file, args.output, flags, args.concept)
        for key, value in file_stats.items():
            total_stats[key] += value
    
    stats_output = f"Redaction statistics:\n"
    for key, value in total_stats.items():
        stats_output += f"{key.capitalize()}: {value}\n"
    
    if args.stats == "stderr":
        print(stats_output, file=sys.stderr)
    elif args.stats == "stdout":
        print(stats_output)

if __name__ == "__main__":
    main()