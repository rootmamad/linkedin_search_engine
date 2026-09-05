import React, { useState } from 'react';
import { Search, MapPin, Briefcase, Mail, Phone, GraduationCap, Link as LinkIcon, User, Plus, X } from 'lucide-react';

// --- Data Constants ---
const ROLES = ['education', 'engineering', 'media', 'sales', 'customer_service', 'investment management', 'operations', 'marketing', 'finance', 'human_resources', 'design', 'real_estate', 'health', 'legal'];
const INDUSTRIES = ['primary/secondary education', 'semiconductors', 'law practice', 'investment management', 'biotechnology', 'government relations', 'information technology and services', 'civil engineering', 'shipbuilding', 'machinery', 'staffing and recruiting', 'apparel & fashion', 'health, wellness and fitness', 'sporting goods', 'food & beverages', 'security and investigations', 'mechanical or industrial engineering', 'education management', 'medical devices', 'railroad manufacture', 'public relations and communications', 'human resources', 'accounting', 'consumer electronics', 'higher education', 'defense & space', 'research', 'construction', 'broadcast media', 'philanthropy', 'wholesale', 'internet', 'business supplies and equipment', 'legal services', 'international affairs', 'design', 'law enforcement', 'management consulting', 'non-profit organization management', 'utilities', 'marketing and advertising', 'entertainment', 'automotive', 'religious institutions', 'hospital & health care', 'telecommunications', 'hospitality', 'aviation & aerospace', 'banking', 'renewables & environment', 'industrial automation', 'consumer services', 'legislative office', 'political organization', 'pharmaceuticals', 'restaurants', 'real estate', 'medical practice', 'retail', 'computer software', 'mental health care', 'government administration', 'publishing', 'electrical/electronic manufacturing', 'financial services', 'leisure, travel & tourism', 'military', 'oil & energy', 'international trade and development', 'civic & social organization', 'libraries', 'food production', 'insurance', 'chemicals', 'consumer goods'];
const LEVELS = ['senior', 'vp', 'training', 'partner', 'manager', 'owner', 'director', 'unpaid', 'accounts', 'professor', 'entry', 'cxo'];
const LOC_COUNTRIES = ['denmark', 'australia', 'france', 'canada', 'iraq', 'united states', 'india', 'united arab emirates', 'united kingdom'];
const COMP_COUNTRIES = ['france', 'united kingdom', 'germany', 'canada', 'denmark', 'iraq', 'united states', 'australia', 'mexico', 'finland', 'japan'];

// Reusable Null-Safe Renderer
const Field = ({ value, className = "text-slate-300" }) => 
  value && value !== "..." && value !== "" ? <span className={className}>{value}</span> : <span className="text-slate-600 font-light">—</span>;

