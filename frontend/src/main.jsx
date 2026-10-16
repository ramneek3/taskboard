import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";

import { createTask, deleteTask, fetchStats, fetchTasks, updateTask } from "./api.js";
import { FILTERS, filterTasks, greeting, nextStatus, relativeTime, statusLabel } from "./taskLogic.js";
import "./styles.css";

const EMPTY_STATS = { total: 0, todo: 0, inProgress: 0, done: 0 };

function App() {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState(EMPTY_STATS);
  const [filter, setFilter] = useState("ALL");
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);
  const visible = useMemo(() => filterTasks(tasks, filter), [tasks, filter]);
  const activity = useMemo(
    () => [...tasks].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5),
    [tasks],
  );

  async function load() {
    try {
      setError("");
      const [nextTasks, nextStats] = await Promise.all([fetchTasks(), fetchStats()]);
      setTasks(nextTasks);
      setStats(nextStats);
    } catch (err) {
      setError(err.message || "Backend unavailable");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function advance(task) {
    try {
      setError("");
      await updateTask(task.id, { status: nextStatus(task.status) });
      await load();
    } catch (err) {
      setError(err.message || "Could not update the task");
    }
  }

  async function remove(task) {
    if (!window.confirm(`Delete “${task.title}”?`)) return;
    try {
      setError("");
      await deleteTask(task.id);
      await load();
    } catch (err) {
      setError(err.message || "Could not delete the task");
    }
  }

  async function onCreate(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSaving(true);
    setFormError("");
    try {
      await createTask({
        title: form.get("title"),
        description: form.get("description") || "",
        priority: form.get("priority"),
        assignee: form.get("assignee") || "Unassigned",
        status: "TODO",
      });
      event.currentTarget.reset();
      setShowForm(false);
      await load();
    } catch (err) {
      setFormError(err.message || "Could not create the task");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">T</span>
          <div>
            <b>TaskBoard</b>
            <small>DevOps Capstone</small>
          </div>
        </div>
        <nav>
          <a className="active" href="#tasks">▦ <span>Dashboard</span></a>
          <a href="#tasks">✓ <span>My Tasks</span></a>
          <a href="#activity">◫ <span>Activity</span></a>
        </nav>
        <div className="side-bottom">
          <div className="upgrade">
            <strong>Ship with confidence.</strong>
            <p>Tests, images, scans, and metrics travel with every change.</p>
          </div>
          <div className="profile">
            <div className="avatar">AR</div>
            <div>
              <b>Alex Rivera</b>
              <small>Workspace owner</small>
            </div>
          </div>
        </div>
      </aside>
      <main className="main">
        <header>
          <div>
            <p className="eyebrow">WORKSPACE / OVERVIEW</p>
            <h1>{greeting()}, Alex</h1>
            <p className="muted">Track delivery work from laptop to cluster.</p>
          </div>
          <button className="primary" type="button" onClick={() => setShowForm(true)}>
            ＋ New task
          </button>
        </header>
        {error && (
          <div className="alert" role="alert">
            ⚠ {error}. Check that the API and database are running, then refresh.
          </div>
        )}
        <section className="stats">
          <Stat label="Total tasks" value={stats.total} icon="▦" />
          <Stat label="To do" value={stats.todo} icon="○" />
          <Stat label="In progress" value={stats.inProgress} icon="◔" />
          <Stat label="Completed" value={stats.done} icon="✓" />
        </section>
        <section className="content-grid">
          <div className="panel tasks-panel" id="tasks">
            <div className="panel-head">
              <div>
                <h2>Tasks</h2>
                <p className="muted">Advance status or remove work that is done.</p>
              </div>
              <div className="filters" role="tablist" aria-label="Filter tasks">
                {FILTERS.map((item) => (
                  <button
                    className={filter === item ? "selected" : ""}
                    onClick={() => setFilter(item)}
                    key={item}
                    type="button"
                  >
                    {item === "ALL" ? "All" : statusLabel(item)}
                  </button>
                ))}
              </div>
            </div>
            {loading ? (
              <div className="empty">Loading tasks…</div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Task</th>
                      <th>Assignee</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visible.map((task) => (
                      <tr key={task.id}>
                        <td>
                          <div className="task-title">
                            <span className={`dot ${task.status.toLowerCase()}`} />
                            <div>
                              <b>{task.title}</b>
                              <small>{task.description || "No description"}</small>
                            </div>
                          </div>
                        </td>
                        <td>{task.assignee}</td>
                        <td>
                          <span className={`priority ${task.priority.toLowerCase()}`}>{task.priority}</span>
                        </td>
                        <td>
                          <span className={`status ${task.status.toLowerCase()}`}>{statusLabel(task.status)}</span>
                        </td>
                        <td className="row-actions">
                          <button className="icon-btn" type="button" onClick={() => advance(task)} title="Advance status">
                            ↻
                          </button>
                          <button className="icon-btn danger" type="button" onClick={() => remove(task)} title="Delete task">
                            ✕
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {!visible.length && (
                  <div className="empty">
                    {tasks.length ? "No tasks in this filter." : "No tasks yet. Create the first one."}
                  </div>
                )}
              </div>
            )}
          </div>
          <aside className="panel activity" id="activity">
            <div className="panel-head">
              <div>
                <h2>Recent activity</h2>
                <p className="muted">Newest tasks in this workspace.</p>
              </div>
            </div>
            {activity.length === 0 && <div className="empty">Activity appears after the first task.</div>}
            {activity.map((task) => (
              <Activity
                key={task.id}
                icon={task.status === "DONE" ? "✓" : "＋"}
                text={`${task.title} · ${statusLabel(task.status)}`}
                time={relativeTime(task.created_at)}
              />
            ))}
            <div className="pipeline">
              <span>CI</span>
              <i />
              <span>Build</span>
              <i />
              <span>Scan</span>
              <i />
              <span>Deploy</span>
            </div>
          </aside>
        </section>
        {showForm && (
          <div className="modal-backdrop">
            <form className="modal" onSubmit={onCreate}>
              <div className="modal-head">
                <div>
                  <p className="eyebrow">CREATE TASK</p>
                  <h2>Add a new task</h2>
                </div>
                <button type="button" className="close" onClick={() => setShowForm(false)} aria-label="Close">
                  ×
                </button>
              </div>
              {formError && (
                <div className="alert" role="alert">
                  ⚠ {formError}
                </div>
              )}
              <label>
                Task title
                <input name="title" required placeholder="e.g. Configure production ingress" />
              </label>
              <label>
                Description
                <textarea name="description" placeholder="What needs to be done?" />
              </label>
              <div className="form-row">
                <label>
                  Priority
                  <select name="priority" defaultValue="MEDIUM">
                    <option>LOW</option>
                    <option>MEDIUM</option>
                    <option>HIGH</option>
                  </select>
                </label>
                <label>
                  Assignee
                  <input name="assignee" defaultValue="Alex Rivera" />
                </label>
              </div>
              <button className="primary full" type="submit" disabled={saving}>
                {saving ? "Creating…" : "Create task"}
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}

function Stat({ label, value, icon }) {
  return (
    <div className="stat">
      <div className="stat-icon">{icon}</div>
      <div>
        <small>{label}</small>
        <strong>{value}</strong>
        <span>Live from the API</span>
      </div>
    </div>
  );
}

function Activity({ icon, text, time }) {
  return (
    <div className="activity-row">
      <span className="activity-icon">{icon}</span>
      <div>
        <b>{text}</b>
        <small>{time}</small>
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
