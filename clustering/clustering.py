"""
Author: Anshul Pardhi
"""
import json
import time
import fastcluster
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import ward, dendrogram

start_time = time.time()

# Open SOLR Index JSON file (Get your SOLR response JSON file here, file too large to upload to GitHub)
f = open('d:/Lectures/Spring 2024/IR/Australia-IR/solr_docs_for_clustering.json', encoding="ISO-8859-1")
data = json.load(f)
f.close()

document_list = []
url_list = []

# Parse text content from indexed json
for outer_index in data:
    if outer_index == "response":
        response_val = data[outer_index]
        for curr_key in response_val:
            if curr_key == "docs":
                site_info = response_val[curr_key]
                for site_dict in site_info:
                    for site_key in site_dict:
                        if site_key == "url":
                            url_list.append(site_dict[site_key])
                        if site_key == "content":
                            content = site_dict[site_key]
                            document_list.append(content)
print("Time taken for parsing JSON: ", time.time() - start_time)

# Use TF-IDF Vectorizer to vectorize document text inputs
vectorizer = TfidfVectorizer(max_df=0.6, min_df=0.1, stop_words='english', use_idf=True)
X = vectorizer.fit_transform(document_list)
print("Time taken for vectorizing inputs: ", time.time() - start_time)

# Apply flat clustering (K-means)
km = KMeans(n_clusters=11, init='k-means++', max_iter=100, n_init=1)
km.fit(X)
# print("Time taken for applying flat clustering: ", time.time() - start_time)

# Store K-means clustering results in a file
id_series = pd.Series(url_list)
cluster_series = pd.Series(km.labels_)
results = (pd.concat([id_series,cluster_series], axis=1))
results.columns = ['id', 'cluster']
results.to_csv("clustering_f.txt", sep=',', columns=['id', 'cluster'], header=False, index=False, encoding='utf-8')
print("Time taken for storing results of flat clustering: ", time.time() - start_time)

# Apply Hierarchical Clustering (Single link)
# Compute distance
dist = 1 - cosine_similarity(X)
print("Time taken for computing cosine similarity: ", time.time() - start_time)

# Apply hierarchical clustering
agg_d = fastcluster.linkage(dist, method='single')
print("Time taken for single linkage: ", time.time() - start_time)

# Draw dendrogram
fig, ax = plt.subplots()
ddata = dendrogram(agg_d, orientation="right", labels=url_list)
plt.tight_layout()
plt.savefig("dendrogram.png")  # optional: save it to a file
print("Time taken for applying hierarchical clustering: ", time.time() - start_time)

# Get labels for each URL
hc_key = ddata["ivl"]
hc_dict = {y: x+1 for x, y in enumerate(sorted(set(ddata["color_list"])))}
hc_value = [hc_dict[x] for x in ddata["color_list"]]

# Save results
hc_cluster_series = pd.Series(hc_value)
hc_id_series = pd.Series(hc_key)
hc_results = pd.concat([hc_id_series, hc_cluster_series], axis=1)
hc_results.columns = ['id', 'cluster']
hc_results.to_csv("clustering_h8.txt", sep=',', header=False, index=False, encoding='utf-8')