import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { formatDistanceToNow } from 'date-fns';
import { 
  Users, MessageSquare, CheckCircle, 
  Settings, LayoutDashboard, Share2, 
  Send, Phone, Search, ExternalLink,
  Loader2, Check, AlertCircle, Upload
} from 'lucide-react';

const API_BASE = 'http://localhost:3001';

// --- COMPONENTS ---

const StatusBadge = ({ status }) => {
  const styles = {
    new: 'bg-blue-900/40 text-blue-400 border-blue-500/30',
    engaged: 'bg-yellow-900/40 text-yellow-400 border-yellow-500/30',
    brochure_sent: 'bg-purple-900/40 text-purple-400 border-purple-500/30',
    cta_sent: 'bg-orange-900/40 text-orange-400 border-orange-500/30',
    converted: 'bg-green-900/40 text-green-400 border-green-500/30'
  };
  return (
    <span className={\`px-2 py-0.5 rounded-full text-[10px] font-bold border \${styles[status] || styles.new}\`}>
      {status.replace('_', ' ').toUpperCase()}
    </span>
  );
};

export default function App() {
  const [tab, setTab] = useState('dashboard');
  const [leads, setLeads] = useState([]);
  const [selectedPhone, setSelectedPhone] = useState(null);
  const [history, setHistory] = useState([]);
  const [reply, setReply] = useState('');
  const [health, setHealth] = useState({ whatsappConnected: false });
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [stats, setStats] = useState({ total: 0, engaged: 0, brochures: 0, ctas: 0, converted: 0 });

  const chatEndRef = useRef(null);

  // Poll for leads & health
  useEffect(() => {
    const fetchLeads = async () => {
      try {
        const res = await axios.get(\`\${API_BASE}/admin/leads\`);
        setLeads(res.data);
        
        // Update stats
        const s = { total: res.data.length, engaged: 0, brochures: 0, ctas: 0, converted: 0 };
        res.data.forEach(l => {
          if (l.status === 'engaged') s.engaged++;
          if (l.status === 'brochure_sent') s.brochures++;
          if (l.status === 'cta_sent') s.ctas++;
          if (l.status === 'converted') s.converted++;
        });
        setStats(s);
      } catch (e) { console.error(e); }
    };

    const fetchHealth = async () => {
      try {
        const res = await axios.get(\`\${API_BASE}/health\`);
        setHealth(res.data);
      } catch (e) { console.error(e); }
    };

    fetchLeads();
    fetchHealth();
    const interval = setInterval(() => { fetchLeads(); fetchHealth(); }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch conversation when lead selected
  useEffect(() => {
    if (selectedPhone) {
      const fetchHistory = async () => {
        try {
          const res = await axios.get(\`\${API_BASE}/admin/conversation/\${selectedPhone}\`);
          setHistory(res.data);
        } catch (e) { console.error(e); }
      };
      fetchHistory();
      const interval = setInterval(fetchHistory, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedPhone]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const sendManual = async () => {
    if (!reply || !selectedPhone) return;
    setLoading(true);
    try {
      await axios.post(\`\${API_BASE}/admin/send-manual\`, { phone: selectedPhone, message: reply });
      setReply('');
      // Refresh local history
      const res = await axios.get(\`\${API_BASE}/admin/conversation/\${selectedPhone}\`);
      setHistory(res.data);
    } catch (e) { alert('Failed to send'); }
    setLoading(false);
  };

  const markConverted = async (phone) => {
    try {
      await axios.post(\`\${API_BASE}/admin/update-status\`, { phone, status: 'converted' });
      // Refresh leads
      const res = await axios.get(\`\${API_BASE}/admin/leads\`);
      setLeads(res.data);
    } catch (e) { alert('Failed to update'); }
  };

  const filteredLeads = leads.filter(l => 
    l.phone.includes(search) || (l.name && l.name.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="flex h-screen w-full bg-dark text-gray-200 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-20 lg:w-64 bg-card border-r border-white/5 flex flex-col items-center lg:items-start">
        <div className="p-6 w-full flex items-center justify-center lg:justify-start gap-3">
          <div className="w-10 h-10 bg-gold rounded-xl flex items-center justify-center shadow-lg shadow-gold/20">
            <Share2 className="text-dark w-6 h-6" />
          </div>
          <div className="hidden lg:block">
            <h1 className="font-bold text-lg leading-tight tracking-tight">Wedding Mediaaa</h1>
            <p className="text-[10px] text-gold uppercase font-black tracking-widest opacity-80">AI Command Center</p>
          </div>
        </div>

        <nav className="flex-1 w-full px-3 mt-4 space-y-2">
          <button onClick={() => setTab('dashboard')} className={\`w-full flex items-center justify-center lg:justify-start p-3 rounded-xl transition-all \${tab === 'dashboard' ? 'bg-gold/10 text-gold shadow-sm' : 'hover:bg-white/5 text-gray-500'}\`}>
            <LayoutDashboard className="w-5 h-5 lg:mr-3" />
            <span className="hidden lg:block font-semibold">Dashboard</span>
          </button>
          <button onClick={() => setTab('setup')} className={\`w-full flex items-center justify-center lg:justify-start p-3 rounded-xl transition-all \${tab === 'setup' ? 'bg-gold/10 text-gold shadow-sm' : 'hover:bg-white/5 text-gray-500'}\`}>
            <ExternalLink className="w-5 h-5 lg:mr-3" />
            <span className="hidden lg:block font-semibold">API Setup</span>
          </button>
          <button onClick={() => setTab('settings')} className={\`w-full flex items-center justify-center lg:justify-start p-3 rounded-xl transition-all \${tab === 'settings' ? 'bg-gold/10 text-gold shadow-sm' : 'hover:bg-white/5 text-gray-500'}\`}>
            <Settings className="w-5 h-5 lg:mr-3" />
            <span className="hidden lg:block font-semibold">Global Settings</span>
          </button>
        </nav>

        <div className="p-4 w-full">
          <div className={\`p-3 rounded-2xl flex items-center gap-2 \${health.whatsappConnected ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}\`}>
            <div className={\`w-2 h-2 rounded-full \${health.whatsappConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}\`}></div>
            <span className="text-[10px] font-bold uppercase tracking-wider hidden lg:block">
              {health.whatsappConnected ? 'System Live' : 'WhatsApp Down'}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full relative">
        {/* Top Header Stats */}
        <header className="h-20 border-b border-white/5 bg-card/50 backdrop-blur-md flex items-center px-8 justify-between">
          <div className="flex gap-8">
            <div className="text-center">
              <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Total Leads</p>
              <p className="text-xl font-bold">{stats.total}</p>
            </div>
            <div className="text-center">
              <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Engaged</p>
              <p className="text-xl font-bold">{stats.engaged}</p>
            </div>
            <div className="text-center">
              <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">Brochures Sent</p>
              <p className="text-xl font-bold">{stats.brochures}</p>
            </div>
            <div className="text-center">
              <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest">CTAs Sent</p>
              <p className="text-xl font-bold">{stats.ctas}</p>
            </div>
            <div className="text-center">
              <p className="text-[10px] text-gold uppercase font-bold tracking-widest">Converted</p>
              <p className="text-xl font-bold text-gold">{stats.converted}</p>
            </div>
          </div>
        </header>

        {tab === 'dashboard' && (
          <div className="flex-1 flex overflow-hidden">
            {/* Lead List */}
            <div className="w-80 border-r border-white/5 flex flex-col">
              <div className="p-4 border-b border-white/5">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input 
                    type="text" placeholder="Search leads..." 
                    value={search} onChange={(e) => setSearch(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-sm outline-none focus:border-gold/50"
                  />
                </div>
              </div>
              <div className="flex-1 overflow-y-auto">
                {filteredLeads.map(l => (
                  <button 
                    key={l.phone} 
                    onClick={() => setSelectedPhone(l.phone)}
                    className={\`w-full p-4 border-b border-white/5 flex flex-col gap-2 text-left transition-all \${selectedPhone === l.phone ? 'bg-gold/5 border-l-4 border-l-gold' : 'hover:bg-white/5'}\`}
                  >
                    <div className="flex justify-between items-start">
                      <p className="font-bold text-sm">+{l.phone}</p>
                      <StatusBadge status={l.status} />
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-gray-500">
                      <span>{l.message_count} messages</span>
                      <span>{formatDistanceToNow(new Date(l.last_message_at))} ago</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Conversation View */}
            <div className="flex-1 flex flex-col bg-[#050505]">
              {selectedPhone ? (
                <>
                  <div className="p-4 border-b border-white/5 bg-card flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center font-bold text-gold">
                        {selectedPhone.slice(-2)}
                      </div>
                      <div>
                        <p className="font-bold">+{selectedPhone}</p>
                        <p className="text-[10px] text-green-500 flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" /> Active Interaction
                        </p>
                      </div>
                    </div>
                    <button 
                      onClick={() => markConverted(selectedPhone)}
                      className="px-4 py-2 bg-gold/10 text-gold border border-gold/20 rounded-xl text-xs font-bold hover:bg-gold/20 transition-all"
                    >
                      Mark as Converted
                    </button>
                  </div>

                  <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {history.map((msg, i) => (
                      <div key={i} className={\`flex \${msg.role === 'user' ? 'justify-start' : 'justify-end'}\`}>
                        <div className={\`max-w-[70%] p-3 rounded-2xl text-sm \${msg.role === 'user' ? 'bg-white/5 text-gray-200' : 'bg-gold/20 text-gold border border-gold/10'}\`}>
                          {msg.content}
                          <p className="text-[10px] opacity-40 mt-1 text-right">
                            {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </div>
                    ))}
                    <div ref={chatEndRef} />
                  </div>

                  <div className="p-4 bg-card border-t border-white/5">
                    <div className="flex gap-2">
                      <input 
                        type="text" value={reply} onChange={(e) => setReply(e.target.value)}
                        placeholder="Type a manual reply..."
                        className="flex-1 bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-sm outline-none focus:border-gold/50"
                        onKeyDown={(e) => e.key === 'Enter' && sendManual()}
                      />
                      <button 
                        onClick={sendManual} disabled={loading}
                        className="bg-gold text-dark p-3 rounded-xl font-bold hover:scale-105 active:scale-95 transition-all disabled:opacity-50"
                      >
                        {loading ? <Loader2 className="animate-spin" /> : <Send />}
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center p-10 opacity-30">
                  <MessageSquare className="w-20 h-20 mb-4" />
                  <h3 className="text-xl font-bold">Select a conversation</h3>
                  <p className="max-w-xs text-sm">Monitor AI-customer interactions in real-time or step in with a manual reply.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {tab === 'setup' && (
          <div className="flex-1 overflow-y-auto p-10 max-w-4xl mx-auto w-full">
             <div className="mb-10">
               <h2 className="text-3xl font-bold mb-2 text-gold">Meta API Setup</h2>
               <p className="text-gray-400">Follow these 7 steps to connect your WhatsApp Business account.</p>
             </div>
             
             <div className="space-y-6">
                {[
                  { num: 1, text: "Go to developers.facebook.com and login" },
                  { num: 2, text: "Create a 'Business' type app called 'Wedding Mediaaa Agent'" },
                  { num: 3, text: "Add 'WhatsApp' product to your app" },
                  { num: 4, text: "Configure Webhook: Set URL to your server address + /webhook" },
                  { num: 5, text: "Verify Token: 'wedding_mediaaa_secret_webhook_token_2024'" },
                  { num: 6, text: "Subscribe to 'messages' field in Webhook settings" },
                  { num: 7, text: "Generate Permanent System User Token & copy ID" },
                ].map((s, i) => (
                  <div key={i} className="flex items-center gap-4 bg-card p-4 rounded-2xl border border-white/5">
                    <div className="w-8 h-8 rounded-lg bg-gold/10 text-gold flex items-center justify-center font-bold">{s.num}</div>
                    <p className="flex-1 text-sm font-medium">{s.text}</p>
                    <CheckCircle className="w-5 h-5 text-green-500/50" />
                  </div>
                ))}
             </div>

             <div className="mt-12 bg-card p-8 rounded-3xl border border-gold/20">
                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                  <Upload className="text-gold w-5 h-5" /> Brochure Management
                </h3>
                <div className="border-2 border-dashed border-white/10 rounded-2xl p-8 text-center hover:border-gold/30 transition-all cursor-pointer">
                  <p className="text-sm text-gray-400">Drag and drop your company brochure (PDF) here</p>
                  <p className="text-[10px] text-gray-600 mt-2 uppercase tracking-widest font-bold">Max size: 10MB</p>
                </div>
             </div>
          </div>
        )}

        {tab === 'settings' && (
           <div className="flex-1 p-10 max-w-3xl">
              <h2 className="text-3xl font-bold mb-8">Agent Settings</h2>
              <div className="space-y-8">
                <div className="grid grid-cols-2 gap-6">
                   <div className="space-y-2">
                      <label className="text-[10px] uppercase font-black text-gray-500 tracking-widest">Founder Phone</label>
                      <input type="text" placeholder="+91 90000 11111" className="w-full bg-white/5 border border-white/10 rounded-xl p-4 outline-none focus:border-gold" />
                   </div>
                   <div className="space-y-2">
                      <label className="text-[10px] uppercase font-black text-gray-500 tracking-widest">Base Pricing</label>
                      <input type="text" placeholder="₹45,000" className="w-full bg-white/5 border border-white/10 rounded-xl p-4 outline-none focus:border-gold" />
                   </div>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-card rounded-2xl border border-white/5">
                    <div>
                      <p className="font-bold">Auto-send Brochure</p>
                      <p className="text-xs text-gray-500">Sends PDF automatically on the 2nd message exchange.</p>
                    </div>
                    <div className="w-12 h-6 bg-gold rounded-full relative"><div className="w-4 h-4 bg-dark rounded-full absolute top-1 right-1"></div></div>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-card rounded-2xl border border-white/5">
                    <div>
                      <p className="font-bold">Auto-CTA Flow</p>
                      <p className="text-xs text-gray-500">Automatically pushes for a call after 4 messages.</p>
                    </div>
                    <div className="w-12 h-6 bg-white/10 rounded-full relative"><div className="w-4 h-4 bg-white/30 rounded-full absolute top-1 left-1"></div></div>
                  </div>
                </div>
                <button className="w-full py-4 bg-gold text-dark font-black uppercase tracking-widest rounded-2xl hover:scale-[1.02] active:scale-[0.98] transition-all">Save Global Settings</button>
              </div>
           </div>
        )}
      </main>
    </div>
  );
}