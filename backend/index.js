import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";
import cors from "cors";
import { spawn } from "child_process";
import pool from "./db/db.js";
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const app = express();
import routes from "./routes/health.js";
import { client, connectRedis } from ("./db/redis");

connectRedis();
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

app.get("/invalidate/:t",async (req,res)=>{
  const {t} = req.params;
  const cachedKey = `homepage:${t}`;
  try{
    await client.del(cachedKey)
    res.json({message:"Cache removed"})
  }
  catch(err){
    res.status(500).json({error:"FAiled to remove cache"})
  }

})
app.get("/homepage/:t", async (req, res) => {
  const { t } = req.params;
  // const dirPath = path.join(__dirname, "agent", "results", t);
  // const file = fs.readdirSync(dirPath);

  // const jsonFile = file.find((f) => f.endsWith(".json"));
  // var filePath = path.join(dirPath, jsonFile);

  // console.log("FilePath: \n", filePath);

  const cacheKey = `homepage:${t}`;

  try {
    const cached = await client.get(cacheKey);

    if (cached) {
      console.log("Cache found; returing data from redis");
      return res.json(JSON.parse(cached));
    }
 
    const [rows] = await pool.query(
      "SELECT asset, sentiment, reasoning FROM sentiment_results WHERE time_range = ?",
      [t],
    );
     // Redis 
    await client.setEx(cacheKey, 3600, JSON.stringify(rows));
    res.json(rows);
  } catch (error) {
    console.log("Error while executing fetching: \n", error);
    res.status(500).json({ error: "DB Error" });
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
