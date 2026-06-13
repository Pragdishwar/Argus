"use client";

import { useEffect, useState } from "react";
import Navigation from "./Navigation";
import OpsView from "./OpsView";
import AnalyticsView from "./AnalyticsView";
import AuditView from "./AuditView";
import { supabase } from "../lib/supabase";

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
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  const fetchData = async () => {
    try {
      const { data: manifestData } = await supabase.from('manifests').select('*').order('id', { ascending: true });
      if (manifestData) setManifests(manifestData);

      const { data: verifData } = await supabase.from('verification_records').select('*').order('id', { ascending: false }).limit(50);
      if (verifData) setVerifications(verifData);

      const { data: alertData } = await supabase.from('alerts').select('*').order('timestamp', { ascending: false }).limit(20);
      if (alertData) setAlerts(alertData);

      const { data: auditData } = await supabase.from('audit_logs').select('*').order('timestamp', { ascending: false }).limit(50);
      if (auditData) setAuditLogs(auditData);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Connect to Supabase Realtime
    const channel = supabase.channel('schema-db-changes')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'verification_records' }, (payload) => {
        setVerifications((prev) => [payload.new as VerificationRecord, ...prev].slice(0, 50));
      })
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'alerts' }, (payload) => {
        setAlerts((prev) => [payload.new as Alert, ...prev].slice(0, 20));
      })
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'audit_logs' }, (payload) => {
        setAuditLogs((prev) => [payload.new, ...prev].slice(0, 50));
      })
      .on('postgres_changes', { event: '*', schema: 'public', table: 'manifests' }, () => {
        fetchData(); // Refetch manifests to keep order and handle deletes
      })
      .on('postgres_changes', { event: 'DELETE', schema: 'public', table: 'verification_records' }, () => {
        fetchData(); // Refetch all if simulator resets
      })
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') setIsConnected(true);
        if (status === 'CLOSED' || status === 'CHANNEL_ERROR') setIsConnected(false);
      });

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  const blockedCount = verifications.filter((v: any) => v.disagreement_score >= 2).length;

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-300 font-sans flex flex-col">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} isConnected={isConnected} blockedCount={blockedCount} />
      
      <main>
        {activeTab === "OPS" && <OpsView verifications={verifications} alerts={alerts} manifests={manifests} isStreaming={isStreaming} setIsStreaming={setIsStreaming} />}
        {activeTab === "ANALYTICS" && <AnalyticsView verifications={verifications} />}
        {activeTab === "AUDIT" && <AuditView logs={auditLogs} />}
      </main>
    </div>
  );
}
