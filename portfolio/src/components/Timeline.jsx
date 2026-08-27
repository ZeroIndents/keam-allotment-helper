import React, { useRef, useState, useEffect } from 'react';

const MILESTONES = [
  {
    date: '2024',
    title: 'Home Assistant & Frigate Setup',
    desc: 'Built a smart home system with Home Assistant, Frigate NVR, and custom-trained YOLOv9 models for object detection.',
    icon: '🏠',
    color: 'from-emerald-500 to-teal-500',
  },
  {
    date: '2025',
    title: 'Industrial Water Level Sensor',
    desc: 'Designed and industrially tested an IoT water level sensor with ESP32 — real-world deployment, not just a prototype.',
    icon: '💧',
    color: 'from-cyan-500 to-blue-500',
  },
  {
    date: '2026',
    title: 'KEAM Allotment Helper',
    desc: 'Built a Flask/SQLite app to parse 290K+ CEE Kerala PDF allotment lists into a searchable database.',
    icon: '🎓',
    color: 'from-emerald-500 to-teal-500',
  },
  {
    date: '2026',
    title: 'Statistics Dashboard & 290K+ Rows',
    desc: 'Added cutoff trends, category spreads, heatmap visualizations, and migration tracking across 142 colleges.',
    icon: '📊',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    date: '2026',
    title: 'Apple Music Downloader',
    desc: 'Built a tool to download lossless ALAC, AAC, or Dolby Atmos from Apple Music subscriptions.',
    icon: '🎵',
    color: 'from-pink-500 to-rose-500',
  },
  {
    date: '2026',
    title: 'Ultrasonic Dog Repeller',
    desc: 'Built an ultrasonic hardware device to safely repel dogs — designed, 3D-printed, and tested.',
    icon: '🐕',
    color: 'from-orange-500 to-red-500',
  },
];

export default function Timeline() {
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
    <section id="timeline" ref={sectionRef} className="relative py-32 px-6">
      <div className="max-w-4xl mx-auto">
        <div
          className={`text-center mb-16 transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <span className="section-title">Journey</span>
          <h2 className="text-4xl sm:text-5xl font-black mt-4 mb-4">
            <span style={{color: 'var(--text-heading)'}}>My </span>
            <span className="text-gradient">Timeline</span>
          </h2>
          <p className="text-lg max-w-xl mx-auto" style={{color: 'var(--text-secondary)'}}>
            Key milestones and projects that shaped my journey.
          </p>
        </div>

        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-px" style={{background: 'linear-gradient(to bottom, var(--accent-glow-strong), var(--accent-glow), transparent)'}} />

          {MILESTONES.map((m, i) => (
            <div
              key={i}
              className={`relative flex items-start gap-6 mb-12 transition-all duration-700 ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
              } ${i % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'}`}
              style={{ transitionDelay: `${200 + i * 100}ms` }}
            >
              {/* Content */}
              <div className={`flex-1 ${i % 2 === 0 ? 'md:text-right' : 'md:text-left'}`}>
                <div className={`glass-card p-6 inline-block ${i % 2 === 0 ? 'md:ml-auto' : ''}`}>
                  <span className="text-xs font-bold uppercase tracking-wider" style={{color: 'var(--text-accent)'}}>
                    {m.date}
                  </span>
                  <h3 className="text-lg font-bold mt-1 mb-2" style={{color: 'var(--text-heading)'}}>{m.title}</h3>
                  <p className="text-sm leading-relaxed" style={{color: 'var(--text-secondary)'}}>{m.desc}</p>
                </div>
              </div>

              {/* Dot */}
              <div className="relative z-10 flex-shrink-0">
                <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${m.color} flex items-center justify-center text-xl shadow-lg`}>
                  {m.icon}
                </div>
              </div>

              {/* Spacer for the other side */}
              <div className="flex-1 hidden md:block" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
