import json
import hashlib

# Load the web graph
with open('d:/Lectures/Spring 2024/IR/Australia-IR/checkpoint_1000_webgraph.json', 'r', encoding='utf-8') as infile:
    web_graph = json.load(infile)

solr_docs = []
for url, items in web_graph.items():
    content = items.get("text", "")  # Ensure there's content to hash
    digest = hashlib.sha256(content.encode('utf-8')).hexdigest()

    solr_doc = {
        "url": url,
        "outgoing_links": items.get("links", []),
        "title": items.get("title", ""),     # Optional title
        "content": content,
        "digest": digest                     # Added digest
    }
    solr_docs.append(solr_doc)

# Save as Solr-compatible JSON
with open('d:/Lectures/Spring 2024/IR/Australia-IR/solr_docs_with_digest.json', 'w+', encoding='utf-8') as outfile:
    json.dump(solr_docs, outfile, indent=2, ensure_ascii=False)

print(f"Converted {len(solr_docs)} documents to solr_docs_with_digest.json with digest included.")
