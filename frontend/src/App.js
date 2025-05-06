// App.jsx
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
      return <p style={{ fontStyle: 'italic', color: '#fff' }}>No results found.</p>;
    }
    return results.map((item, index) => (
      <div key={index} style={{ marginBottom: '1em' }}>
        <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ fontWeight: 'bold' }}>{item.title}</a>
        <p style={{ fontSize: '0.9em' }}>{item.url}<br />{item.meta_info}</p>
      </div>
    ));
  };

  return (
    <div>
      <div className="background-image" ></div>
      <div className="app-container">
        <header className="top-bar">
          <span>Australia Search Engine</span>
        </header>

        <section className="search-section">
          <div className="search-bar-group">
            <input
              type="text"
              placeholder="Enter query..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button onClick={handleSearch}>Search</button>
          </div>

          <div className="toolbar">
            <div className="toggle-group">
              <legend>Relevance</legend>
              <div className="toggle-buttons">
                <input type="radio" id="page_rank" name="type" value="page_rank" checked={type === 'page_rank'} onChange={() => setType('page_rank')} />
                <label htmlFor="page_rank">PageRank</label>
                <input type="radio" id="hits" name="type" value="hits" checked={type === 'hits'} onChange={() => setType('hits')} />
                <label htmlFor="hits">HITS</label>
              </div>
            </div>

            <div className="toggle-group">
              <legend>Clustering</legend>
              <div className="toggle-buttons">
                <input type="radio" id="flat_clustering" name="type" value="flat_clustering" checked={type === 'flat_clustering'} onChange={() => setType('flat_clustering')} />
                <label htmlFor="flat_clustering">Flat</label>
                <input type="radio" id="hierarchical_clustering" name="type" value="hierarchical_clustering" checked={type === 'hierarchical_clustering'} onChange={() => setType('hierarchical_clustering')} />
                <label htmlFor="hierarchical_clustering">Hierarchical</label>
              </div>
            </div>

            <div className="toggle-group">
              <legend>Query Expansion</legend>
              <div className="toggle-buttons">
                <input type="radio" id="association_qe" name="type" value="association_qe" checked={type === 'association_qe'} onChange={() => setType('association_qe')} />
                <label htmlFor="association_qe">Association</label>
                <input type="radio" id="metric_qe" name="type" value="metric_qe" checked={type === 'metric_qe'} onChange={() => setType('metric_qe')} />
                <label htmlFor="metric_qe">Metric</label>
                <input type="radio" id="scalar_qe" name="type" value="scalar_qe" checked={type === 'scalar_qe'} onChange={() => setType('scalar_qe')} />
                <label htmlFor="scalar_qe">Scalar</label>
              </div>
            </div>
          </div>
        </section>

        {/* 3-Column Layout Section */}
        <div style={{ display: 'flex', gap: '1.5%', marginTop: '2rem' }}>
          <div style={{ flex: 1 }}>
            <h2 style={{ color: 'white' }}>Internal Results</h2>
            <section id="results">{renderResults()}</section>
          </div>

          <div style={{ flex: 1 }}>
            <h2 style={{ color: 'white' }}>Google Search</h2>
            <iframe id="google" title="google" width="100%" height="500" />
          </div>

          <div style={{ flex: 1 }}>
            <h2 style={{ color: 'black' }}>Bing Search</h2>
            <iframe id="bing" title="bing" width="100%" height="500" />
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
