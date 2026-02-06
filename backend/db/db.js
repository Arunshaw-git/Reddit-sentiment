import mysql from "mysql2/promise";
import "dotenv/config";

const isProd = process.env.NODE_ENV === "production";

const pool = mysql.createPool({
  host: process.env.MYSQL_HOST,
  port: Number(process.env.MYSQL_PORT),
  user: process.env.MYSQL_USER,
  password: process.env.MYSQL_PASSWORD,
  database: process.env.MYSQL_DB,

  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,

  ...(isProd && {
    ssl: {
      rejectUnauthorized: false,
    },
  }),
});

console.log("MySQL pool created");

export default pool;