// App.jsx
import React, { useState } from 'react';
import './style.css';

const BASE_URL = 'http://localhost:5000/api/v1/indexer';

function App() {
  const [query, setQuery] = useState('');
  const [type, setType] = useState('page_rank');
  const [results, setResults] = useState([]);
  const [usedQuery, setUsedQuery] = useState('');

  const handleSearch = async () => {
    try {
      const response = await fetch(`${BASE_URL}?query=${query}&type=${type}`);
      const data = await response.json();
      if (Array.isArray(data.results)) {
      setResults(data.results);
      setUsedQuery(data.query);
    } else {
      setResults([]);
      setUsedQuery(data.query || query);
    }

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
        <p style={{ fontSize: '0.9em', color: "black" }}>{item.url}<br />{item.meta_info}</p>
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
              <legend>Search Type</legend>
              <select value={type} onChange={(e) => setType(e.target.value)}>
                <optgroup label="Relevance">
                  <option value="page_rank">PageRank</option>
                  <option value="hits">HITS</option>
                </optgroup>
                <optgroup label="Clustering">
                  <option value="flat_clustering">Flat</option>
                  <option value="hierarchical_clustering">Hierarchical</option>
                </optgroup>
                <optgroup label="Query Expansion">
                  <option value="association_qe">Association</option>
                  <option value="metric_qe">Metric</option>
                  <option value="scalar_qe">Scalar</option>
                </optgroup>
              </select>
            </div>
          </div>

        </section>
        <section>
        <p style={{ color: 'white', fontStyle: 'italic' }}>
          Showing results for: <strong>{usedQuery}</strong>
        </p>
        </section>

        {/* 3-Column Layout Section */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '1.5%',
            marginTop: '2rem',
            height: '500px' // Consistent height for all children
          }}
        >
          <div style={{ flex: '1 1 32%' , flexDirection: 'column', display: 'flex', height: '100%' }}>
            <h2 style={{ color: 'white' }}>Internal Results</h2>
            <div style={{overflowY: "auto", flexGrow: 1, minHeight: 0 }}> 
              <section id="results">{renderResults()}</section>

            </div>
          </div>

          <div style={{ flex: '1 1 32%', height: '100%' }}>
            <h2 style={{ color: 'white' }}>Google Search</h2>
            <iframe id="google" title="google" width="100%" height="100%" />
          </div>

          <div style={{ flex: '1 1 32%', height: '100%' }}>
            <h2 style={{ color: 'black' }}>Bing Search</h2>
            <iframe id="bing" title="bing" width="100%" height="100%" />
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
