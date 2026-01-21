import React, { useEffect, useState } from "react";
import fs from "fs";
import path from "path";
import "./stles/homepage.css";
// import SentimentCard from "./SentimentCard";

const homepage = () => {
  const [results, setResults] = useState([]);

  // useEffect(async () => {
  //   try {
  //     const res = await fetch("http://localhost:5000/homepage/today");

  //     const data = res.json();
  //     console.log(data);
  //     setResults(data);
  //   } catch (error) {
  //     console.log("Fetching error",error)
  //   }
  // }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetch("http://localhost:5000/homepage/today");
        const data = await res.json();
        console.log("wtf:\n", data);
        setResults(data);
      } catch (error) {
        console.error("Error while fetch", error);
      }
    };

    loadData();
  }, []);

  return (
    <div className="container my-2 ">
      <h1 className="logo  ">REDDIT BASED SENTIMENT</h1>
      <p className="text-muted text-center">
        Aggregated stock & sector sentiment extracted from Reddit discussions
      </p>
      <div className="row">
        {results.map((el, i) => {
          return (
            <li className="result-item">
              <div className="list">
                <div className="left">
                  <h1 className="index">{i}</h1>
                </div>

                <div className="content">
                  <h2 className="assetName">{el.ticker}</h2>
                  <span className={`sentiment ${el.sentiment}`}>
                    {el.sentiment}
                  </span>
                  <p className="reasoning">{el.reasoning}</p>
                </div>
              </div>
            </li>
          );
        })}
      </div>
    </div>
  );
};

export default homepage;
