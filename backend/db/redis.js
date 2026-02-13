import redis from "redis";

export const client = redis.createClient({
  url: process.env.REDIS_URL,
});

client.on("error", (err) => {
  console.error("❌ Redis Error:", err);
});

export const connectRedis = async () => {
  try {
    await client.connect();
    console.log("✅ Redis Connected");
  } catch (err) {
    console.error("❌ Redis Connection Failed:", err);
  }
};

