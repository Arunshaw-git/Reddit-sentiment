import React, { useState } from "react";
import "./stles/homepage.css";

const SentimentCard = ({ el, i, expanded, onToggle}) => {

  return (
    <li
      className={`result-item ${expanded ? "expanded" : ""}`}
      onClick={onToggle}
    >
      <div className="list">
        <div className="left">
          <h1 className="index">{i}</h1>
        </div>

        <div className="content">
          <h2 className="assetName">{el.asset}</h2>
          <span className={`sentiment ${el.sentiment}`}>{el.sentiment}</span>
          <p className="reasoning">{el.reasoning}</p>
        </div>
      </div>
    </li>
  );
};
export default SentimentCard;
