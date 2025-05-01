import json

with open('checkpoint_1000_webgraph.json', 'r', encoding='utf-8') as infile:
    web_graph = json.load(infile)

solr_docs = []
for url, data in web_graph.items():
    solr_doc = {
        "url": url,
        "outgoing_links": data.get("links", []),
        "title": data.get("title", ""),
        "content": data.get("content", "")
    }
    solr_docs.append(solr_doc)

with open('solr_docs.json', 'w', encoding='utf-8') as outfile:
    json.dump(solr_docs, outfile, indent=2, ensure_ascii=False)

print(f"Converted {len(solr_docs)} documents to solr_docs.json")
