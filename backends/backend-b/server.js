const express = require("express");

const app = express();

const PORT = 3002;
const HOST = "0.0.0.0";

// Middleware: add our backend identification header
app.use((req, res, next) => {
    res.setHeader("X-Backend", "B");
    next();
});

// GET /
app.get("/", (req, res) => {
    res.json({
        backend: "B",
        message: "Hello from Backend B",
        server: "Mac 4"
    });
});

// GET /api/status
app.get("/api/status", (req, res) => {
    res.json({
        backend: "B",
        status: "ok"
    });
});

// Start server
app.listen(PORT, HOST, () => {
    console.log(`Backend B running at http://${HOST}:${PORT}`);
});
