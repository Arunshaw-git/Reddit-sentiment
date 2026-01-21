import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import cors from "cors"


const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();

app.use(cors({
    origin: 'http://localhost:5173',
    methods: ['GET', 'POST', 'PUT', 'DELETE'] 
}))
app.use(express.json());

app.get("/homepage/:t", (req,res)=>{
    const {t} = req.params;
    const dirPath = path.join(__dirname, 'agent', 'results',t);
    const file = fs.readdirSync(dirPath)
    
    const jsonFile = file.find(f=>f.endsWith(".json"));
    const filePath = path.join(dirPath,jsonFile)

    console.log("FilePath: \n",filePath)
    const data = JSON.parse(fs.readFileSync(filePath,"utf-8"));
    console.log("\nDATA:",data)
    res.json(data);
});

app.listen("5000",()=>{
    console.log("Started sever ")
})