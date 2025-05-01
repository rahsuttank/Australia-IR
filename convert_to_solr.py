import json

# Load the web graph
with open('d:/Lectures/Spring 2024/IR/Australia-IR/checkpoint_5000_webgraph.json', 'r', encoding='utf-8') as infile:
    web_graph = json.load(infile)

solr_docs = []
for url, items in web_graph.items():
    solr_doc = {
        "url": url,
        "outgoing_links": items["links"],
        "title": items["title"],    # Placeholder, fill if you have title data
        "content": items["text"]   # Placeholder, fill if you have content data
    }
    solr_docs.append(solr_doc)

# Save as Solr-compatible JSON
with open('d:/Lectures/Spring 2024/IR/Australia-IR/solr_docs.json', 'w+') as outfile:
    json.dump(solr_docs, outfile, indent=2)

print(f"Converted {len(solr_docs)} documents to solr_docs.json")
