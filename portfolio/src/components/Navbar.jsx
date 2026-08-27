import React, { useState, useEffect } from 'react';

const NAV_ITEMS = [
  { id: 'home', label: 'Home', icon: '✦' },
  { id: 'keam', label: 'KEAM Helper', icon: '🎓' },
  { id: 'projects', label: 'Projects', icon: '⚡' },
  { id: 'timeline', label: 'Journey', icon: '📅' },
  { id: 'about', label: 'About', icon: '👤' },
  { id: 'contact', label: 'Contact', icon: '✉️' },
];

export default function Navbar() {
  const [active, setActive] = useState('home');
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);

      const sections = NAV_ITEMS.map(item => ({
        id: item.id,
        el: document.getElementById(item.id),
      })).filter(s => s.el);

      const scrollPos = window.scrollY + window.innerHeight / 3;
      for (let i = sections.length - 1; i >= 0; i--) {
        if (sections[i].el.offsetTop <= scrollPos) {
          setActive(sections[i].id);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <nav
      className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 transition-all duration-500 ${
        scrolled ? 'opacity-100' : 'opacity-100'
      }`}
    >
      <div className="nav-pill flex items-center gap-1 shadow-2xl shadow-black/30">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => scrollTo(item.id)}
            className={`${
              active === item.id ? 'active' : ''
            } whitespace-nowrap`}
          >
            <span className="hidden sm:inline">{item.label}</span>
            <span className="sm:hidden">{item.icon}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}
