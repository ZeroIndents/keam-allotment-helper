import React, { useState, useEffect } from 'react';

export default function ScrollProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPos = window.scrollY;
      setProgress(totalHeight > 0 ? (scrollPos / totalHeight) * 100 : 0);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="fixed top-0 left-0 right-0 z-[100] h-[3px]">
      <div
        className="h-full transition-[width] duration-150 ease-out"
        style={{
          width: `${progress}%`,
          background: 'linear-gradient(90deg, #7c3aed, #6366f1, #3b82f6, #06b6d4)',
          boxShadow: '0 0 10px rgba(124, 58, 237, 0.5)',
        }}
      />
    </div>
  );
}
