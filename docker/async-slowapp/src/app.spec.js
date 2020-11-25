
const request = require("supertest");
const assert = require("chai").assert;
// const expect = require("chai").expect;

const sleep = (delay) => {
    return new Promise(resolve => {
        setTimeout(resolve, delay)
    });
};



describe("express with async-slowapp", function () {
    var server;
    var env;
    before(function () {
        env = process.env;
        let app = require("./app");
        app.setup({ LOG_LEVEL: (process.env.NODE_ENV === "test" ? "warn": "debug"), HOST:"https://fakehost.com"});
        server = app.start({PORT: 9002});
    });

    beforeEach(function () {

    });
    afterEach(function () {

    });
    after(function () {
        process.env = env;
        server.close();
    });

    it("responds to /_ping", (done) => {
        request(server)
            .get("/_ping")
            .expect(200, {ping: "pong"})
            .expect("Content-Type", /json/, done);
    });

    it("responds not found to get /poll poll for missing id", (done) => {
        request(server)
            .get("/poll?id=madeup")
            .expect(404, done);
    });

    it("responds not found to delete /poll poll for missing id", (done) => {
        request(server)
            .delete("/poll?id=madeup")
            .expect(404, done);
    });

    it("responds to /slow with a new content-location", (done) => {
        request(server)
            .get("/slow")
            .expect("Content-Type", /json/)
            .expect(res => {
                let headers = res.res.rawHeaders.asMultiValue();
                assert.isTrue(headers.has('content-location'));
                let cookies = headers.cookies("set-cookie");
                assert.isDefined(cookies["poll-count"]);
                let poll_count = parseInt(cookies["poll-count"].split(";")[0].split("=")[1]);
                // this checks cookies are preserved through the poll cycle
                assert.equal(poll_count, 0);
            })
            .expect(202, done)

    });

    it("responds to /slow with a content-location and poll count increments", (done) => {
        let content_location;
        request(server)
            .get("/slow?complete_in=0.01&final_status=418")
            .expect("Content-Type", /json/)
            .expect(res => {
                let headers = res.res.rawHeaders.asMultiValue();
                assert.isTrue(headers.has('content-location'));
                content_location = headers['content-location'];
                let cookies = headers.cookies("set-cookie");
                assert.isDefined(cookies["poll-count"]);
                let poll_count = parseInt(cookies["poll-count"].split(";")[0].split("=")[1]);
                assert.equal(poll_count, 0);
            })
            .expect(202)
            .end(async ()=>{
                await sleep(500);
                let url = new URL(content_location);
                request(server)
                .get(url.pathname + url.search)
                .set("Cookie", "poll-count=0")
                .expect(res => {
                    let headers = res.res.rawHeaders.asMultiValue();
                    assert.isFalse(headers.has('content-location'));
                    let cookies = headers.cookies("set-cookie");
                    assert.isDefined(cookies["poll-count"]);
                    let poll_count = parseInt(cookies["poll-count"].split(";")[0].split("=")[1]);
                    assert.equal(poll_count, 1);
                })
                .expect(418, done)
            });
    });


});



describe("express with async-slowapp with /sub", function () {
    var server;
    var env;
    before(function () {
        env = process.env;
        let app = require("./app");
        app.setup({ LOG_LEVEL: (process.env.NODE_ENV === "test" ? "warn": "debug"), HOST:"https://fakehost.com/sub"});
        server = app.start({PORT: 9002});
    });

    beforeEach(function () {

    });
    afterEach(function () {

    });
    after(function () {
        process.env = env;
        server.close();
    });

    it("responds to /sub/_ping", (done) => {
        request(server)
            .get("/sub/_ping")
            .expect(200, {ping: "pong"})
            .expect("Content-Type", /json/, done);
    });

    it("responds not found to get /sub/poll poll for missing id", (done) => {
        request(server)
            .get("/sub/poll?id=madeup")
            .expect(404, done);
    });

    it("responds not found to delete /sub/poll poll for missing id", (done) => {
        request(server)
            .delete("/sub/poll?id=madeup")
            .expect(404, done);
    });

    it("responds to /sub/slow with a new content-location", (done) => {
        request(server)
            .get("/sub/slow")
            .expect("Content-Type", /json/)
            .expect(res => {
                let headers = res.res.rawHeaders.asMultiValue();
                assert.isTrue(headers.has('content-location'));
                let cookies = headers.cookies("set-cookie");
                assert.isDefined(cookies["poll-count"]);
                let poll_count = parseInt(cookies["poll-count"].split(";")[0].split("=")[1]);
                // this checks cookies are preserved through the poll cycle
                assert.equal(poll_count, 0);
            })
            .expect(202, done)

    });

    it("responds to /sub/slow with a content-location and poll count increments", (done) => {
        let content_location;
        request(server)
            .get("/sub/slow?complete_in=0.01&final_status=418")
            .expect("Content-Type", /json/)
            .expect(res => {
                let headers = res.res.rawHeaders.asMultiValue();
                assert.isTrue(headers.has('content-location'));
                content_location = headers['content-location'];
                let cookies = headers.cookies("set-cookie");
                assert.isDefined(cookies["poll-count"]);
                let poll_count = parseInt(cookies["poll-count"].split(";")[0].split("=")[1]);
                assert.equal(poll_count, 0);
            })
            .expect(202)
            .end(async ()=>{
                await sleep(500);
                let url = new URL(content_location);
                request(server)
                    .get(url.pathname + url.search)
                    .set("Cookie", "poll-count=0")
                    .expect(res => {
                        let headers = res.res.rawHeaders.asMultiValue();
                        assert.isFalse(headers.has('content-location'));
                        let cookies = headers.cookies("set-cookie");
                        assert.isDefined(cookies["poll-count"]);
                        let poll_count = parseInt(cookies["poll-count"].split(";")[0].split("=")[1]);
                        assert.equal(poll_count, 1);
                    })
                    .expect(418, done)
            });
    });


    it("responds to /sub/poll continues with correct location", (done) => {
        let content_location;
        request(server)
            .get("/sub/slow?complete_in=0.3&final_status=418")
            .expect("Content-Type", /json/)
            .expect(res => {
                let headers = res.res.rawHeaders.asMultiValue();
                assert.isTrue(headers.has('content-location'));
                content_location = headers['content-location'];
                let cookies = headers.cookies("set-cookie");
                assert.isDefined(cookies["poll-count"]);
                let poll_count = parseInt(cookies["poll-count"].split(";")[0].split("=")[1]);
                assert.equal(poll_count, 0);
            })
            .end(async ()=>{
                let url = new URL(content_location);
                request(server)
                    .get(url.pathname + url.search)
                    .set("Cookie", "poll-count=0")
                    .expect(res => {
                        let headers = res.res.rawHeaders.asMultiValue();
                        assert.isTrue(headers.has('content-location'));
                        assert.match(headers['content-location'], /^https:\/\/.*\/sub\/poll\?id=.*/)
                    })
                    .expect(202, done)
            });
    });

});
