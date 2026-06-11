import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

export default function AnalyticsView({ verifications }: any) {
  
  const total = verifications.length;
  const passed = verifications.filter((v:any) => v.disagreement_score === 0).length;
  const held = verifications.filter((v:any) => v.disagreement_score === 1).length;
  const blocked = verifications.filter((v:any) => v.disagreement_score >= 2).length;

  const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
  const holdRate = total > 0 ? Math.round((held / total) * 100) : 0;
  const blockRate = total > 0 ? Math.round((blocked / total) * 100) : 0;

  // Mock data for charts
  const lineData = Array.from({length: 30}).map((_, i) => ({ name: i, score: Math.random() > 0.8 ? (Math.random() > 0.5 ? 2 : 1) : 0 }));
  const pieData = [
    { name: 'PASS', value: passed || 1, color: '#22c55e' },
    { name: 'HOLD', value: held || 0, color: '#eab308' },
    { name: 'BLOCK', value: blocked || 0, color: '#ef4444' }
  ];
  const barData = [
    { name: 'OCR FAIL', count: verifications.filter((v:any) => v.ocr_status !== 'MATCH').length || 0 },
    { name: 'FPRINT FAIL', count: verifications.filter((v:any) => v.fingerprint_status !== 'MATCH').length || 0 },
    { name: 'ZONE FAIL', count: verifications.filter((v:any) => v.zone_status !== 'Correct Gate').length || 0 },
  ];

  return (
    <div className="p-6 h-[calc(100vh-80px)] overflow-y-auto">
      <div className="grid grid-cols-12 gap-6">
        
        {/* Top KPIs */}
        <div className="col-span-3 bg-neutral-900 border border-neutral-800 rounded-lg p-5 flex flex-col shadow-inner">
          <span className="text-xs text-neutral-500 font-bold tracking-widest uppercase mb-2">Verifications</span>
          <span className="text-4xl font-bold text-blue-500">{total}</span>
        </div>
        <div className="col-span-3 bg-neutral-900 border border-neutral-800 rounded-lg p-5 flex flex-col shadow-inner">
          <span className="text-xs text-neutral-500 font-bold tracking-widest uppercase mb-2">Pass Rate</span>
          <span className="text-4xl font-bold text-green-500">{passRate}%</span>
        </div>
        <div className="col-span-3 bg-neutral-900 border border-neutral-800 rounded-lg p-5 flex flex-col shadow-inner">
          <span className="text-xs text-neutral-500 font-bold tracking-widest uppercase mb-2">Hold Rate</span>
          <span className="text-4xl font-bold text-yellow-500">{holdRate}%</span>
        </div>
        <div className="col-span-3 bg-neutral-900 border border-neutral-800 rounded-lg p-5 flex flex-col shadow-inner">
          <span className="text-xs text-neutral-500 font-bold tracking-widest uppercase mb-2">Block Rate</span>
          <span className="text-4xl font-bold text-red-500">{blockRate}%</span>
        </div>

        {/* Charts Middle Row */}
        <div className="col-span-6 bg-neutral-900 border border-neutral-800 rounded-lg p-5 h-[300px] shadow-inner flex flex-col">
          <span className="text-xs text-neutral-500 font-bold tracking-widest uppercase mb-4">Redundancy Score - Last 30</span>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                <XAxis dataKey="name" hide />
                <YAxis domain={[0, 3]} ticks={[0, 1, 2, 3]} stroke="#525252" fontSize={12} tickFormatter={(val) => val === 0 ? "0 (PASS)" : val === 1 ? "1 (WARN)" : "2+ (HALT)"} width={80} />
                <Tooltip contentStyle={{backgroundColor: '#171717', borderColor: '#262626'}} />
                <Line type="stepAfter" dataKey="score" stroke="#3b82f6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="col-span-6 bg-neutral-900 border border-neutral-800 rounded-lg p-5 h-[300px] shadow-inner flex flex-col">
          <span className="text-xs text-neutral-500 font-bold tracking-widest uppercase mb-4">Decision Distribution</span>
          <div className="flex-1 w-full">
            {total === 0 ? (
              <div className="h-full flex items-center justify-center text-neutral-600 italic">No data available</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value">
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{backgroundColor: '#171717', borderColor: '#262626', color: '#fff'}} itemStyle={{color: '#fff'}} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="flex justify-center gap-6 mt-2 text-xs font-mono">
            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-green-500"></span> PASS</div>
            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-yellow-500"></span> HOLD</div>
            <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500"></span> BLOCK</div>
          </div>
        </div>

        {/* Chart Bottom Row */}
        <div className="col-span-12 bg-neutral-900 border border-neutral-800 rounded-lg p-5 h-[250px] shadow-inner flex flex-col">
          <span className="text-xs text-neutral-500 font-bold tracking-widest uppercase mb-4">Failure Breakdown</span>
          <div className="flex-1 w-full">
             <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" horizontal={false} />
                <XAxis type="number" stroke="#525252" fontSize={12} allowDecimals={false} />
                <YAxis type="category" dataKey="name" stroke="#a3a3a3" fontSize={10} width={80} />
                <Tooltip cursor={{fill: '#171717'}} contentStyle={{backgroundColor: '#171717', borderColor: '#262626'}} />
                <Bar dataKey="count" fill="#ef4444" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
