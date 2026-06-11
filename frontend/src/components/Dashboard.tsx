"use client";

import { useEffect, useState } from "react";
import Navigation from "./Navigation";
import OpsView from "./OpsView";
import AnalyticsView from "./AnalyticsView";
import AuditView from "./AuditView";

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

type Manifest = {
  id: number;
  package_id: string;
  flight_number: string;
  destination: string;
  status: string;
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("OPS");
  const [verifications, setVerifications] = useState<VerificationRecord[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [manifests, setManifests] = useState<Manifest[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  const fetchData = () => {
    fetch('http://127.0.0.1:8000/manifest')
      .then(res => res.json())
      .then(data => setManifests(data))
      .catch(e => console.error(e));

    fetch('http://127.0.0.1:8000/verifications')
      .then(res => res.json())
      .then(data => setVerifications(data.reverse().slice(0, 50)))
      .catch(e => console.error(e));

    fetch('http://127.0.0.1:8000/alerts')
      .then(res => res.json())
      .then(data => setAlerts(data.slice(0, 20)))
      .catch(e => console.error(e));
  };

  useEffect(() => {
    // Initial fetch
    fetchData();

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
      } else if (payload.event === "simulator_reset") {
        setVerifications([]);
        setAlerts([]);
        setManifests([]);
      } else if (payload.event === "simulator_seeded") {
        fetchData();
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 text-white font-sans overflow-hidden">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} isConnected={isConnected} />
      
      <main>
        {activeTab === "OPS" && <OpsView verifications={verifications} alerts={alerts} manifests={manifests} isStreaming={isStreaming} setIsStreaming={setIsStreaming} />}
        {activeTab === "ANALYTICS" && <AnalyticsView verifications={verifications} />}
        {activeTab === "AUDIT" && <AuditView />}
      </main>
    </div>
  );
}
