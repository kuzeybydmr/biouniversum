# Generative AI has been used to reformat and refine the code for conciseness and performance

print("BioUniversum - Loading Web Application...")
# Import necessary modules 
from flask import Flask, render_template, request, jsonify, redirect
from collections import OrderedDict
from sklearn.feature_extraction.text import TfidfVectorizer # Module used for showing most related search results
from sklearn.metrics.pairwise import cosine_similarity
from keybert import KeyBERT
import numpy as np
import webbrowser
from threading import Timer
import requests
import json
import os

# Setup for BART, KeyBERT and scikit-learn's TF-IDF vectorizer (The AI solutions we're going to use)
# Used Model: facebook/bart-large-cnn
# Documentation and examples: https://huggingface.co/facebook/bart-large-cnn
model_name="facebook/bart-large-cnn"
os.environ['HF_TOKEN'] = "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"
API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
}
kw_model = KeyBERT()           # This is for extracting keywords from articles
vectorizer = TfidfVectorizer() # Used for related article matching
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

app = Flask(__name__)

# Setup for AI-generated data caching to reduce API calls and power usage
len_history = 10    # Maximum capacity of both summary and keyword caches
recent_sum = OrderedDict() # Holds recent summaries
recent_kws = OrderedDict() # Holds recently generated keywords

#            input,
#            max_length=1024,
#            min_length=30,
#            do_sample=False,
#            top_k=50

# Gallery data
gallery_items = [
    {"file": "images-assets.nasa.gov/image/iss012e15387/iss012e15387~orig.jpg", "desc": "Plants inside the leaf chamber of the LADA green house during Expedition 12"},
    {"file": "images-assets.nasa.gov/image/iss021e016211/iss021e016211~orig.jpg", "desc": "FE-1 Suraev prepares a new version of the BIO-5 Rasteniya-2 Experiment"},
    {"file": "images-assets.nasa.gov/image/iss006e44970/iss006e44970~orig.jpg", "desc": "Water droplet on a leaf on the Russian BIO-5 Rastenya-2 Plant Growth Experiment"},
    {"file": "images-assets.nasa.gov/image/S61-00203/S61-00203~orig.jpg", "desc": 'Chimpanzee "Ham" - Biosensors - Cape'},
    {"file": "images-assets.nasa.gov/image/AFRC2018-0028-15/AFRC2018-0028-15~orig.jpg", "desc": "Armstrong Assists with Performance Testing Bio-Based Synthetic Oils"},
    {"file": "images-assets.nasa.gov/image/iss006e45080/iss006e45080~orig.jpg", "desc": "Close-up view of sprouts on the Russian BIO-5 Rasteniya-2/Lada-2 (Plants-2) Plant Growth Experiment"},
    {"file": "images-assets.nasa.gov/image/iss006e44969/iss006e44969~orig.jpg", "desc": "Close-up view of dwarf peas with red flowers on the Russian Plant Growth Experiment"},
    {"file": "images-assets.nasa.gov/image/61a-18-001a/61a-18-001a~orig.jpg", "desc": "Astronaut Bonnie Dunbar preparing to perform bio-medical test"},
    {"file": "images-assets.nasa.gov/image/iss021e006274/iss021e006274~orig.jpg", "desc": "View of CBEF Space Seed Experiment Hardware"},
    {"file": "images-assets.nasa.gov/image/KSC-20200110-PH-CSH01_0003/KSC-20200110-PH-CSH01_0003~orig.jpg", "desc": "Radiation Tomatoes"},
    {"file": "images-assets.nasa.gov/image/ACD25-0047-007/ACD25-0047-007~orig.jpg", "desc": "Mark Clampin Tours the Bioscience Collaborative Laboratory"}
]

