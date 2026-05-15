import React, { useEffect, useState } from "react";
import "./stles/homepage.css";
import SentimentCard from "./SentimentCard";
import heroBg from "/herobg.jpeg";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

const Homepage = () => {
  const [results, setResults] = useState([]);
  const [timeRange, setTimeRange] = useState("today");
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [selectedSubreddit, setSelectedSubreddit] = useState("all");
  const timeRanges = ["today", "week", "month", "year"];

  // Extract unique subreddits for filtering
  const subreddits = ["all", ...new Set(results.map(r => r.subreddit).filter(Boolean))];

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetch(`${API_URL}/homepage/${timeRange}`);
        const data = await res.json();
        setResults(data);
        setSelectedSubreddit("all"); // Reset filter on time range change
      } catch (error) {
        console.error("Error while fetching", error);
      }
    };
    loadData();
  }, [timeRange]);

  const filteredResults = selectedSubreddit === "all" 
    ? results 
    : results.filter(r => r.subreddit === selectedSubreddit);

  return (
    <div className="app-container">
      {/* Hero Section */}
      <section className="hero">
        <img
          className="hero-bg"
          src={heroBg}
          alt="Hero background"
        />

        <div className="hero-content animate-in">
          <h1>ESCAPE <br /> THE <br /> <span className="outline">NOISE</span></h1>
          <p className="hero-tagline">RAW SIGNAL. UNFILTERED DATA. NO DISTRACTIONS.</p>
        </div>
      </section>

      {/* Main Data Section */}
      <main className="data-section">
        <div className="section-header">
          <div className="section-title">LIVE MARKET SENTIMENT / {timeRange.toUpperCase()}</div>
          <select
            className="custom-dropdown"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            {timeRanges.map(range => (
              <option key={range} value={range}>{range.toUpperCase()}</option>
            ))}
          </select>
        </div>

        {/* Subreddit Filter */}
        {subreddits.length > 1 && (
          <div className="filter-container">
            {subreddits.map(sub => (
              <button
                key={sub}
                className={`filter-chip ${selectedSubreddit === sub ? "active" : ""}`}
                onClick={() => setSelectedSubreddit(sub)}
              >
                {sub === "all" ? "ALL SUBREDDITS" : `r/${sub}`}
              </button>
            ))}
          </div>
        )}

        <div className="results-list">
          {filteredResults.length > 0 ? (
            filteredResults.map((el, i) => (
              <SentimentCard
                key={i}
                i={i}
                el={el}
                expanded={expandedIndex === i}
                onToggle={() => setExpandedIndex(expandedIndex === i ? null : i)}
              />
            ))
          ) : (
            <p style={{ textAlign: "center", color: "var(--text-dim)", padding: "2rem" }}>
              {results.length === 0 ? "LOADING QUANT DATA..." : "NO RESULTS MATCHING FILTER"}
            </p>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-brand">SENTIMENT ANALYTICA</div>
        <div className="footer-copy">Made by Arun Shaw 2026</div>
      </footer>
    </div>
  );
};

export default Homepage;
