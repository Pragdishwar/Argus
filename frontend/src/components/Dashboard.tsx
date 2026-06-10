"use client";

import { useEffect, useState } from "react";

type VerificationRecord = {
  id: number;
  package_id: string;
  disagreement_score: number;
  ocr_status: string;
  fingerprint_status: string;
  zone_status: string;
};

type Alert = {
  id: number;
  type: string;
  severity: string;
  message: string;
  timestamp: string;
};

export default function Dashboard() {
  const [verifications, setVerifications] = useState<VerificationRecord[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Connect to FastAPI WebSocket
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/live");

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.event === "new_verification") {
        setVerifications((prev) => [payload.data, ...prev].slice(0, 50));
      } else if (payload.event === "new_alert") {
        setAlerts((prev) => [payload.data, ...prev].slice(0, 20));
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-8 font-sans">
      <header className="flex justify-between items-center mb-8 border-b border-neutral-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
            <span className="text-blue-500">ARGUS</span> System Dashboard
          </h1>
          <p className="text-neutral-400 mt-1">Autonomous Real-time Gate & Cargo Unified Surveillance</p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`h-3 w-3 rounded-full ${isConnected ? "bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.6)]" : "bg-red-500"}`}></div>
          <span className="text-sm font-medium text-neutral-300">{isConnected ? "Live Connection Active" : "Disconnected"}</span>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Stats & Alerts */}
        <div className="flex flex-col gap-8">
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-2xl">
            <h2 className="text-xl font-semibold mb-4 text-neutral-100">System Status</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-neutral-950 rounded-lg p-4 border border-neutral-800">
                <p className="text-sm text-neutral-400 mb-1">Total Scans</p>
                <p className="text-3xl font-bold text-white">{verifications.length}</p>
              </div>
              <div className="bg-neutral-950 rounded-lg p-4 border border-neutral-800">
                <p className="text-sm text-neutral-400 mb-1">Active Alerts</p>
                <p className="text-3xl font-bold text-red-400">{alerts.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-2xl flex-grow">
            <h2 className="text-xl font-semibold mb-4 text-neutral-100 flex items-center gap-2">
              <span className="text-red-500">●</span> Alert Stream
            </h2>
            <div className="flex flex-col gap-3 overflow-y-auto max-h-[400px] pr-2">
              {alerts.length === 0 ? (
                <p className="text-neutral-500 text-sm italic">No recent alerts.</p>
              ) : (
                alerts.map((alert, idx) => (
                  <div key={idx} className={`p-4 rounded-lg border border-neutral-800 border-l-4 ${
                    alert.severity === 'critical' ? 'border-l-red-600 bg-red-950/20' : 
                    alert.severity === 'high' ? 'border-l-orange-500 bg-orange-950/20' : 
                    'border-l-yellow-500 bg-yellow-950/20'
                  }`}>
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-bold text-sm uppercase tracking-wider">{alert.type}</span>
                      <span className="text-xs text-neutral-500">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p className="text-sm text-neutral-300">{alert.message}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Live Verification Feed */}
        <div className="lg:col-span-2 bg-neutral-900 border border-neutral-800 rounded-xl p-6 shadow-2xl">
          <h2 className="text-xl font-semibold mb-6 text-neutral-100 flex items-center justify-between">
            Live Verification Feed
            <span className="text-xs font-normal text-neutral-400 bg-neutral-800 px-3 py-1 rounded-full">Auto-updating</span>
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-950 text-neutral-400 uppercase text-xs tracking-wider">
                <tr>
                  <th className="p-4 rounded-tl-lg">Package ID</th>
                  <th className="p-4">OCR Check</th>
                  <th className="p-4">Fingerprint</th>
                  <th className="p-4">Zone Track</th>
                  <th className="p-4 rounded-tr-lg">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-800">
                {verifications.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-neutral-500 italic">Waiting for initial scan data...</td>
                  </tr>
                ) : (
                  verifications.map((v, idx) => (
                    <tr key={idx} className="hover:bg-neutral-800/50 transition-colors">
                      <td className="p-4 font-medium text-white">{v.package_id}</td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${v.ocr_status === 'MATCH' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                          {v.ocr_status}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${v.fingerprint_status === 'MATCH' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                          {v.fingerprint_status}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${v.zone_status === 'Correct Gate' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                          {v.zone_status}
                        </span>
                      </td>
                      <td className="p-4">
                        {v.disagreement_score >= 2 ? (
                          <span className="px-3 py-1 rounded bg-red-600 text-white text-xs font-bold shadow-[0_0_10px_rgba(220,38,38,0.5)]">HALT LOAD</span>
                        ) : v.disagreement_score === 1 ? (
                          <span className="px-3 py-1 rounded bg-yellow-600 text-white text-xs font-bold">WARN</span>
                        ) : (
                          <span className="px-3 py-1 rounded bg-green-600 text-white text-xs font-bold">APPROVE</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
