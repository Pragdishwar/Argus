import { Play, Database, RotateCcw, Crosshair, Scan, ShieldCheck, Camera, Webhook } from "lucide-react";
import { useState, useRef, useEffect } from "react";

export default function OpsView({ verifications, alerts, manifests, isStreaming, setIsStreaming }: any) {
  const [cameraMode, setCameraMode] = useState<'edge' | 'local'>('edge');
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (cameraMode === 'local' && isStreaming) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        })
        .catch(err => console.error("Camera access denied:", err));
    } else {
      if (videoRef.current?.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach(track => track.stop());
        videoRef.current.srcObject = null;
      }
    }
    
    return () => {
      if (videoRef.current?.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, [cameraMode, isStreaming]);
  
  const handleFastAPIAction = async (action: string) => {
    try {
      await fetch(`/api/simulator/${action}`, { method: 'POST' });
    } catch (e) {
      console.error("Simulator Error:", e);
    }
  };

    const handleCVAction = async (action: string) => {
      try {
        if (cameraMode === 'local') {
          if (!videoRef.current || !canvasRef.current) return;
          const video = videoRef.current;
          const canvas = canvasRef.current;
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          canvas.getContext('2d')?.drawImage(video, 0, 0);
          const base64Image = canvas.toDataURL('image/jpeg');
          
          await fetch(`https://surround-soundtrack-johns-shed.trycloudflare.com/${action}_remote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: base64Image })
          });
        } else {
          await fetch(`https://surround-soundtrack-johns-shed.trycloudflare.com/${action}`, { method: 'POST' });
        }
      } catch (e) {
        console.error("CV Engine Error:", e);
      }
    };

  const pendingCount = 5; // Mock
  const loadedCount = verifications.filter((v: any) => v.disagreement_score === 0).length;
  const blockedCount = verifications.filter((v: any) => v.disagreement_score >= 2).length;
  const manifestCount = pendingCount + loadedCount + blockedCount;

  return (
    <div className="p-6 h-[calc(100vh-80px)] overflow-y-auto">
      <div className="grid grid-cols-12 gap-6 h-full">
        
        {/* LEFT SIDEBAR */}
        <div className="col-span-3 flex flex-col gap-6">
          
          {/* Telemetry */}
          <section>
            <h3 className="text-xs font-bold text-neutral-500 tracking-widest mb-3 uppercase">Telemetry</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4">
                <div className="text-xs text-neutral-500 uppercase tracking-wider mb-2">Manifest</div>
                <div className="text-2xl font-bold text-blue-400">{manifestCount}</div>
              </div>
              <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4">
                <div className="text-xs text-neutral-500 uppercase tracking-wider mb-2">Pending</div>
                <div className="text-2xl font-bold text-yellow-500">{pendingCount}</div>
              </div>
              <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4">
                <div className="text-xs text-neutral-500 uppercase tracking-wider mb-2">Loaded</div>
                <div className="text-2xl font-bold text-green-500">{loadedCount}</div>
              </div>
              <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4">
                <div className="text-xs text-neutral-500 uppercase tracking-wider mb-2">Blocked</div>
                <div className="text-2xl font-bold text-red-500">{blockedCount}</div>
              </div>
            </div>
          </section>

          {/* Latest Verification */}
          <section className="flex-1 min-h-0 flex flex-col">
            <h3 className="text-xs font-bold text-neutral-500 tracking-widest mb-3 uppercase">Latest Verification</h3>
            <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 flex-1 overflow-y-auto">
              {verifications.length === 0 ? (
                <div className="h-full flex items-center justify-center text-neutral-500 text-sm">No verifications yet</div>
              ) : (
                <div className="space-y-3">
                  {verifications.slice(0, 5).map((v: any, idx: number) => (
                    <div key={idx} className="flex justify-between items-center border-b border-neutral-800 pb-2 last:border-0">
                      <span className="font-mono text-sm text-neutral-300">{v.package_id}</span>
                      <div className="flex flex-col items-end">
                        <span className={`text-xs px-2 py-0.5 rounded font-bold ${v.disagreement_score >= 2 ? 'bg-red-500/20 text-red-400' : v.disagreement_score === 1 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}`}>
                          {v.disagreement_score >= 2 ? 'BLOCK' : v.disagreement_score === 1 ? 'WARN' : 'PASS'}
                        </span>
                        {v.disagreement_score >= 2 && (
                          <span className="text-[10px] text-red-400/70 mt-1 uppercase text-right leading-tight max-w-[100px]">
                            {v.zone_status !== 'Correct Gate' ? 'Wrong Gate Detected' :
                             v.fingerprint_status !== 'MATCH' ? 'Fingerprint Mismatch' :
                             v.ocr_status !== 'MATCH' ? 'OCR Mismatch' : 'Verification Failed'}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* Simulator Controls */}
          <section>
            <h3 className="text-xs font-bold text-neutral-500 tracking-widest mb-3 uppercase">Simulator</h3>
            <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 flex flex-col gap-3">
              <div className="flex bg-neutral-950 border border-neutral-800 rounded p-1 mb-2">
                <button 
                  onClick={() => { setCameraMode('edge'); setIsStreaming(false); }}
                  className={`flex-1 py-1 text-xs font-bold rounded flex items-center justify-center gap-1 ${cameraMode === 'edge' ? 'bg-neutral-800 text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
                >
                  <Webhook size={12} /> Edge Cam
                </button>
                <button 
                  onClick={() => { setCameraMode('local'); setIsStreaming(false); }}
                  className={`flex-1 py-1 text-xs font-bold rounded flex items-center justify-center gap-1 ${cameraMode === 'local' ? 'bg-neutral-800 text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
                >
                  <Camera size={12} /> Mobile Cam
                </button>
              </div>
              <button onClick={() => setIsStreaming(!isStreaming)} className={`w-full font-bold py-3 rounded-md flex justify-center items-center gap-2 transition-colors ${isStreaming ? 'bg-red-600 hover:bg-red-500 text-white' : 'bg-blue-600 hover:bg-blue-500 text-white'}`}>
                <Play fill="currentColor" size={16} /> {isStreaming ? "STOP STREAM" : "START STREAM"}
              </button>
              <div className="grid grid-cols-2 gap-3">
                <button onClick={() => handleCVAction('scan')} className="bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-sm py-2 rounded-md flex justify-center items-center gap-2 transition-colors">
                  <Scan size={14} /> Scan
                </button>
                <button onClick={() => handleCVAction('verify')} className="bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-sm py-2 rounded-md flex justify-center items-center gap-2 transition-colors">
                  <ShieldCheck size={14} /> Verify
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <button onClick={() => handleFastAPIAction('seed')} className="bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-sm py-2 rounded-md flex justify-center items-center gap-2 transition-colors">
                  <Database size={14} /> Seed
                </button>
                <button onClick={() => handleFastAPIAction('reset')} className="bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-sm py-2 rounded-md flex justify-center items-center gap-2 transition-colors">
                  <RotateCcw size={14} /> Reset
                </button>
              </div>
            </div>
          </section>

          {/* Alerts Mini */}
          <section className="h-32 flex flex-col">
            <h3 className="text-xs font-bold text-neutral-500 tracking-widest mb-3 uppercase">Alerts ({alerts.length})</h3>
            <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 flex-1 overflow-y-auto">
              {alerts.length === 0 ? (
                <div className="h-full flex items-center justify-center text-neutral-500 text-sm">All clear</div>
              ) : (
                <div className="space-y-2">
                  {alerts.slice(0, 3).map((a: any, idx: number) => (
                    <div key={idx} className="text-xs text-red-400 truncate">{a.message}</div>
                  ))}
                </div>
              )}
            </div>
          </section>

        </div>

        {/* RIGHT AREA */}
        <div className="col-span-9 flex flex-col gap-6">
          
          <div className="grid grid-cols-2 gap-6 h-[400px]">
            {/* Camera Feed */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-lg overflow-hidden relative flex flex-col shadow-inner">
              <div className="p-3 border-b border-neutral-800 flex justify-between items-center bg-neutral-950/50">
                <div className="flex items-center gap-2 text-blue-400 text-xs font-mono font-bold tracking-wider">
                  <Crosshair size={14} /> CAM-07 - GATE
                </div>
              </div>
              <div className="flex-1 relative bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:20px_20px] flex items-center justify-center overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-t from-neutral-900/80 to-transparent pointer-events-none z-10"></div>
                {isStreaming ? (
                  cameraMode === 'edge' ? (
                    <img src="https://surround-soundtrack-johns-shed.trycloudflare.com/video_feed" alt="Live Feed" className="w-full h-full object-cover relative z-0 -scale-x-100" />
                  ) : (
                    <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover relative z-0 -scale-x-100"></video>
                  )
                ) : (
                  <div className="w-64 h-40 border border-yellow-500/50 bg-yellow-500/5 rounded relative flex items-center justify-center animate-pulse shadow-[0_0_15px_rgba(234,179,8,0.1)] z-0">
                    <span className="absolute -top-6 text-yellow-500 text-xs font-mono tracking-widest">AWAITING STREAM</span>
                    <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-yellow-500"></div>
                    <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-yellow-500"></div>
                    <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-yellow-500"></div>
                    <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-yellow-500"></div>
                  </div>
                )}
                <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
              </div>
              <div className="p-2 border-t border-neutral-800 flex justify-between items-center bg-neutral-950/50 text-[10px] font-mono text-neutral-500 relative z-20">
                <span>[ ] OCR active - 1280x720 - {isStreaming ? "30fps" : "0fps"}</span>
                <span>07:42:18</span>
              </div>
            </div>

            {/* Gate Topology Placeholder */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 flex flex-col shadow-inner">
               <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xs font-bold text-neutral-500 tracking-widest uppercase">Gate Topology - LHR-T5</h3>
                    <div className="text-[10px] text-neutral-500 mt-1 font-mono flex gap-3">
                      <span className="text-green-500">✓ approved</span>
                      <span className="text-yellow-500">! warning</span>
                      <span className="text-red-500">✗ blocked</span>
                    </div>
                  </div>
                  <div className="text-xs font-mono bg-neutral-950 border border-neutral-800 px-2 py-1 rounded text-neutral-400 mt-1">
                    <span className="text-white mr-1">{loadedCount}</span> CARGO TRACKED
                  </div>
               </div>
               <div className="flex-1 flex gap-2">
                 {['A07', 'B03', 'B12', 'C04', 'D15'].map((gate, i) => (
                   <div key={gate} className={`flex-1 border rounded-md p-3 flex flex-col ${i === 0 ? 'border-green-500/30 bg-green-500/5' : 'border-neutral-800 bg-neutral-950'}`}>
                     <div className={`text-xs font-mono font-bold ${i === 0 ? 'text-green-400' : 'text-neutral-500'}`}>{gate}</div>
                     <div className="mt-auto space-y-1 text-[10px] font-mono">
                        <div className="flex justify-between text-green-500"><span>✓</span> <span>{i === 0 ? loadedCount : 0}</span></div>
                        <div className="flex justify-between text-yellow-500"><span>!</span> <span>{i === 0 ? (pendingCount > 0 ? 1 : 0) : 0}</span></div>
                        <div className="flex justify-between text-red-500"><span>×</span> <span>{i === 0 ? blockedCount : 0}</span></div>
                     </div>
                   </div>
                 ))}
               </div>
            </div>
          </div>

          {/* Cargo Manifest Table */}
          <section className="flex-1 min-h-0 flex flex-col">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-xs font-bold text-neutral-500 tracking-widest uppercase">Cargo Manifest</h3>
              <div className="text-xs text-neutral-500">{(manifests?.length || 0) + verifications.filter((v: any) => !manifests?.some((m: any) => m.package_id === v.package_id)).length} records</div>
            </div>
            <div className="bg-neutral-900 border border-neutral-800 rounded-lg flex-1 overflow-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-neutral-950 text-neutral-500 sticky top-0 border-b border-neutral-800">
                  <tr>
                    <th className="p-3 font-normal">AWB</th>
                    <th className="p-3 font-normal">FLIGHT</th>
                    <th className="p-3 font-normal">ROUTE</th>
                    <th className="p-3 font-normal">GATE</th>
                    <th className="p-3 font-normal">WEIGHT</th>
                    <th className="p-3 font-normal text-center">OCR</th>
                    <th className="p-3 font-normal text-center">FP</th>
                    <th className="p-3 font-normal text-center">ZONE</th>
                    <th className="p-3 font-normal text-right">STATUS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-800/50">
                  {(!manifests || manifests.length === 0) && verifications.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="p-8 text-center text-neutral-500 italic">Manifest empty — press SEED to load demo cargo.</td>
                    </tr>
                  ) : (
                    <>
                      {/* Render Expected Manifest Records */}
                      {manifests?.map((m: any, idx: number) => {
                        const v = verifications.find((ver: any) => ver.package_id === m.package_id);
                        let statusText = 'PENDING';
                        let statusBadge = 'bg-neutral-800 text-neutral-400';
                        
                        if (v) {
                          if (v.disagreement_score >= 2) {
                            statusText = 'BLOCKED';
                            statusBadge = 'bg-red-950/50 text-red-500 border border-red-900 shadow-[0_0_8px_rgba(239,68,68,0.2)]';
                          } else if (v.disagreement_score === 1) {
                            statusText = 'HOLD';
                            statusBadge = 'bg-yellow-950/50 text-yellow-500 border border-yellow-900';
                          } else {
                            statusText = 'LOADED';
                            statusBadge = 'bg-green-950/50 text-green-500 border border-green-900';
                          }
                        }

                        const gateNum = (m.destination.length % 5) + 1;
                        const gateChar = String.fromCharCode(65 + (m.id % 4)); 
                        const gate = `${gateChar}0${gateNum}`;
                        const weight = (100 + (m.id * 13.5)).toFixed(1);

                        return (
                          <tr key={`m-${idx}`} className="hover:bg-neutral-800/30">
                            <td className="p-3 text-neutral-300 font-bold">{m.package_id}</td>
                            <td className="p-3 text-blue-400">{m.flight_number}</td>
                            <td className="p-3 text-neutral-400">{'->'} {m.destination}</td>
                            <td className="p-3 text-neutral-300">{gate}</td>
                            <td className="p-3 text-neutral-400">{weight} kg</td>
                            <td className="p-3 text-center">
                              {v ? <span className={v.ocr_status === 'MATCH' ? 'text-green-400' : 'text-red-400'}>{v.ocr_status === 'MATCH' ? '✓' : '×'}</span> : <span className="text-neutral-600">-</span>}
                            </td>
                            <td className="p-3 text-center">
                              {v ? <span className={v.fingerprint_status === 'MATCH' ? 'text-green-400' : 'text-red-400'}>{v.fingerprint_status === 'MATCH' ? '✓' : '×'}</span> : <span className="text-neutral-600">-</span>}
                            </td>
                            <td className="p-3 text-center">
                              {v ? <span className={v.zone_status === 'Correct Gate' ? 'text-green-400' : 'text-red-400'}>{v.zone_status === 'Correct Gate' ? '✓' : '×'}</span> : <span className="text-neutral-600">-</span>}
                            </td>
                            <td className="p-3 text-right">
                              <span 
                                className={`px-2 py-1 rounded cursor-help ${statusBadge}`}
                                title={v ? `Vote Breakdown:\nOCR: ${v.ocr_status}\nFingerprint: ${v.fingerprint_status}\nZone: ${v.zone_status}` : 'Pending verification'}
                              >
                                {statusText}
                              </span>
                            </td>
                          </tr>
                        );
                      })}

                      {/* Render Orphan Verifications (Unexpected Scans) */}
                      {verifications
                        .filter((v: any) => !manifests?.some((m: any) => m.package_id === v.package_id))
                        .map((v: any, idx: number) => {
                          let statusText = 'LOADED';
                          let statusBadge = 'bg-green-950/50 text-green-500 border border-green-900';
                          if (v.disagreement_score >= 2) {
                            statusText = 'BLOCKED';
                            statusBadge = 'bg-red-950/50 text-red-500 border border-red-900 shadow-[0_0_8px_rgba(239,68,68,0.2)]';
                          } else if (v.disagreement_score === 1) {
                            statusText = 'HOLD';
                            statusBadge = 'bg-yellow-950/50 text-yellow-500 border border-yellow-900';
                          }

                          return (
                            <tr key={`v-${idx}`} className="hover:bg-neutral-800/30 bg-red-950/10">
                              <td className="p-3 text-red-400 font-bold">{v.package_id}</td>
                              <td className="p-3 text-red-400/50">UNEXPECTED</td>
                              <td className="p-3 text-red-400/50">NO ROUTE</td>
                              <td className="p-3 text-neutral-500">?</td>
                              <td className="p-3 text-neutral-500">?</td>
                              <td className="p-3 text-center">
                                <span className={v.ocr_status === 'MATCH' ? 'text-green-400' : 'text-red-400'}>{v.ocr_status === 'MATCH' ? '✓' : '×'}</span>
                              </td>
                              <td className="p-3 text-center">
                                <span className={v.fingerprint_status === 'MATCH' ? 'text-green-400' : 'text-red-400'}>{v.fingerprint_status === 'MATCH' ? '✓' : '×'}</span>
                              </td>
                              <td className="p-3 text-center">
                                <span className={v.zone_status === 'Correct Gate' ? 'text-green-400' : 'text-red-400'}>{v.zone_status === 'Correct Gate' ? '✓' : '×'}</span>
                              </td>
                              <td className="p-3 text-right">
                                <span 
                                  className={`px-2 py-1 rounded cursor-help ${statusBadge}`}
                                  title={`Vote Breakdown:\nOCR: ${v.ocr_status}\nFingerprint: ${v.fingerprint_status}\nZone: ${v.zone_status}`}
                                >
                                  {statusText}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                    </>
                  )}
                </tbody>
              </table>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
