import React, { useState } from 'react';
import './style.css';

const BASE_URL = 'http://localhost:5000/api/v1/indexer';

function App() {
  const [query, setQuery] = useState('');
  const [type, setType] = useState('page_rank');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    try {
      const response = await fetch(`${BASE_URL}?query=url:${query}&type=${type}`);
      const data = await response.json();
      setResults(Array.isArray(data) ? data : []);

      document.getElementById('google').src = `https://www.google.com/search?igu=1&source=hp&ei=lheWXriYJ4PktQXN-LPgDA&q=${query}`;
      document.getElementById('bing').src = `https://www.bing.com/search?q=${query}`;
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const renderResults = () => {
    if (!results || results.length === 0) {
      return <p style={{ fontStyle: 'italic', color: '#777' }}>No results found.</p>;

    }
  
    return results.map((item, index) => (
      <div key={index}>
        <a href={item.url}>{item.title}</a>
        <p>{item.url}<br />{item.meta_info}</p>
      </div>
    ));
  };

  return (
    <div className="App">
      <h1>Australia Search Engine</h1>
      <form className="form-section" onSubmit={(e) => e.preventDefault()}>
        <input
          type="text"
          placeholder="Enter query here..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <fieldset>
          <legend>Relevance Model Options:</legend>
          <input type="radio" id="page_rank" name="type" value="page_rank" checked={type === 'page_rank'} onChange={() => setType('page_rank')} />
          <label htmlFor="page_rank">Page Rank</label>
          <input type="radio" id="hits" name="type" value="hits" checked={type === 'hits'} onChange={() => setType('hits')} />
          <label htmlFor="hits">HITS</label>
        </fieldset>

        <fieldset>
          <legend>Clustering Options:</legend>
          <input type="radio" id="flat_clustering" name="type" value="flat_clustering" checked={type === 'flat_clustering'} onChange={() => setType('flat_clustering')} />
          <label htmlFor="flat_clustering">Flat Clustering</label>
          <input type="radio" id="hierarchical_clustering" name="type" value="hierarchical_clustering" checked={type === 'hierarchical_clustering'} onChange={() => setType('hierarchical_clustering')} />
          <label htmlFor="hierarchical_clustering">Hierarchical Clustering</label>
        </fieldset>

        <fieldset>
          <legend>Query Expansion Option:</legend>
          <input type="radio" id="association_qe" name="type" value="association_qe" checked={type === 'association_qe'} onChange={() => setType('association_qe')} />
          <label htmlFor="association_qe">Association</label>
          <input type="radio" id="metric_qe" name="type" value="metric_qe" checked={type === 'metric_qe'} onChange={() => setType('metric_qe')} />
          <label htmlFor="metric_qe">Metric</label>
          <input type="radio" id="scalar_qe" name="type" value="scalar_qe" checked={type === 'scalar_qe'} onChange={() => setType('scalar_qe')} />
          <label htmlFor="scalar_qe">Scalar</label>
        </fieldset>

        <input type="button" value="Search" onClick={handleSearch} />
      </form>

      <section id="results">{renderResults()}</section>

      <h2 style={{ color: 'dodgerblue' }}>Google Search</h2>
      <iframe id="google" title="google" width="90%" height="500" />

      <h2 style={{ color: 'brown' }}>Bing Search</h2>
      <iframe id="bing" title="bing" width="90%" height="500" />
    </div>
  );
}

export default App;

