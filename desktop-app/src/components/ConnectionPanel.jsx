import React, { useState, useEffect } from 'react';
import { generateConnectionCode } from '../api';

export default function ConnectionPanel({ onConnectionRequest }) {
  const [connectionCode, setConnectionCode] = useState(null);
  const [qrCode, setQrCode] = useState(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pcIp, setPcIp] = useState('Detecting...');

  // Function to detect local IP
  const detectLocalIP = async () => {
    try {
      // Try to get IP from the server
      const response = await fetch('http://localhost:8000/debug/local-ip');
      const data = await response.json();
      if (data.ip && data.ip !== '127.0.0.1') {
        setPcIp(data.ip);
        return;
      }
    } catch (error) {
      console.log('Could not get IP from server, using fallback');
    }

    // Fallback: Try WebRTC to get local IP
    try {
      const peerConnection = new RTCPeerConnection({ iceServers: [] });
      peerConnection.createDataChannel('');
      peerConnection.createOffer()
        .then(offer => peerConnection.setLocalDescription(offer))
        .catch(() => {});

      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          const ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;
          const ipMatch = event.candidate.candidate.match(ipRegex);
          if (ipMatch) {
            setPcIp(ipMatch[1]);
            peerConnection.close();
          }
        }
      };

      // Timeout fallback
      setTimeout(() => {
        if (pcIp === 'Detecting...') {
          setPcIp('192.168.1.100'); // Common default
        }
        peerConnection.close();
      }, 1000);
    } catch (error) {
      setPcIp('192.168.1.100'); // Final fallback
    }
  };

  const generateNewCode = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await generateConnectionCode();
      
      if (data) {
        setConnectionCode(data.code);
        setQrCode(data.qr_code);
        setTimeLeft(data.valid_for_minutes * 60);
        console.log('✅ Generated new connection code:', data.code);
        
        // Detect IP when generating new code
        detectLocalIP();
      } else {
        setError('Failed to generate connection code');
      }
    } catch (error) {
      console.error('❌ Failed to generate code:', error);
      // Fallback: generate random code locally
      const fallbackCode = Math.floor(100000 + Math.random() * 900000).toString();
      setConnectionCode(fallbackCode);
      setTimeLeft(600);
      detectLocalIP(); // Still try to detect IP
      setError('Using offline mode - check connection');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    generateNewCode();
    
    // Refresh code every 9 minutes (before expiration)
    const interval = setInterval(() => {
      generateNewCode();
    }, 9 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Countdown timer
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && connectionCode) {
      generateNewCode();
    }
  }, [timeLeft]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // Show temporary success message
      const originalText = pcIp;
      setPcIp('✅ Copied!');
      setTimeout(() => setPcIp(originalText), 2000);
    });
  };

  if (isLoading) {
    return (
      <div className="connection-panel">
        <div className="card">
          <h3>Connect Mobile Device</h3>
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Generating connection code...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="connection-panel">
        <div className="card">
          <h3>Connect Mobile Device</h3>
          <div className="error-state">
            <p>❌ {error}</p>
            <button className="btn" onClick={generateNewCode}>
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!connectionCode) {
    return (
      <div className="connection-panel">
        <div className="card">
          <h3>Connect Mobile Device</h3>
          <p>Failed to load connection code</p>
          <button className="btn" onClick={generateNewCode}>
            Generate Code
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="connection-panel">
      <div className="card">
        <h3>Connect Mobile Device</h3>
        <p>Share these details with your mobile app:</p>
        
        {/* IP Address Display */}
        <div className="ip-display" onClick={() => copyToClipboard(pcIp)} style={{cursor: 'pointer'}}>
          <div className="label">Your PC IP Address (Click to copy)</div>
          <div className="value">{pcIp}</div>
        </div>
        
        <div className="connection-info">
          <div className="info-item">
            <span className="info-label">Connection Code:</span>
            <span className="info-value connection-code-small">{connectionCode}</span>
          </div>
        </div>
        
        <div className="time-remaining">
          Code expires in: {formatTime(timeLeft)}
        </div>

        <div className="qr-code">
          {qrCode ? (
            <img src={qrCode} alt="QR Code for connection" />
          ) : (
            <div className="qr-placeholder">
              <div className="qr-fallback">
                <div className="fallback-code">{connectionCode}</div>
                <p>Enter this code manually</p>
              </div>
            </div>
          )}
          <p>Scan QR code or enter code manually</p>
        </div>

        <div className="connection-help">
          <p><strong>Mobile setup instructions:</strong></p>
          <ol>
            <li>Open SmartDesk Mirror mobile app</li>
            <li>Enter the IP address shown above</li>
            <li>Enter the 6-digit connection code</li>
            <li>Click Connect and wait for approval</li>
          </ol>
        </div>

        <button className="btn ghost" onClick={generateNewCode}>
          Generate New Code
        </button>
      </div>
    </div>
  );
}