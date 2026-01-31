import React, { useEffect, useState } from "react";
import "./stles/homepage.css";
import SentimentCard from "./SentimentCard";
// import SentimentCard from "./SentimentCard";
import 'dotenv/config'; 

const API_URL = process.env.API_KEY;

const homepage = () => {
  const [results, setResults] = useState([]);
  const [timeRange, setTimeRange] = useState("today");
  const timeRanges = ["today", "week", "month", "year"];
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
        const res = await fetch(`${API_URL}/homepage/${timeRange}`);
        const data = await res.json();
        console.log("wtf:\n", data);
        setResults(data);
      } catch (error) {
        console.error("Error while fetch", error);
      }
    };

    loadData();
  }, [timeRange]);

  return (
    <div className="container my-2 ">
      <div className="text-center my-3">
        <h1 className="logo">REDDIT BASED SENTIMENT</h1>
      </div>

      <p className="text-center" style={{ color: "white" }}>
        Aggregated stock & sector sentiment extracted from Reddit discussions
      </p>

      <div className="dropdown">
        <button
          className="btn btn-secondary dropdown-toggle"
          type="button"
          id="dropdownMenuButton"
          data-bs-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
        >
          {timeRange.toUpperCase()}
        </button>

        <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton">
          {timeRanges.map((element) => (
            <li key={element}>
              <button
                className={`dropdown-item ${
                  element === timeRange ? "active" : ""
                }`}
                onClick={() => setTimeRange(element)}
              >
                {element}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <br />

      <div className="row">
        {results.map((el, i) => {
          return <SentimentCard key={i} i={i} el={el}></SentimentCard>;
        })}
      </div>
    </div>
  );
};

export default homepage;
