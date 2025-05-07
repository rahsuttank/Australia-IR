import os
import socket
import flask # type: ignore
from flask_cors import CORS # type: ignore
import pysolr # type: ignore
import re
from flask import request, jsonify
import json
from query_expansion.Association_Cluster import association_main
from query_expansion.Metric_Clusters import metric_cluster_main
from spellchecker import SpellChecker
from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer('all-MiniLM-L6-v2')
doc_vectors = {}

spell = SpellChecker()

# currently used Solr core 
CURRENT_CORE = "australia/"
# Create a client instance. The timeout and authentication options are not required.
solr = pysolr.Solr('http://localhost:8983/solr/' + CURRENT_CORE, always_commit=True, timeout=10)

app = flask.Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
app.config["DEBUG"] = True


@app.route('/api/v1/indexer', methods=['GET'])
def get_query():
    if 'query' in request.args and 'type' in request.args:
        query = str(request.args['query'])
        print(query)
        type =  str(request.args['type'])
        total_results = 50
        if type == "association_qe" or type == "metric_qe" or type == "scalar_qe":
            total_results = 50

        solr_results = get_results_from_solr(query, total_results)
        api_resp = parse_solr_results(solr_results)
        if type == "page_rank":
            result = api_resp
        elif "clustering" in type:
            result = get_clustering_results(api_resp, type)
        elif type == "hits":
            result = get_hits_results(api_resp)
        elif type == "association_qe":
            # query = spell.correction(query)
            # print(query)
            expanded_query = association_main(query, solr_results)
            expanded_query = 'url:' + expanded_query
            solr_res_after_qe = get_results_from_solr(expanded_query, 20)
            api_resp = parse_solr_results(solr_res_after_qe)
            result = api_resp
        elif type == "metric_qe":
            # query = spell.correction(query)
            expanded_query = metric_cluster_main(query, solr_results)
            expanded_query = 'url:' + expanded_query
            solr_res_after_qe = get_results_from_solr(expanded_query, 20)
            api_resp = parse_solr_results(solr_res_after_qe)
            result = api_resp
        elif type == "scalar_qe":
            # query = spell.correction(query)
            expanded_query = association_main(query, solr_results)
            expanded_query = 'url:' + expanded_query
            solr_res_after_qe = get_results_from_solr(expanded_query, 20)
            api_resp = parse_solr_results(solr_res_after_qe)
            result = api_resp

        return jsonify(result)
    else:
        return "Error: No query or type provided"


# def get_results_from_solr(query, no_of_results):
#     results = solr.search(query, search_handler="/select", **{
#         "wt": "json",
#         "rows": no_of_results
#     })
#     return results

def get_results_from_solr(query, no_of_results):
    return solr.search(query, search_handler="/select", **{
        "defType": "edismax", 
        "qf": "title^2 content^ url",
        "pf": "title^2 content^5",
        "qs": 4,
        "mm": "1<60%",  # allow some flexibility
        "rows": no_of_results,
        "wt": "json",
        "fl": "*,score"
    })
    # query_vector = model.encode(query, convert_to_tensor=True)

    # for result in solr_results:
    #     content = result.get('content', "")
    #     if isinstance(content, list):
    #         content = " ".join(content)
    #     url = result.get('url', [""])[0]

    #     doc_vector = doc_vectors.get(url)
    #     if doc_vector is None:
    #         doc_vector = model.encode(content, convert_to_tensor=True)
    #         doc_vectors[url] = doc_vector

    #     sim_score = float(util.cos_sim(query_vector, doc_vector))
    #     solr_score = float(result.get('score', 0.0))
    #     final_score = 0.6 * solr_score + 0.4 * sim_score

    #     result["final_score"] = final_score
    #     print(final_score)

    # # Sort by final_score
    # solr_results.sort(key=lambda r: r["final_score"], reverse=True)

    # return solr_results

def parse_solr_results(solr_results):
    if solr_results.hits == 0:
        return {"message": "query out of scope"}
    else:
        api_resp = list()
        rank = 0
        for result in solr_results:
            rank += 1
            title = ""
            url = ""
            content = ""
            meta_info = ""
            if 'title' in result:
                title = result['title']
            if 'url' in result:
                url = result['url']
            if 'content' in result:
                content = result['content']
                if isinstance(content, list):
                    content = " ".join(content)
                meta_info = content[:200]
                meta_info = meta_info.replace("\n", " ")
                meta_info = " ".join(re.findall("[a-zA-Z]+", meta_info))
            link_json = {
                "title": title,
                "url": url,
                "meta_info": meta_info,
                "rank": rank
            }
            api_resp.append(link_json)
    return api_resp


def get_clustering_results(clust_inp, param_type):
    if param_type == "flat_clustering":
        f = open('flat_clustering_output.txt')
        lines = f.readlines()
        f.close()
    elif param_type == "hierarchical_clustering":
        f = open('complete_linkage_clusters.txt')
        lines = f.readlines()
        f.close()

    cluster_map = {}
    for line in lines:
        line_split = line.split(",")
        if line_split[1] == "":
            line_split[1] = "99"
        cluster_map.update({line_split[0]: line_split[1]})

    for curr_resp in clust_inp:
        curr_url = curr_resp["url"][0]
        curr_cluster = cluster_map.get(curr_url, "99")
        curr_resp.update({"cluster": curr_cluster})
        curr_resp.update({"done": "False"})

    clust_resp = []
    curr_rank = 1
    for curr_resp in clust_inp:
        if curr_resp["done"] == "False":
            curr_cluster = curr_resp["cluster"]
            curr_resp.update({"done": "True"})
            curr_resp.update({"rank": str(curr_rank)})
            curr_rank += 1
            clust_resp.append({"title": curr_resp["title"], "url": curr_resp["url"],
                               "meta_info": curr_resp["meta_info"], "rank": curr_resp["rank"]})
            for remaining_resp in clust_inp:
                if remaining_resp["done"] == "False":
                    if remaining_resp["cluster"] == curr_cluster:
                        remaining_resp.update({"done": "True"})
                        remaining_resp.update({"rank": str(curr_rank)})
                        curr_rank += 1
                        clust_resp.append({"title": remaining_resp["title"], "url": remaining_resp["url"],
                                           "meta_info": remaining_resp["meta_info"], "rank": remaining_resp["rank"]})

    return clust_resp


def get_hits_results(clust_inp):
    authority_score_file = open("HITS/precomputed_scores/authority_score_3", 'r').read()
    authority_score_dict = json.loads(authority_score_file)

    clust_inp = sorted(clust_inp, key=lambda x: authority_score_dict.get(x['url'][0], 0.0), reverse=True)
    return clust_inp


    # with open('HITS/precomputed_scores/authority_score_2') as f:
    #     authority_score_dict = json.load(f)
    
    # # Ensure api_resp is a list of dictionaries
    # # if not isinstance(clust_inp, list):
    # #     api_resp = [clust_inp]  # Wrap single dict in a list
    
    # # Add error handling for URL access
    # # clust_inp = []
    # # for item in api_resp:
    # #     if isinstance(item, dict) and 'url' in item:
    # #         clust_inp.append(item)
    
    # # Sort by authority score
    # return sorted(clust_inp, 
    #              key=lambda x: authority_score_dict.get(x.get('url', ''), 0.0), 
    #              reverse=True)


app.run(port='5000')

