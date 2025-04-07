const http = require("http");
const express = require("express");
const answersJson = require("./answers.json");

const app = express();
app.use(express.json());

console.logCopy = console.log.bind(console);

app.get("/mock/backend/getResponse", (req, res) => {
    console.log(req);

    // delay response by 0-5 seconds
    const delay = Math.floor(Math.random() * 5) * 1000;

    console.log(delay);

    setTimeout(() => {
        // send one of the answers in the frontend/answers.json file
        const randomIndex = Math.floor(Math.random() * answersJson.length);
        const randomAnswer = answersJson[randomIndex];
        res.send(randomAnswer);
    }, delay);
});

const httpServer = http.createServer(app);
const port = process.env.PORT ?? 8080;

httpServer.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});

console.log = function (message) {
    const time = new Date().toLocaleTimeString();
    this.logCopy(time,message);
}
