# Import required modules
import json
import requests
import pandas as pd
import xml.etree.ElementTree as ET

chunk_size = 10

# Read the CSV file containing our links to the articles
df = pd.read_csv("SB_publication_PMC.csv")
links = df["Link"].tolist()  # Extract the links to the articles
titles = df["Title"].tolist()  # Extract the titles of all articles

chunked_links = [links[i:i+chunk_size] for i in range(0, len(links), chunk_size)]  # Split links into chunks

def pmc_to_pmid(pmc_ids):
    lost = []
    ids = []
    for pmc in pmc_ids:
        url = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        parameters = {
            'db': 'pmc',
            'id': pmc,
            'rettype': 'medline',
            'retmode': 'xml'
        }

        try:
            response = requests.get(url, params=parameters)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            
            pmid_elem = root.find('.//PMID')
            if pmid_elem is not None:
                ids.append(pmid_elem.text)
            else:
                lost.append(pmc)
        except (requests.RequestException, ET.ParseError):
            print(f"Error fetching PMID for {pmc}")
            lost.append(pmc)
    return ids

def get_article(pmcs, idx):
    try:
        response = requests.get(f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{','.join(pmcs)}/unicode")
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except (requests.RequestException, ET.ParseError):
        print(f"Could not fetch {pmcs}, trying fallback")
        pmid = pmc_to_pmid([pmc.replace('PMC','') for pmc in pmcs])
        if pmid:
            try:
                response = requests.get(f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pubmed.cgi/bioc_xml/{','.join(pmid)}/unicode")
                response.raise_for_status()
                root = ET.fromstring(response.content)
            except (requests.RequestException, ET.ParseError):
                print(f"Fallback failed for {pmid}")
                return None
        else:
            print(f"No PMIDs found for {pmcs}")
            return None

    articles_data = []

    for doc in root.findall(".//document"):
        article_data = {
            "id": None,
            "title": None,
            "year": None,
            "pmid": None,
            "abstract": "",
            "fulltext": ""
        }
        sections = []
        ac_title = None

        for i, p in enumerate(doc.findall("passage")):
            text = p.findtext("text")
            if text:
                sections.append(text.strip())

            if any(infon.get("key") == "section_type" and infon.text == "ABSTRACT" for infon in p.findall("infon")):
                article_data["abstract"] += f"{p.find('text').text}\n"

            if i == 0:  # Extract metadata only from the first passage
                for infon in p.findall("infon"):
                    key = infon.attrib.get("key", "").lower()
                    value = infon.text.strip() if infon.text else None
                    if key == "alt-title":
                        article_data["title"] = value
                    elif key == "article-id_pmc":
                        article_data["id"] = value
                        ac_title = titles[next((i for i, s in enumerate(links) if article_data["id"] in s), None)]
                    elif key == "year" and value:
                        article_data["year"] = int(value)
                    elif key == "article-id_pmid":
                        article_data["pmid"] = value

            if "PMC" not in article_data["id"]:
                article_data["id"] = "PMC" + article_data["id"] # Add the sign to the PMCID if not present

            if ac_title:
                article_data["title"] = ac_title

        article_data["fulltext"] = "\n\n".join(sections)
        articles_data.append(article_data)

    return articles_data if articles_data else None

# Combine all articles into a single list
all_articles = []

for i, link_batch in enumerate(chunked_links):
    pmcids = [link.rstrip("/").split("/")[-1] for link in link_batch]  # Extract only PMCID
    print(f"Processing {pmcids}")
    articles = get_article(pmcids, i*chunk_size)
    if articles:
        all_articles.extend(articles)

# Save all articles in a single JSON file
with open("all_articles.json", "w", encoding="utf-8") as f:
    json.dump(all_articles, f, indent=2, ensure_ascii=False)

print("All articles saved in all_articles.json")