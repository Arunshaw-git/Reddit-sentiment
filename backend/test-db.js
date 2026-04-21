import mongoose from "mongoose";
import "dotenv/config";
import { SentimentResult } from "./db/db.js";

async function testConnection() {
  const mongoUri = process.env.MONGO_URI || "mongodb://localhost:27017/reddit_sentiment";
  console.log("Testing connection to:", mongoUri);

  try {
    await mongoose.connect(mongoUri);
    console.log("✅ MongoDB Connection Successful!");
    
    const count = await SentimentResult.countDocuments();
    console.log(`📊 Current document count: ${count}`);
    
    process.exit(0);
  } catch (error) {
    console.error("❌ MongoDB Connection Failed!");
    console.error(error);
    process.exit(1);
  }
}

testConnection();
