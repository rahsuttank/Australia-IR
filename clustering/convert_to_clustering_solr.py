import json

# Path to your original JSON file
input_file = 'd:/Lectures/Spring 2024/IR/Australia-IR/solr_docs.json'

# Path to save Solr-style file
output_file = 'd:/Lectures/Spring 2024/IR/Australia-IR/solr_docs_for_clustering.json'

# Load original file
with open(input_file, 'r', encoding='utf-8') as f:
    original_docs = json.load(f)

# Extract only the fields required by the clustering script
solr_docs = []
for doc in original_docs:
    if 'url' in doc and 'content' in doc:
        solr_docs.append({
            'url': doc['url'],
            'content': doc['content']
        })

# Wrap in Solr-style format
solr_format = {
    'response': {
        'docs': solr_docs
    }
}

# Save to output
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(solr_format, f, indent=2)

print(f"Converted {len(solr_docs)} documents to Solr format and saved to {output_file}")