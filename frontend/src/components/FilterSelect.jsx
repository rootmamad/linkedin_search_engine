import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, X, Check } from 'lucide-react';

export default function FilterSelect({ label, options, selected, onChange, multi = false }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setIsOpen(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const toggleOption = (option) => {
    if (!multi) {
      onChange(selected === option ? '' : option);
      setIsOpen(false);
      return;
    }
    const current = Array.isArray(selected) ? selected : [];
    const updated = current.includes(option)
      ? current.filter((item) => item !== option)
      : [...current, option];
    onChange(updated);
  };

  const removeChip = (e, option) => {
    e.stopPropagation();
    onChange(selected.filter((item) => item !== option));
  };

  const hasSelection = multi ? selected?.length > 0 : !!selected;

  return (
    <div className="relative" ref={dropdownRef}>
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="min-h-[42px] bg-[#111A31] border border-blue-900/50 rounded-xl p-2 flex items-center justify-between cursor-pointer hover:border-blue-500/50 transition-colors"
      >
        <div className="flex flex-wrap gap-1.5 items-center flex-1">
          {!hasSelection && <span className="text-slate-400 text-sm px-1">{label}</span>}
          
          {multi && hasSelection && selected.map(item => (
            <span key={item} className="bg-blue-600/20 border border-blue-500/30 text-blue-200 text-xs px-2 py-1 rounded-md flex items-center gap-1">
              {item}
              <div onClick={(e) => removeChip(e, item)} className="hover:text-white hover:bg-blue-500/50 rounded-full p-0.5 transition-colors">
                <X size={12} />
              </div>
            </span>
          ))}
          
          {!multi && hasSelection && (
            <span className="text-blue-200 text-sm px-1 capitalize">{selected}</span>
          )}
        </div>
        <ChevronDown size={16} className={`text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </div>

      {isOpen && (
        <div className="absolute z-50 top-full mt-2 w-full bg-[#1A2642] border border-blue-900/50 rounded-xl shadow-2xl max-h-60 overflow-y-auto custom-scrollbar p-1">
          {options.map((opt) => {
            const isSelected = multi ? selected?.includes(opt) : selected === opt;
            return (
              <div
                key={opt}
                onClick={() => toggleOption(opt)}
                className={`px-3 py-2 text-sm rounded-lg cursor-pointer flex items-center justify-between transition-colors ${
                  isSelected ? 'bg-blue-600/20 text-blue-300' : 'text-slate-300 hover:bg-white/5'
                }`}
              >
                <span className="capitalize">{opt}</span>
                {isSelected && <Check size={14} />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}