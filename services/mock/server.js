const http = require("http");
const express = require("express");
const exampleJson = require("./example/example.json");

const app = express();
app.use(express.json());

console.logCopy = console.log.bind(console);

// Example
app.get("/mock/example", (req, res) => {
    console.log(req);
    res.send(exampleJson);
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
