import express from "express";
import { mongoose } from "../db/db.js";

const router = express.Router();

router.get("/health/db", async (req, res) => {
 try {
    // Check if the connection state is 'connected' (1)
    if (mongoose.connection.readyState === 1) {
      res.json({ status: "ok", db: "mongodb", state: "connected" });
    } else {
      throw new Error("MongoDB not connected");
    }
  } catch (err) {
    console.error("DB HEALTH CHECK FAILED:", err.message);
    res.status(500).json({
      status: "error",
      db: "mongodb",
      state: "disconnected",
      error: err.message,
    });
  }
});

export default router;