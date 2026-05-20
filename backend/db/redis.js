import client from "ioredis";
import dotenv from "dotenv";
dotenv.config();

const redisClient = new client(
    process.env.REDIS_URL,{maxRetriesPerRequest: 1,
    lazyConnect: true,
    family: 0,}
);

redisClient.on(
    "connect",
    ()=>{   
        console.log("Connected to Redis");
    }
);

redisClient.on("error", (err) => {
    console.error("Redis error:", err);
});

export default redisClient;
