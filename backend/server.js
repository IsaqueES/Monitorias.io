//? FRAMEWORK
import express, { json } from "express";
const app = express();

app.use(express.json());

const users = [];
//! ROUTES
app.post("/usuarios", (req, res) => {
  users.push(req.body);
  res.send("Tudo certo");
});

app.get("/usuarios", (req, res) => {
  res.json(users);
});

app.listen(3000);

//!SENHA MONGO DB : 16hO3gGh294UK8So
