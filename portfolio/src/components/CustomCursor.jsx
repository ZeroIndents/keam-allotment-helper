import React, { useState, useEffect } from 'react';

export default function CustomCursor() {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [clicking, setClicking] = useState(false);
  const [hovering, setHovering] = useState(false);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Only show on desktop
    if (window.matchMedia('(hover: none)').matches) return;

    const handleMove = (e) => {
      setPos({ x: e.clientX, y: e.clientY });
      setVisible(true);
    };

    const handleDown = () => setClicking(true);
    const handleUp = () => setClicking(false);

    const handleOverInteractive = (e) => {
      if (e.target.closest('a, button, .glass-card, .skill-badge, [role="button"]')) {
        setHovering(true);
      } else {
        setHovering(false);
      }
    };

    document.addEventListener('mousemove', handleMove);
    document.addEventListener('mousedown', handleDown);
    document.addEventListener('mouseup', handleUp);
    document.addEventListener('mouseover', handleOverInteractive);

    document.body.style.cursor = 'none';

    return () => {
      document.removeEventListener('mousemove', handleMove);
      document.removeEventListener('mousedown', handleDown);
      document.removeEventListener('mouseup', handleUp);
      document.removeEventListener('mouseover', handleOverInteractive);
      document.body.style.cursor = '';
    };
  }, []);

  if (!visible) return null;

  return (
    <>
      {/* Outer glow ring */}
      <div
        className="fixed pointer-events-none z-[9999] rounded-full transition-transform duration-200 ease-out mix-blend-difference hidden md:block"
        style={{
          width: hovering ? 48 : 32,
          height: hovering ? 48 : 32,
          left: pos.x - (hovering ? 24 : 16),
          top: pos.y - (hovering ? 24 : 16),
          border: `2px solid ${hovering ? 'rgba(139, 92, 246, 0.8)' : 'rgba(255, 255, 255, 0.4)'}`,
          transform: clicking ? 'scale(0.8)' : 'scale(1)',
          background: hovering ? 'rgba(139, 92, 246, 0.1)' : 'transparent',
        }}
      />
      {/* Inner dot */}
      <div
        className="fixed pointer-events-none z-[9999] rounded-full hidden md:block"
        style={{
          width: 6,
          height: 6,
          left: pos.x - 3,
          top: pos.y - 3,
          background: '#fff',
          transform: clicking ? 'scale(0.5)' : 'scale(1)',
          boxShadow: '0 0 8px rgba(139, 92, 246, 0.6)',
        }}
      />
    </>
  );
}
