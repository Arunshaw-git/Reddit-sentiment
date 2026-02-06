import express from "express";
import connectToDB from "../config/connectToDB.js";

const router = express.Router();

router.get("/health/db", async (req, res) => {
 try {
    await pool.query("SELECT 1");
    res.json({ status: "ok", db: "connected" });
  } catch (err) {
    console.error("DB HEALTH CHECK FAILED:", err.message);
    res.status(500).json({
      status: "error",
      db: "disconnected",
      error: err.message,
    });
  }
});

export default router;