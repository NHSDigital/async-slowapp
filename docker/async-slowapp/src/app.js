"use strict";

const express = require("express");
const app = express();
const log = require("loglevel");

function setup(options) {
    options = options || {};
    log.setLevel(options.LOG_LEVEL || "info");
    app.locals.tracked = {};
    app.locals.base_uri = options.BASE_URI || `http://localhost:${process.env.PORT}`;
}

function start(options) {
    options = options || {};
    let server = app.listen(options.PORT || 9000, () => {
        log.info("server listening on port %d", server.address().port);
    });
    return server;
}

const handlers = require("./handlers");
app.get("/_ping", handlers.ping);
app.get("/_status", handlers.ping);
app.get("/slow", handlers.slow);
app.delete("/poll", handlers.delete_poll);
app.get("/poll", handlers.poll);
app.get("/sub/_ping", handlers.ping);
app.get("/sub/_status", handlers.ping);
app.get("/sub/slow", handlers.slow);
app.delete("/sub/poll", handlers.delete_poll);
app.get("/sub/poll", handlers.poll);


module.exports = {start: start, setup: setup};