# Load articles from JSON file
with open("all_articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Preprocess articles for a smoother experience on the site
tfidf = vectorizer.fit_transform([item["fulltext"] for item in articles])

# Summarization logic
def summarize(text, chunk_size=500):
    # Split full text into n-word chunks
    chunks = []
    current_chunk = []
    current_length = 0
    for sentence in text.split(". "):
        words = sentence.split()
        if current_length + len(words) <= chunk_size:
            current_chunk.append(sentence)
            current_length += len(words)
        else:
            if current_chunk:
                chunks.append(". ".join(current_chunk))
            current_chunk = [sentence]
            current_length = len(words)
    if current_chunk:
        chunks.append(". ".join(current_chunk))

    # Summarize every chunk with API
    partial_summaries = []
    for chunk in chunks:
        response = query({"inputs": chunk})

        if isinstance(response, str):
            summary = response
        elif isinstance(response, list) and isinstance(response[0], dict) and "summary_text" in response[0]:
            summary = response[0]["summary_text"]
        else:
            continue
        partial_summaries.append(summary)

    # Combine summaries into one
    if len(partial_summaries) > 1:
        combined_text = " ".join(partial_summaries)
        response = query({"inputs": combined_text})

        if isinstance(response, str):
            final_summary = response
        elif isinstance(response, list) and isinstance(response[0], dict) and "summary_text" in response[0]:
            final_summary = response[0]["summary_text"]
        else:
            final_summary = combined_text
        return final_summary

    return partial_summaries[0]

@app.route("/")
def index():
    query = request.args.get("q", "")
    year_filter = request.args.get("year", "")

    results = articles
    if query:
        results = [a for a in results if query.lower() in a["title"].lower()]
    if year_filter:
        results = [a for a in results if str(a.get("year", "")) == year_filter]

    years = sorted({str(a.get("year")) for a in articles if a.get("year")})

    return render_template("index.html", results=results, query=query, years=years, selected_year=year_filter)

@app.route("/article/<string:article_id>")
def article(article_id):
    row = next((a for a in articles if a["id"] == article_id), None)
    if not row:
        return "Article not found", 404

    text = row.get("fulltext", "No full text available")
    abstract = row.get("abstract", "No abstract available")

    return render_template(
        "article.html",
        title=row["title"],
        link=f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id}",
        year=row.get("year"),
        pmid=row.get("pmid"),
        fulltext=text,
        abstract=abstract,
        article_id=article_id
    )

@app.route("/summarize/<string:article_id>")
def summarize_article(article_id):
    if article_id not in recent_sum: # Checks dictionary keys for current article
        row = next((a for a in articles if a["id"] == article_id), None)
        if not row:
            return jsonify({"error": "Article not found"}), 404

        text = row.get("fulltext", "")
        summary = summarize(text)
        recent_sum[article_id] = summary
        if len(recent_sum) > len_history:
            recent_sum.popitem(last=False)
    else:
        summary = recent_sum[article_id]
    return jsonify({"summary": summary})

@app.route("/keywords/<string:article_id>")
def generate_keyword(article_id):
    if article_id not in recent_kws:
        row = next((a for a in articles if a["id"] == article_id), None)
        if not row:
            return jsonify({"error": "error"}), 404

        text = row.get("fulltext", "")
        keywords = [keyw[0] for keyw in kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 1), stop_words=None)]
        recent_kws[article_id] = keywords
        if len(recent_kws) > len_history:
            recent_kws.popitem(last=False)
    else:
        keywords = recent_kws[article_id]
    return jsonify({"keywords": keywords})

@app.route("/about")
def about_us():
    return render_template("about.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html", gallery_items=gallery_items)

@app.route("/bestmatch")
def bestmatch():
    query = request.args.get("q", "")
    best_match = int(np.argmax(cosine_similarity(tfidf, vectorizer.transform([query]))))
    return redirect(f"/article/{articles[best_match]["id"]}")

@app.route("/guide")
def guide():
    return render_template("guide.html")

if __name__ == "__main__":
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")
    
    print("Finished!")
    Timer(1, open_browser).start()

    app.run(debug=True)
