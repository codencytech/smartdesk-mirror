import React, { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import StatusBadge from "./components/StatusBadge";
import ConnectionPanel from "./components/ConnectionPanel";
import { checkPcAgentStatus, fetchSystemMetrics, getPendingRequests, respondToConnection } from "./api";

export default function App() {
  const [status, setStatus] = useState("Checking...");
  const [metrics, setMetrics] = useState({
    cpu: "--",
    ram: "--", 
    net: "--"
  });
  const [pendingConnections, setPendingConnections] = useState([]);
  const [activeConnections, setActiveConnections] = useState([]);

  // Poll for connection requests and system metrics
  useEffect(() => {
    let mounted = true;

    async function checkStatus() {
      const s = await checkPcAgentStatus();
      if (mounted) setStatus(s);
    }

    async function checkMetrics() {
      const m = await fetchSystemMetrics();
      if (mounted && m) {
        setMetrics({
          cpu: m.cpu || "--",
          ram: m.ram || "--",
          net: m.net || "--"
        });
      }
    }

    async function checkConnectionRequests() {
      try {
        const requests = await getPendingRequests();
        if (mounted) {
          setPendingConnections(requests);
        }
      } catch (error) {
        console.error('Failed to fetch connection requests:', error);
      }
    }

    async function checkAll() {
      await checkStatus();
      await checkMetrics();
      await checkConnectionRequests();
    }

    checkAll();
    const t = setInterval(checkAll, 2000); // Check every 2 seconds
    
    return () => {
      mounted = false;
      clearInterval(t);
    };
  }, []);

  // Handle connection response
  const handleConnectionResponse = async (requestId, accepted) => {
    try {
      const result = await respondToConnection(requestId, accepted);
      if (result.success) {
        // Remove from pending requests
        setPendingConnections(prev => prev.filter(req => req.id !== requestId));
        
        if (accepted) {
          // Add to active connections
          const acceptedRequest = pendingConnections.find(req => req.id === requestId);
          if (acceptedRequest) {
            setActiveConnections(prev => [...prev, {
              id: Date.now(),
              deviceInfo: acceptedRequest.device_info,
              connectedAt: new Date(),
              code: acceptedRequest.code
            }]);
          }
        }
      }
    } catch (error) {
      console.error('Failed to respond to connection:', error);
    }
  };

  return (
    <div className="app-root">
      <Sidebar />
      <div className="main-area">
        <Header />
        <div className="content">
          <div className="left-panel">
            <ConnectionPanel />
            
            <div className="card hero-card">
              <h2 className="title">Welcome to SmartDesk Mirror</h2>
              <p className="subtitle">Control & monitor your PC with secure on-device AI.</p>
              <div className="status-row">
                <StatusBadge statusText={status} />
                <div className="metrics">
                  <div className="metric">
                    <div className="m-val">{metrics.cpu}</div>
                    <div className="m-label">CPU</div>
                  </div>
                  <div className="metric">
                    <div className="m-val">{metrics.ram}</div>
                    <div className="m-label">RAM</div>
                  </div>
                  <div className="metric">
                    <div className="m-val">{metrics.net}</div>
                    <div className="m-label">NET</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="card placeholder-card">
              <h3>Active Connections</h3>
              <div className="connections-list">
                {activeConnections.length === 0 ? (
                  <p className="no-connections">No active connections</p>
                ) : (
                  activeConnections.map(conn => (
                    <div key={conn.id} className="connection-item">
                      <div className="conn-device">{conn.deviceInfo}</div>
                      <div className="conn-status">
                        <span className="status-dot active"></span>
                        Connected since {conn.connectedAt.toLocaleTimeString()}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="right-panel">
            <div className="card preview-card">
              <div className="preview-header">
                <span>Live Preview</span>
                <span className="dot">●</span>
              </div>
              <div className="preview-area">
                <div className="preview-placeholder">
                  {activeConnections.length > 0 
                    ? "Screen sharing active with mobile device" 
                    : "Waiting for mobile connection"
                  }
                </div>
              </div>
            </div>

            <div className="card chat-card">
              <h4>Connection Status</h4>
              <div className="connection-stats">
                <div className="stat">
                  <div className="stat-value">{activeConnections.length}</div>
                  <div className="stat-label">Active</div>
                </div>
                <div className="stat">
                  <div className="stat-value">{pendingConnections.length}</div>
                  <div className="stat-label">Pending</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <footer className="app-footer">
          <div>SmartDesk Mirror • Secure Connection System • Built for Arm</div>
        </footer>
      </div>

      {/* Connection Request Dialogs */}
      {pendingConnections.map(request => (
        <ConnectionRequestDialog
          key={request.id}
          request={request}
          onResponse={handleConnectionResponse}
        />
      ))}
    </div>
  );
}

// Connection Request Dialog Component
function ConnectionRequestDialog({ request, onResponse }) {
  const getDeviceType = (deviceInfo) => {
    if (deviceInfo.includes('Android')) return 'Android Phone';
    if (deviceInfo.includes('iPhone')) return 'iPhone';
    if (deviceInfo.includes('iPad')) return 'iPad';
    return 'Mobile Device';
  };

  const getDeviceIcon = (deviceInfo) => {
    if (deviceInfo.includes('Android')) return '📱';
    if (deviceInfo.includes('iPhone') || deviceInfo.includes('iPad')) return '📱';
    return '📱';
  };

  return (
    <div className="dialog-overlay">
      <div className="connection-dialog">
        <div className="dialog-header">
          <h3>🔐 Connection Request</h3>
        </div>
        <div className="dialog-content">
          <div className="device-info">
            <strong>{getDeviceIcon(request.device_info)} Device:</strong> {getDeviceType(request.device_info)}
          </div>
          <div className="device-details">
            <strong>📱 Name:</strong> {request.device_info}
          </div>
          <div className="request-time">
            <strong>🕒 Time:</strong> {new Date(request.timestamp * 1000).toLocaleTimeString()}
          </div>
          <div className="connection-code">
            <strong>🔑 Code:</strong> {request.code}
          </div>
          <div className="security-notice">
            <p>This device wants to access your PC screen and controls.</p>
            <p className="security-warning">⚠️ Only accept connections from trusted devices</p>
          </div>
        </div>
        <div className="dialog-actions">
          <button 
            className="btn decline"
            onClick={() => onResponse(request.id, false)}
          >
            ❌ Decline
          </button>
          <button 
            className="btn accept"
            onClick={() => onResponse(request.id, true)}
          >
            ✅ Accept & Connect
          </button>
        </div>
      </div>
    </div>
  );
}