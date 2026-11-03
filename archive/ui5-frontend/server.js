
const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 8080;

// Serve the production SAPUI5 application
app.use(express.static(path.join(__dirname, "dist")));

// Send index.html for the application entry point
app.get("/{*splat}", (req, res) => {
    res.sendFile(path.join(__dirname, "dist", "index.html"));
});

app.listen(PORT, "0.0.0.0", () => {
    console.log(`Career Orchestrator running on port ${PORT}`);
});
