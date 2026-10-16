import assert from "node:assert/strict";
import test from "node:test";

import { filterTasks, greeting, nextStatus, relativeTime, statusLabel } from "../src/taskLogic.js";

test("nextStatus cycles the board columns", () => {
  assert.equal(nextStatus("TODO"), "IN_PROGRESS");
  assert.equal(nextStatus("IN_PROGRESS"), "DONE");
  assert.equal(nextStatus("DONE"), "TODO");
});

test("filterTasks keeps the full list for ALL", () => {
  const tasks = [{ status: "TODO" }, { status: "DONE" }];
  assert.equal(filterTasks(tasks, "ALL").length, 2);
  assert.deepEqual(filterTasks(tasks, "DONE"), [{ status: "DONE" }]);
});

test("statusLabel and relativeTime format display values", () => {
  assert.equal(statusLabel("IN_PROGRESS"), "IN PROGRESS");
  const now = Date.parse("2026-10-16T12:00:00Z");
  assert.equal(relativeTime("2026-10-16T11:58:00Z", now), "2 min ago");
  assert.equal(relativeTime("not-a-date", now), "");
});

test("greeting follows the local hour", () => {
  assert.equal(greeting(new Date("2026-10-16T08:00:00")), "Good morning");
  assert.equal(greeting(new Date("2026-10-16T15:00:00")), "Good afternoon");
  assert.equal(greeting(new Date("2026-10-16T20:00:00")), "Good evening");
});
