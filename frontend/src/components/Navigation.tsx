import { Activity, LayoutDashboard, ScrollText, CheckCircle2 } from "lucide-react";
import { useEffect, useState } from "react";

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isConnected: boolean;
  blockedCount: number;
}

export default function Navigation({ activeTab, setActiveTab, isConnected, blockedCount }: NavigationProps) {
  const [time, setTime] = useState("");

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setTime(now.toISOString().substring(11, 19));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const tabs = [
    { id: "OPS", icon: <Activity size={18} />, label: "OPS" },
    { id: "ANALYTICS", icon: <LayoutDashboard size={18} />, label: "ANALYTICS" },
    { id: "AUDIT", icon: <ScrollText size={18} />, label: "AUDIT LOG" },
  ];

  return (
    <header className="flex justify-between items-center bg-neutral-950 border-b border-neutral-800 p-4 sticky top-0 z-50">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-3">
          <div className="bg-neutral-900 border border-neutral-700 p-2 rounded-lg">
            <Activity className="text-blue-500" size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white leading-tight">ARGUS</h1>
            <p className="text-[10px] uppercase tracking-widest text-neutral-400">Cargo Surveillance <span className="mx-1">•</span> V1.0</p>
          </div>
        </div>

        <nav className="flex gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? "bg-neutral-800 text-white shadow-inner border border-neutral-700"
                  : "text-neutral-500 hover:text-neutral-300 hover:bg-neutral-900"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 bg-neutral-900 border border-neutral-800 px-3 py-1.5 rounded-full">
          <div className={`h-2.5 w-2.5 rounded-full ${!isConnected ? "bg-red-500" : blockedCount > 0 ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)] animate-pulse" : "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse"}`}></div>
          <span className="text-xs font-mono text-neutral-400">
            SYS <span className={!isConnected ? "text-red-400 font-bold" : blockedCount > 0 ? "text-red-500 font-bold" : "text-green-400 font-bold"}>
              {!isConnected ? "OFFLINE" : blockedCount > 0 ? "ALERT" : "NOMINAL"}
            </span>
          </span>
        </div>
        <div className="text-xs font-mono text-neutral-400 border border-neutral-800 bg-neutral-900 px-3 py-1.5 rounded-md">
          UTC <span className="text-white ml-1">{time || "00:00:00"}</span>
        </div>
      </div>
    </header>
  );
}
