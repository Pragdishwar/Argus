import { NextResponse } from 'next/server';
import { supabase } from '../../../../lib/supabase';

export async function POST() {
  await supabase.from('manifests').delete().not('package_id', 'is', null);
  await supabase.from('verification_records').delete().not('package_id', 'is', null);
  await supabase.from('alerts').delete().not('id', 'is', null);
  await supabase.from('audit_logs').delete().not('id', 'is', null);

  return NextResponse.json({ success: true });
}
