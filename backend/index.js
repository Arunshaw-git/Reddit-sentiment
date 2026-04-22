import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";
import cors from "cors";
import { spawn } from "child_process";
import { SentimentResult } from "./db/db.js";
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const app = express();
import routes from "./routes/health.js";
// import { client, connectRedis } from "./db/redis.js";

// connectRedis();
app.use(routes);
// const pythonPath = path.join(
//   process.cwd(),

//   "agent",
//   ".venv",
//   "Scripts",
//   "python.exe",
// );

const pythonPath = process.env.PYTHON || "python3";

const scriptPath = path.join(process.cwd(), "agent", "scrapingAndSentiment.py");

app.use(
  cors({
    origin: ["http://localhost:5173", "https://redditstocks.netlify.app"],
    methods: ["GET", "POST", "PUT", "DELETE"],
  }),
);

app.use(express.json());

app.get("/run-agent", (req, res) => {
  console.log("Manual trigger: Running agent...");
  runAgent();
  res.json({ message: "Agent started manually. Check Render logs for progress." });
});

app.get("/db-check", async (req, res) => {
  try {
    const count = await SentimentResult.countDocuments();
    const sample = await SentimentResult.findOne().limit(1);
    res.json({ 
      database: "reddit_sentiment",
      collection: "sentiment_results",
      count,
      sample 
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to check DB", message: err.message });
  }
});

app.get("/homepage/:t", async (req, res) => {
  const { t } = req.params;
  // const dirPath = path.join(__dirname, "agent", "results", t);
  // const file = fs.readdirSync(dirPath);

  // const jsonFile = file.find((f) => f.endsWith(".json"));
  // var filePath = path.join(dirPath, jsonFile);

  // console.log("FilePath: \n", filePath);

  // const cacheKey = `homepage:${t}`;
  // 
  // const cached = await client.get(cacheKey);
  // 
  // if (cached) {
  //   console.log("Cache found; returing data from redis");
  //   return res.json(JSON.parse(cached));
  // }
  try {
    const rows = await SentimentResult.find(
      { time_range: t },
      { asset: 1, sentiment: 1, reasoning: 1, _id: 0 }
    );
    // Redis 
    // await client.setEx(cacheKey, 3600, JSON.stringify(rows));
    res.json(rows);
  } catch (error) {
    console.error("Error while fetching sentiment results:", error);
    res.status(500).json({
      error: "Database Query Error",
      message: error.message,
      stack: process.env.NODE_ENV === 'production' ? null : error.stack
    });
  }
});

function runAgent() {
  const agent = spawn(pythonPath, [scriptPath], {
    cwd: path.join(__dirname, "agent"),
    env: process.env,
  });

  agent.stdout.on("data", (data) => {
    console.log("PYTHON ****************:", data.toString());
  });

  agent.stderr.on("data", (data) => {
    console.error("PYTHON ERROR:", data.toString());
  });

  agent.on("close", (code) => {
    console.log("Agent exited with code", code);
  });
}

let agentStarted = false;

// let fileName = null;
// const dirPath = path.join(__dirname, "agent", "results", "today");
// if (fs.existsSync(dirPath)) {
//   const file = fs.readdirSync(dirPath);
//   if (file.length > 0) {
//     fileName = file[0];
//   }
// }

app.listen(5000, () => {
  console.log("Started server");
  const date = new Date().toISOString().slice(0, 10);
  console.log(date);
  if (!agentStarted) {
    agentStarted = true;
    // if (!fileName || !fileName.startsWith(`today_${date}`)) runAgent();
    setTimeout(
      () => {
        runAgent();
      },
      1000 * 60 * 60 * 24,
    );
  }
});
