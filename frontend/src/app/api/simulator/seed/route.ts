import { NextResponse } from 'next/server';
import { supabase } from '../../../lib/supabase';

export async function POST() {
  const mockManifests = [
    { package_id: "PKG-001", flight_number: "BA011", destination: "JFK", status: "Pending" },
    { package_id: "PKG-002", flight_number: "AF112", destination: "CDG", status: "Pending" },
    { package_id: "PKG-003", flight_number: "LH400", destination: "FRA", status: "Pending" },
    { package_id: "PKG-004", flight_number: "EK002", destination: "DXB", status: "Pending" },
    { package_id: "PKG-005", flight_number: "QF009", destination: "MEL", status: "Pending" }
  ];

  await supabase.from('manifests').insert(mockManifests);

  for (let i = 0; i < 5; i++) {
    const pkg = mockManifests[i].package_id;
    const disagreementScore = i < 3 ? 0 : (i === 3 ? 2 : 1);
    const action = disagreementScore >= 2 ? "System BLOCK" : "System HOLD";

    const v = {
      package_id: pkg,
      ocr_status: i !== 3 ? "MATCH" : "MISMATCH",
      fingerprint_status: i !== 4 ? "MATCH" : "MISMATCH",
      zone_status: i < 3 ? "Correct Gate" : "Wrong Gate",
      disagreement_score: disagreementScore
    };
    
    await supabase.from('verification_records').insert([v]);

    if (disagreementScore > 0) {
      await supabase.from('audit_logs').insert([{
        package_id: pkg,
        action: action,
        result: `OCR: ${v.ocr_status}, FP: ${v.fingerprint_status}, Zone: ${v.zone_status}`,
        severity: action === "System BLOCK" ? "HIGH" : "MEDIUM"
      }]);
    }
  }

  return NextResponse.json({ success: true });
}
