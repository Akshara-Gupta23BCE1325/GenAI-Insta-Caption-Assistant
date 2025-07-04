from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import json
import spacy
import random

# Load models once
nlp = spacy.load("en_core_web_sm")
bart_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# Creative templates for captions
CAPTION_TEMPLATES = [
    "Living for moments like this {} ✨",
    "Can we talk about how amazing this {} is?",
    "{} but make it aesthetic 🌟",
    "This {} has my whole heart 💖",
    "Found my happy place with this {}",
    "{} and chill 🍃",
    "This {} deserves all the hype!",
    "Sending you good vibes with this {} ✌️",
    "Who else loves {} as much as I do?",
    "This {} hits different 🔥"
]

# Generate creative caption from user text
def caption_from_text(prompt):
    # First get a summary
    summary = bart_pipeline(prompt, max_length=50, min_length=20, do_sample=True)[0]['summary_text']
    
    # Extract main keyword
    keywords = extract_keywords(summary)
    main_keyword = keywords[0] if keywords else "moment"
    
    # Apply creative template
    template = random.choice(CAPTION_TEMPLATES)
    return template.format(main_keyword)

# Generate creative caption from uploaded image
def caption_from_image(image_file):
    image = Image.open(image_file).convert("RGB")
    
    # Generate multiple captions and pick the most interesting one
    inputs = blip_processor(images=image, return_tensors="pt")
    outputs = blip_model.generate(
        **inputs,
        num_return_sequences=3,
        max_length=30,
        num_beams=5,
        temperature=0.7,
        top_k=50,
        top_p=0.9
    )
    
    captions = [blip_processor.decode(output, skip_special_tokens=True) for output in outputs]
    return max(captions, key=lambda x: len(x.split()))  # Pick the most descriptive one

# Extract keywords using spaCy with more sophistication
def extract_keywords(text):
    doc = nlp(text.lower())
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop:
            keywords.append(token.text)
    
    # Also consider noun chunks
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3:  # Avoid long phrases
            keywords.append(chunk.text)
    
    return list(set(keywords))

# Enhanced hashtag suggestion
def suggest_hashtags(caption):
    with open("hashtags.json", "r") as f:
        hashtag_data = json.load(f)
    
    keywords = extract_keywords(caption)
    matched = []
    
    # Get direct matches
    for word in keywords:
        if word in hashtag_data:
            matched += hashtag_data[word]
    
    # Get related matches (check if keyword is contained in other keys)
    for key in hashtag_data:
        if any(word in key for word in keywords):
            matched += hashtag_data[key]
    
    # Add some trending general hashtags
    matched += random.sample(hashtag_data.get("_trending", []), 3)
    
    return list(set(matched))[:30], keywords  # Limit to 30 hashtags