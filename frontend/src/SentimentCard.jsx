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
      </div>

      <div className="card-sentiment">
        <span className="sentiment-label">Sentiment</span>
        <div className={`sentiment-value ${el.sentiment?.toLowerCase()}`}>
          <span className="icon">{getSentimentIcon(el.sentiment)}</span>
          <span className="text">{el.sentiment?.toUpperCase()}</span>
        </div>
      </div>

      <div className="card-reasoning-summary">
        <span className="reason-label">Analysis Summary</span>
        <p className="reason-text-inline">
          {el.reasoning || "Analyzing latest Reddit discussions..."}
        </p>
      </div>

      {/* Expanded details could still exist for extra long text if needed, 
          but the main reason is now in the probability map's spot */}
      {expanded && (
        <div className="card-details-full">
           <div className="divider"></div>
           <p className="full-reasoning">{el.reasoning}</p>
        </div>
      )}
    </div>
  );
};

export default SentimentCard;
