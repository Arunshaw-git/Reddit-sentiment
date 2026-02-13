import redis from "redis";

const client = redis.createClient({
  url: process.env.REDIS_URL,
});

client.on("error", (err) => {
  console.error("❌ Redis Error:", err);
});

const connectRedis = async () => {
  try {
    await client.connect();
    console.log("✅ Redis Connected");
  } catch (err) {
    console.error("❌ Redis Connection Failed:", err);
  }
};

module.exports = { client, connectRedis };