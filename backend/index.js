import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";
import cors from "cors";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
// const pythonPath = path.join(
//   process.cwd(),

//   "agent",
//   ".venv",
//   "Scripts",
//   "python.exe",
// );
const pythonPath =process.env.PYTHON || "python3";

const scriptPath = path.join(process.cwd(), "agent", "scrapingAndSentiment.py");

app.use(
  cors({
    origin: "http://localhost:5173",
    methods: ["GET", "POST", "PUT", "DELETE"],
  }),
);

app.use(express.json());

app.get("/homepage/:t", (req, res) => {
  const { t } = req.params;
  const dirPath = path.join(__dirname, "agent", "results", t);
  const file = fs.readdirSync(dirPath);

  const jsonFile = file.find((f) => f.endsWith(".json"));
  const filePath = path.join(dirPath, jsonFile);

  console.log("FilePath: \n", filePath);
  const data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
  console.log("\nDATA:", data);
  res.json(data);
});

function runAgent() {
  const agent = spawn(pythonPath, [scriptPath], {
    cwd: path.join(__dirname, "agent"),
    env: process.env,
  });

  agent.stdout.on("data", (data) => {
    console.log("PYTHON:", data.toString());
  });

  agent.stderr.on("data", (data) => {
    console.error("PYTHON ERROR:", data.toString());
  });

  agent.on("close", (code) => {
    console.log("Agent exited with code", code);
  });
}

let agentStarted = false;

app.listen(5000, () => {
  console.log("Started server");

  if (!agentStarted) {
    agentStarted = true;
    setTimeout(()=>{
      runAgent();

    }, 1000 * 60 *60 *60)
  }
});
