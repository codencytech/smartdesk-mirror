export const API_BASE = "http://localhost:8000";

// For desktop app internal use - no authentication needed
export async function checkPcAgentStatus() {
  try {
    const res = await fetch(`${API_BASE}/`);
    if (!res.ok) return "PC Agent Offline";
    const data = await res.json();
    return data.status || "PC Agent Running";
  } catch (err) {
    return "PC Agent Offline";
  }
}

// For desktop app internal use - no authentication needed
export async function fetchSystemMetrics() {
  try {
    const res = await fetch(`${API_BASE}/system-metrics`);
    if (!res.ok) return null;
    const data = await res.json();
    return data;
  } catch (err) {
    return null;
  }
}

// For connection code generation (desktop app)
export async function generateConnectionCode() {
  try {
    const res = await fetch(`${API_BASE}/connection/generate-code`);
    if (!res.ok) {
      console.error('Failed to generate code:', res.status);
      return null;
    }
    return await res.json();
  } catch (err) {
    console.error('Failed to generate connection code:', err);
    return null;
  }
}

// For getting pending connection requests (desktop app)
export async function getPendingRequests() {
  try {
    const res = await fetch(`${API_BASE}/connection/pending-requests`);
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error('Failed to get pending requests:', err);
    return [];
  }
}

// For responding to connection requests (desktop app)
export async function respondToConnection(requestId, accepted) {
  try {
    const res = await fetch(`${API_BASE}/connection/respond`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request_id: requestId,
        accepted: accepted
      })
    });
    return await res.json();
  } catch (err) {
    console.error('Failed to respond to connection:', err);
    return { success: false };
  }
}

// For getting active connections (desktop app)
export async function getActiveConnections() {
  try {
    const res = await fetch(`${API_BASE}/connection/active`);
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error('Failed to get active connections:', err);
    return [];
  }
}