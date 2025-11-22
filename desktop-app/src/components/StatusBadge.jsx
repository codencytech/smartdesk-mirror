import React from "react";

export default function StatusBadge({ statusText }) {
  const online = /running|online/i.test(statusText);
  return (
    <div className={`status-badge ${online ? "online" : "offline"}`}>
      <div className="pulse" />
      <div className="text">{statusText}</div>
    </div>
  );
}