export default function App() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({
    job_title_role: '', job_title_levels: [], company_industry: '',
    company_country: '', company_region: '', location_country: '', location_region: '', skills: []
  });
  const [skillInput, setSkillInput] = useState('');
  const [results, setResults] = useState([]);
  const [activeProfile, setActiveProfile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFilterChange = (key, value) => setFilters(prev => ({ ...prev, [key]: value }));

  const toggleMultiSelect = (key, value) => {
    setFilters(prev => {
      const current = prev[key];
      return { ...prev, [key]: current.includes(value) ? current.filter(item => item !== value) : [...current, value] };
    });
  };

  const addSkill = () => {
    if (skillInput.trim() && !filters.skills.includes(skillInput.trim())) {
      setFilters(prev => ({ ...prev, skills: [...prev.skills, skillInput.trim()] }));
      setSkillInput('');
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    setActiveProfile(null);
    try {
      const payload = { q: query, ...filters, page: 1, page_size: 20 };
      const res = await fetch('http://127.0.0.1:8000/api/search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'accept': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      console.log("Raw Backend Data:", data); 

      // اصلاح کلید اصلی به items بر اساس ساختار واقعی بک‌اند شما
      if (data && Array.isArray(data.items)) {
        setResults(data.items);
      } else if (Array.isArray(data)) {
        setResults(data);
      } else if (data && Array.isArray(data.results)) {
        setResults(data.results);
      } else if (data && Array.isArray(data.data)) {
        setResults(data.data);
      } else {
        setResults([]); 
      }

    } catch (error) {
      console.error("Search failed:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="min-h-screen bg-[#070B14] text-slate-200 font-sans selection:bg-blue-500/30 flex flex-col h-screen overflow-hidden">
      
      <header className="px-8 py-5 shrink-0 bg-[#0A1121] border-b border-blue-900/30 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-teal-300 tracking-tight">
            linkedin search Engine
          </h1>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden p-6 gap-6">
        

        <div className="w-[480px] flex flex-col gap-3 shrink-0 h-full">
          
          <div className="bg-[#0D1526] border border-blue-900/30 rounded-2xl p-3.5 shadow-2xl shrink-0 flex flex-col gap-2.5">
            
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-blue-500/50" />
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search queries..." 
                className="w-full bg-[#111A31] border border-blue-900/50 rounded-xl py-1.5 pl-9 pr-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-all text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Job Details</h3>
              <div className="grid grid-cols-2 gap-2">
                <select className="w-full bg-[#111A31] border border-blue-900/50 rounded-xl p-2 text-xs text-slate-300 outline-none focus:border-blue-500"
                        value={filters.job_title_role} onChange={e => handleFilterChange('job_title_role', e.target.value)}>
                  <option value="">Role (Any)</option>
                  {ROLES.map(r => <option key={r} value={r} className="capitalize">{r.replace('_', ' ')}</option>)}
                </select>
                <select className="w-full bg-[#111A31] border border-blue-900/50 rounded-xl p-2 text-xs text-slate-300 outline-none focus:border-blue-500"
                        value={filters.company_industry} onChange={e => handleFilterChange('company_industry', e.target.value)}>
                  <option value="">Industry (Any)</option>
                  {INDUSTRIES.map(i => <option key={i} value={i} className="capitalize">{i}</option>)}
                </select>
              </div>
              <div className="bg-[#111A31] border border-blue-900/50 rounded-xl p-2">
                <p className="text-[9px] uppercase tracking-wider text-slate-500 mb-1">Job Levels (Multi-select)</p>
                <div className="flex flex-wrap gap-1">
                  {LEVELS.map(level => {
                    const isActive = filters.job_title_levels.includes(level);
                    return (
                      <button key={level} onClick={() => toggleMultiSelect('job_title_levels', level)}
                        className={`text-[10px] px-1.5 py-0.5 rounded border capitalize transition-colors ${isActive ? 'bg-blue-600/20 border-blue-500 text-blue-300' : 'bg-transparent border-blue-900/30 text-slate-400 hover:border-blue-500/50'}`}>
                        {level}
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>

            <div className="space-y-2.5 pt-2.5 border-t border-blue-900/30">
            <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Location</h3>
            <div className="grid grid-cols-2 gap-2.5">
              <select className="w-full bg-[#111A31] border border-blue-900/50 rounded-xl p-2.5 text-sm text-slate-300 outline-none focus:border-blue-500"
                      value={filters.location_country} onChange={e => handleFilterChange('location_country', e.target.value)}>
                <option value="">Person Country</option>
                {LOC_COUNTRIES.map(c => <option key={c} value={c} className="capitalize">{c}</option>)}
              </select>
              <select className="w-full bg-[#111A31] border border-blue-900/50 rounded-xl p-2.5 text-sm text-slate-300 outline-none focus:border-blue-500"
                      value={filters.company_country} onChange={e => handleFilterChange('company_country', e.target.value)}>
                <option value="">Company Country</option>
                {COMP_COUNTRIES.map(c => <option key={c} value={c} className="capitalize">{c}</option>)}
              </select>
            </div>
          </div>

            <div className="space-y-1.5 pt-2 border-t border-blue-900/30">
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Custom Skills</h3>
              <div className="flex gap-2">
                <input type="text" placeholder="Type & enter..." 
                  className="flex-1 bg-[#111A31] border border-blue-900/50 rounded-xl py-1.5 px-2.5 text-xs text-white focus:border-blue-500 outline-none"
                  value={skillInput} onChange={e => setSkillInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && addSkill()} />
                <button onClick={addSkill} className="bg-blue-600/20 text-blue-400 border border-blue-500/30 p-1.5 rounded-xl hover:bg-blue-500/30 transition-colors"><Plus size={16}/></button>
              </div>
              {filters.skills.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {filters.skills.map(skill => (
                    <span key={skill} className="flex items-center gap-1 bg-blue-900/40 text-blue-300 text-[10px] px-2 py-0.5 rounded-lg border border-blue-800/50">
                      {skill} <X className="w-3 h-3 cursor-pointer hover:text-white" onClick={() => toggleMultiSelect('skills', skill)} />
                    </span>
                  ))}
                </div>
              )}
            </div>

            <button onClick={handleSearch} disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-500 hover:to-teal-500 text-white font-medium py-2 rounded-xl text-xs transition-all shadow-lg shadow-blue-900/20 mt-1">
              {loading ? 'Executing Query...' : 'Run Intelligence Query'}
            </button>
          </div>

          <div className="flex-1 overflow-y-auto pr-1 space-y-2.5 custom-scrollbar">
            {loading ? <div className="text-center text-slate-500 py-6 text-xs animate-pulse">Scanning records...</div> : 
             results.map((user) => (
              <div key={user.id} onClick={() => setActiveProfile(user)}
                className={`bg-[#0D1526] border rounded-xl p-3 cursor-pointer transition-all ${activeProfile?.id === user.id ? 'border-blue-500 bg-[#111A31] shadow-[0_0_15px_rgba(59,130,246,0.15)]' : 'border-blue-900/30 hover:border-blue-500/50'}`}>
                <h3 className="font-bold text-white text-sm capitalize"><Field value={user.full_name} /></h3>
                <p className="text-xs text-slate-400 mt-0.5 capitalize"><Field value={user.job_title} /></p>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  <span className="text-[10px] bg-blue-950/50 text-blue-300 px-1.5 py-0.5 rounded border border-blue-900/50 capitalize">
                    <Field value={user.company_name?.replace(/-/g, ' ')} />
                  </span>
                  <span className="text-[10px] bg-slate-800/50 text-slate-400 px-1.5 py-0.5 rounded border border-slate-700/50 capitalize">
                    <Field value={user.location_country} />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="flex-1 bg-[#0A1121] border border-blue-900/30 rounded-2xl shadow-2xl overflow-y-auto custom-scrollbar relative">
          {!activeProfile ? (
            <div className="h-full flex items-center justify-center text-slate-600">Select a record from the results to view deep intelligence details</div>
          ) : (
            <div className="p-10 animate-fade-in">
              
              <div className="flex justify-between items-start border-b border-blue-900/30 pb-8 mb-8">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h2 className="text-4xl font-black text-white capitalize"><Field value={activeProfile.full_name} /></h2>
                    <span className="bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs px-2 py-1 rounded uppercase tracking-wider">
                      ID: {activeProfile.id}
                    </span>
                  </div>
                  <div className="text-xl text-slate-300 font-medium capitalize flex items-center gap-2">
                    <Briefcase size={20} className="text-blue-500"/>
                    <Field value={activeProfile.job_title} /> <span className="text-slate-600">at</span> <Field value={activeProfile.company_name?.replace(/-/g, ' ')} />
                  </div>
                  <div className="text-slate-400 mt-2 flex items-center gap-2 capitalize">
                    <MapPin size={16} className="text-teal-500"/>
                    <Field value={activeProfile.location_region} />, <Field value={activeProfile.location_country} />
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-3 text-sm">
                  {activeProfile.linkedin_url ? (
                    <a href={`https://${activeProfile.linkedin_url}`} target="_blank" rel="noreferrer" className="flex items-center gap-2 bg-[#0077b5]/10 text-[#0077b5] hover:bg-[#0077b5]/20 px-4 py-2 rounded-lg transition-colors border border-[#0077b5]/30 font-medium">
                      <LinkIcon size={16}/> LinkedIn
                    </a>
                  ) : <Field value={null} />}
                  <span className="text-slate-500 capitalize flex items-center gap-2 bg-[#111A31] px-3 py-1.5 rounded-lg border border-blue-900/30">
                    <User size={14} className="text-blue-400"/> {activeProfile.gender || "—"}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-10">
                <div className="col-span-2 space-y-10">
                  <section>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Executive Summary</h3>
                    <p className="text-slate-300 leading-relaxed text-lg"><Field value={activeProfile.summary} /></p>
                  </section>

                  <section>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6">Professional History</h3>
                    <div className="space-y-6 border-l border-blue-900/50 ml-2 pl-6 relative">
                      {activeProfile.experiences?.length ? activeProfile.experiences.map((exp, idx) => (
                        <div key={idx} className="relative">
                          <div className="absolute -left-[31px] top-1.5 h-3 w-3 rounded-full bg-blue-500 ring-4 ring-[#0A1121]"></div>
                          <h4 className="text-white font-semibold text-lg capitalize"><Field value={exp.job_title} /></h4>
                          <p className="text-teal-400 capitalize"><Field value={exp.company_name} /></p>
                        </div>
                      )) : <Field value={null} />}
                    </div>
                  </section>

                  <section>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                      <GraduationCap size={16} className="text-blue-400"/> Academic Background
                    </h3>
                    <div className="grid gap-4">
                      {activeProfile.educations?.length ? activeProfile.educations.map((edu, idx) => (
                        <div key={idx} className="bg-[#0D1526] border border-blue-900/30 rounded-xl p-5 shadow-inner">
                          <h4 className="text-white font-medium capitalize text-lg mb-3"><Field value={edu.school_name} /></h4>
                          <div className="flex gap-10 text-sm">
                            <div>
                              <span className="text-slate-500 block mb-1 uppercase text-[10px] tracking-wider">Degrees</span>
                              {edu.degrees?.length ? edu.degrees.map(d => <div key={d} className="text-slate-300 capitalize">{d}</div>) : <Field value={null} />}
                            </div>
                            <div>
                              <span className="text-slate-500 block mb-1 uppercase text-[10px] tracking-wider">Majors</span>
                              {edu.majors?.length ? edu.majors.map(m => <div key={m} className="text-slate-300 capitalize">{m}</div>) : <Field value={null} />}
                            </div>
                          </div>
                        </div>
                      )) : <Field value={null} />}
                    </div>
                  </section>
                </div>

                <div className="space-y-10">
                  <section>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Verified Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {activeProfile.skills?.length ? activeProfile.skills.map((skill, idx) => (
                        <span key={idx} className="bg-[#111A31] border border-blue-900/30 text-teal-300 px-3 py-1.5 rounded-lg text-sm capitalize">
                          {skill}
                        </span>
                      )) : <Field value={null} />}
                    </div>
                  </section>

                  <section className="bg-[#0D1526] border border-blue-900/30 rounded-2xl p-5 shadow-lg">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Contact Intelligence</h3>
                    <div className="space-y-5">
                      <div>
                        <div className="flex items-center gap-2 text-slate-400 mb-2 text-sm"><Mail size={16} className="text-emerald-400"/> Email Addresses</div>
                        {activeProfile.emails?.length ? activeProfile.emails.map((email, idx) => (
                          <div key={idx} className="flex flex-col mb-2 last:mb-0 bg-[#111A31] p-2 rounded-lg border border-blue-900/20">
                            <span className="text-blue-300 text-sm">{email.address}</span>
                            <span className="text-[10px] uppercase text-slate-500">{email.type || 'unknown type'}</span>
                          </div>
                        )) : <Field value={null} />}
                      </div>

                      <div className="pt-4 border-t border-blue-900/30">
                        <div className="flex items-center gap-2 text-slate-400 mb-2 text-sm"><Phone size={16} className="text-emerald-400"/> Phone Numbers</div>
                        {activeProfile.phone_numbers?.length ? activeProfile.phone_numbers.map((phone, idx) => (
                          <div key={idx} className="text-slate-300 font-mono text-sm bg-[#111A31] p-2 rounded-lg border border-blue-900/20 mb-2">{phone}</div>
                        )) : <Field value={null} />}
                      </div>
                    </div>
                  </section>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}