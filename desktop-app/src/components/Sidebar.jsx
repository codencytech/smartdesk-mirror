import React from "react";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="logo">
        <div className="logo-icon">SM</div>
        <div className="logo-text">SmartDesk</div>
      </div>

      <nav className="nav">
        <button className="nav-item active">Dashboard</button>
        <button className="nav-item">Screen</button>
        <button className="nav-item">Chat</button>
        <button className="nav-item">Settings</button>
      </nav>

      <div className="version">v1.0 • Beta</div>
    </aside>
  );
}
