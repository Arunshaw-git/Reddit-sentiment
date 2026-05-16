import React from "react";

const SentimentCard = ({ el, i, expanded, onToggle }) => {
  const getSentimentIcon = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return "↗";
      case 'negative': return "↘";
      default: return "−";
    }
  };

  return (
    <div
      className={`sentiment-card ${expanded ? "expanded" : ""}`}
      onClick={onToggle}
    >
      <div className="card-ticker">
        <span className="symbol">{el.asset}</span>
        <span className="name">{el.asset_name || "Market Asset"}</span>
        <div className="card-meta">
          <span className="subreddit-badge">r/{el.subreddit}</span>
          <div className="meta-item">
            <span>💬 {el.num_comments}</span>
          </div>
          <div className="meta-item">
            <span>📊 Score: {el.score}</span>
          </div>
        </div>
      </div>

      <div className="card-sentiment">
        <span className="sentiment-label">Sentiment</span>
        <div className={`sentiment-value ${el.sentiment?.toLowerCase()}`}>
          <span className="icon">{getSentimentIcon(el.sentiment)}</span>
          <span className="text">{el.sentiment?.toUpperCase()}</span>
        </div>
        
        <div className="confidence-container">
          <div className="confidence-header">
            <span>AI Confidence</span>
            <span>{Math.round((el.confidence || 0) * 100)}%</span>
          </div>
          <div className="confidence-bar-bg">
            <div 
              className="confidence-bar-fill" 
              style={{ width: `${(el.confidence || 0) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="card-reasoning-summary">
        <span className="reason-label">Analysis Summary</span>
        <p className="reason-text-inline">
          {el.reasoning || "Analyzing latest Reddit discussions..."}
        </p>
        
        <a 
          href={`https://www.reddit.com${el.url}`} 
          target="_blank" 
          rel="noopener noreferrer"
          className="btn-view-post"
          onClick={(e) => e.stopPropagation()}
        >
          View on Reddit ↗
        </a>
      </div>

    </div>
  );
};

export default SentimentCard;
