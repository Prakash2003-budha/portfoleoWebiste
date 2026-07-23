// api.js
// Every call to the backend goes through here. `credentials: "include"`
// is what makes the session cookie work across the frontend's own origin
// (e.g. http://127.0.0.1:5500) talking to the backend's origin
// (e.g. http://127.0.0.1:5000).

const API_BASE = window.PFW_API_BASE || "http://127.0.0.1:5000/api";

async function request(method, path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: "include",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await response.json();
  } catch (err) {
    data = null;
  }

  if (!response.ok) {
    const message = (data && data.error) || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}

const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  put: (path, body) => request("PUT", path, body),
  del: (path) => request("DELETE", path),
};
