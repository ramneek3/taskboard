const API = "/api";

async function request(path, options) {
  const response = await fetch(`${API}${path}`, options);
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // Non-JSON error bodies still surface as HTTP failures.
    }
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  if (response.status === 204) return null;
  return response.json();
}

export function fetchTasks() {
  return request("/tasks");
}

export function fetchStats() {
  return request("/tasks/stats");
}

export function createTask(payload) {
  return request("/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function updateTask(id, payload) {
  return request(`/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function deleteTask(id) {
  return request(`/tasks/${id}`, { method: "DELETE" });
}
