# biouniversum

This is BioUniversum, an intuitive dashboard that uses AI summarization to help scientists, mission planners, and researchers quickly explore space biology publications.

## Features

* 1. **Search Articles:** Search publications by title or keyword.
* 2. **Article Access:** View abstracts and full-text links directly from NCBI.
* 3. **AI Summaries:** Quickly understand lengthy articles with automatically generated summaries.
* 4. **Keyword Navigation:** Clickable keywords redirect to related articles for rapid exploration.
* 5. **Find Matching Article:** Jump directly to the most relevant article for your query.
* 6. **Gallery:** View screenshots and visualizations from NASA’s Space Biology experiments.

## Demo

*(Optional: include screenshots or GIFs here to show your dashboard in action.)*

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/biouniversum.git
cd biouniversum
```

2. Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the Flask app:

```bash
python main.py
```

5. Open your browser and go to `http://127.0.0.1:5000/`

---

## Usage

* Type a keyword or topic into the search bar to find relevant articles.
* Click an article to view its abstract, AI summary, keywords, and full-text link.
* Click any keyword to explore related publications instantly.
* Use the “Find Matching Article” feature for a direct recommendation.
* Visit the Gallery page to see example screenshots and visualizations.

---

## Data

* The app uses open-access NASA Space Biology publications in JSON format.
* Each article includes metadata like title, year, PMC ID, abstract, and full text.

---

## Contributing

We welcome contributions! If you’d like to improve the platform, please submit a pull request or open an issue.

---

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.
