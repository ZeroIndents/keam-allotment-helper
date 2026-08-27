import React, { useState, useEffect } from 'react';

const KONAMI_CODE = [
  'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
  'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
  'b', 'a',
];

export default function EasterEgg() {
  const [activated, setActivated] = useState(false);
  const [input, setInput] = useState([]);

  useEffect(() => {
    const handleKey = (e) => {
      setInput((prev) => {
        const next = [...prev, e.key].slice(-KONAMI_CODE.length);
        if (JSON.stringify(next) === JSON.stringify(KONAMI_CODE)) {
          setActivated(true);
          setTimeout(() => setActivated(false), 5000);
          return [];
        }
        return next;
      });
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  if (!activated) return null;

  return (
    <div className="fixed inset-0 z-[200] pointer-events-none">
      {/* Celebration particles */}
      {Array.from({ length: 50 }).map((_, i) => (
        <div
          key={i}
          className="absolute animate-bounce"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            fontSize: `${Math.random() * 20 + 12}px`,
            animationDelay: `${Math.random() * 0.5}s`,
            animationDuration: `${1 + Math.random() * 2}s`,
          }}
        >
          {['🎉', '🚀', '⭐', '🎮', '🕹️', '💜', '✨', '🔥'][Math.floor(Math.random() * 8)]}
        </div>
      ))}

      {/* Center message */}
      <div className="fixed inset-0 flex items-center justify-center">
        <div className="glass-card p-8 text-center animate-bounce">
          <div className="text-6xl mb-4">🎮</div>
          <h3 className="text-2xl font-black text-gradient mb-2">KONAMI CODE ACTIVATED!</h3>
          <p className="text-gray-400 text-sm">You found the easter egg! 🎉</p>
        </div>
      </div>
    </div>
  );
}
