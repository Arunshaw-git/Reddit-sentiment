import React, { useEffect, useState } from "react";
import "./stles/homepage.css";
import SentimentCard from "./SentimentCard";
import heroVideo from "./hero video/Waves_rolling_left_202604230655.mp4";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

const Homepage = () => {
  const [results, setResults] = useState([]);
  const [timeRange, setTimeRange] = useState("today");
  const [expandedIndex, setExpandedIndex] = useState(null);
  const timeRanges = ["today", "week", "month", "year"];

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetch(`${API_URL}/homepage/${timeRange}`);
        const data = await res.json();
        setResults(data);
      } catch (error) {
        console.error("Error while fetching", error);
      }
    };
    loadData();
  }, [timeRange]);

  return (
    <div className="app-container">
      {/* Hero Section */}
      <section className="hero">
        <video
          className="hero-video"
          autoPlay
          loop
          muted
          playsInline
        >
          <source src={heroVideo} type="video/mp4" />
        </video>

        <div className="hero-content animate-in">
          <h1>ESCAPE <br /> THE <br /> <span className="outline">NOISE</span></h1>
          <p className="hero-tagline">RAW SIGNAL. UNFILTERED DATA. NO DISTRACTIONS.</p>
          <div className="hero-actions">
            <button className="btn-terminal">ACCESS TERMINAL</button>
            <button className="btn-outline">VIEW PROTOCOLS</button>
          </div>
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

        <div className="results-list">
          {results.length > 0 ? (
            results.map((el, i) => (
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
              LOADING QUANT DATA...
            </p>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-brand">SENTIMENT ANALYTICA</div>
        <div className="footer-copy">© 2024 SENTIMENT ANALYTICA. ALL RIGHTS RESERVED. DATA IS DELAYED.</div>
      </footer>
    </div>
  );
};

export default Homepage;
