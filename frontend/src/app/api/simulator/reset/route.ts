import { NextResponse } from 'next/server';
import { supabase } from '../../../../lib/supabase';

export async function POST() {
  await supabase.from('manifests').delete().neq('id', 0);
  await supabase.from('verification_records').delete().neq('id', 0);
  await supabase.from('alerts').delete().neq('id', 0);
  await supabase.from('audit_logs').delete().neq('id', 0);

  return NextResponse.json({ success: true });
}
