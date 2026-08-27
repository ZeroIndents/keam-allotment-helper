import React, { useRef, useState, useEffect } from 'react';

const HIGHLIGHTS = [
  {
    icon: '🌐',
    title: 'Full-Stack Developer',
    desc: 'Python backends, React frontends, SQLite databases, REST APIs — build complete systems end-to-end.',
  },
  {
    icon: '🤖',
    title: 'IoT & Hardware',
    desc: 'ESP32 devices, Home Assistant, Frigate NVR with custom YOLOv9 models, industrial sensors — real-world deployments.',
  },
  {
    icon: '🧠',
    title: 'AI & Data Pipelines',
    desc: 'Zero-shot market forecasting, 290K+ row data pipelines, PDF parsing, web scraping — turning raw data into tools.',
  },
  {
    icon: '🚀',
    title: 'Ship & Deploy',
    desc: 'Proxmox labs, Docker containers, Cloudflare, Gunicorn — production-grade infrastructure from day one.',
  },
];

export default function Testimonials() {
  const sectionRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.1 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} className="relative py-20 px-6">
      <div className="max-w-5xl mx-auto">
        <div
          className={`text-center mb-12 transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <span className="section-title">What I Do</span>
          <h2 className="text-3xl sm:text-4xl font-black mt-3 mb-2">
            <span style={{color: 'var(--text-heading)'}}>Beyond </span>
            <span className="text-gradient">The Code</span>
          </h2>
          <p className="text-sm max-w-lg mx-auto" style={{color: 'var(--text-secondary)'}}>
            Building across the full stack — from IoT hardware to AI pipelines to production web apps.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {HIGHLIGHTS.map((h, i) => (
            <div
              key={i}
              className={`glass-card p-6 text-center transition-all duration-500 ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
              }`}
              style={{ transitionDelay: `${200 + i * 100}ms` }}
            >
              <div className="text-3xl mb-3">{h.icon}</div>
              <h3 className="text-base font-bold mb-2" style={{color: 'var(--text-heading)'}}>{h.title}</h3>
              <p className="text-xs leading-relaxed" style={{color: 'var(--text-secondary)'}}>{h.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
