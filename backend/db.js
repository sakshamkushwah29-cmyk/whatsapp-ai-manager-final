require('dotenv').config({ path: '../.env' });
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.warn("SUPABASE_URL or SUPABASE_KEY not found in env. Falling back to in-memory (data will be lost on restart).");
}

const supabase = createClient(supabaseUrl || 'https://placeholder.supabase.co', supabaseKey || 'placeholder');

module.exports = {
  upsertLead: async (phone) => {
    const { data, error } = await supabase
      .from('leads')
      .upsert({ phone, last_message_at: new Date().toISOString() }, { onConflict: 'phone' })
      .select();
    
    // Increment message count manually if needed or via RPC
    const { data: lead } = await supabase.from('leads').select('message_count').eq('phone', phone).single();
    await supabase.from('leads').update({ message_count: (lead?.message_count || 0) + 1 }).eq('phone', phone);
  },
  saveMessage: async (phone, role, content) => {
    await supabase.from('messages').insert({ phone, role, content });
  },
  getConversation: async (phone, limit = 20) => {
    const { data } = await supabase
      .from('messages')
      .select('*')
      .eq('phone', phone)
      .order('timestamp', { ascending: true })
      .limit(limit);
    return data || [];
  },
  getAllLeads: async () => {
    const { data } = await supabase
      .from('leads')
      .select('*')
      .order('last_message_at', { ascending: false });
    return data || [];
  },
  updateLeadStatus: async (phone, status) => {
    await supabase.from('leads').update({ status }).eq('phone', phone);
  },
  updateLeadName: async (phone, name) => {
    await supabase.from('leads').update({ name }).eq('phone', phone);
  }
};
