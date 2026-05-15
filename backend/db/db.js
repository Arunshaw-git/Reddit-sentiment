import mongoose from "mongoose";
import "dotenv/config";

const mongoUri = process.env.MONGO_URI || "mongodb://localhost:27017/reddit_sentiment";

mongoose.connect(mongoUri, {
  dbName: 'reddit_sentiment'
})
  .then(() => console.log("MongoDB connected successfully"))
  .catch((err) => console.error("MongoDB connection error:", err));

const sentimentResultSchema = new mongoose.Schema({
  id: { type: Number, unique: true },
  time_range: { type: String, enum: ['today', 'week', 'month', 'year'] },
  sentiment: { type: String, enum: ['positive', 'negative', 'mixed', 'neutral'] },
  asset: { type: String, maxlength: 150 },
  reasoning: String,
  url: String,
  score: Number,
  subreddit: String,
  num_comments: Number,
  upvote_ratio: Number,
  confidence: Number,
  created_at: { type: Date, default: Date.now }
}, { collection: 'sentiment_results' });

const SentimentResult = mongoose.model("SentimentResult", sentimentResultSchema);

export { mongoose, SentimentResult };
export default mongoose.connection;