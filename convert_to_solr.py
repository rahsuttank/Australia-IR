import json

# Load the web graph
with open('australia_web_graph.json', 'r') as infile:
    web_graph = json.load(infile)

solr_docs = []
for url, outgoing_links in web_graph.items():
    solr_doc = {
        "url": url,
        "outgoing_links": outgoing_links,
        "title": "",    # Placeholder, fill if you have title data
        "content": ""   # Placeholder, fill if you have content data
    }
    solr_docs.append(solr_doc)

# Save as Solr-compatible JSON
with open('solr_docs.json', 'w+') as outfile:
    json.dump(solr_docs, outfile, indent=2)

print(f"Converted {len(solr_docs)} documents to solr_docs.json")
