import { Search } from "lucide-react";
import { useState } from "react";

export default function AuditView({ logs = [] }: { logs?: any[] }) {
  const [searchTerm, setSearchTerm] = useState("");
  
  const filteredLogs = logs.filter(log => 
    log.package_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.action?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 h-[calc(100vh-80px)] overflow-y-auto">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="text-lg font-bold text-white tracking-widest uppercase mb-1">Audit Trail</h2>
          <p className="text-xs font-mono text-neutral-500">Immutable event log <span className="text-neutral-700 mx-2">•</span> {logs.length} entries</p>
        </div>
        
        <div className="relative w-96">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-neutral-500">
            <Search size={16} />
          </div>
          <input 
            type="text" 
            placeholder="Filter by AWB, event, actor..." 
            className="w-full bg-neutral-900 border border-neutral-800 text-neutral-300 text-sm rounded-lg block pl-10 p-2.5 focus:ring-blue-500 focus:border-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="bg-neutral-900 border border-neutral-800 rounded-lg overflow-hidden shadow-inner">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-neutral-950 text-neutral-500 border-b border-neutral-800">
            <tr>
              <th className="p-4 font-normal w-48">TIMESTAMP (UTC)</th>
              <th className="p-4 font-normal w-32">EVENT</th>
              <th className="p-4 font-normal w-32">AWB</th>
              <th className="p-4 font-normal w-32">ACTOR</th>
              <th className="p-4 font-normal">PAYLOAD</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-800/50">
            {filteredLogs.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-12 text-center text-neutral-500 italic">No audit entries.</td>
              </tr>
            ) : (
              filteredLogs.map((log, idx) => (
                <tr key={idx} className="hover:bg-neutral-800/30">
                  <td className="p-4 text-neutral-400">{new Date(log.timestamp).toLocaleString()}</td>
                  <td className="p-4 text-blue-400">{log.action}</td>
                  <td className="p-4 text-white font-bold">{log.package_id}</td>
                  <td className="p-4 text-neutral-400">SYSTEM</td>
                  <td className="p-4 text-neutral-500 truncate max-w-md">{log.result}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
