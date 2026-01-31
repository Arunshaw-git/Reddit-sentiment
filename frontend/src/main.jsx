// Example from src/index.js (or main.jsx)
import React from "react";
import ReactDOM from "react-dom/client";
import Homepage from "./Homepage.jsx"; // Import the main App component
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

const root = ReactDOM.createRoot(document.getElementById("app"));
root.render(
  <React.StrictMode>
    <div className="main">
      <Homepage />
    </div>
  </React.StrictMode>,
);
