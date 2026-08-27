import React, { useState, useRef, useEffect } from 'react';

const FEATURES = [
  {
    icon: '🔍',
    title: '290K+ Allotment Rows',
    desc: 'Search across official CEE Kerala allotment lists from 2024-2026',
  },
  {
    icon: '📊',
    title: 'Live Statistics',
    desc: 'Cutoff trends, category spreads, college comparisons & migration tracking',
  },
  {
    icon: '🎯',
    title: 'Rank Predictor',
    desc: '5:3:2 board normalization calculator with estimated merit-rank brackets',
  },
  {
    icon: '⚡',
    title: 'Find Your Options',
    desc: 'Enter your rank and see Safe / Moderate / Ambitious college suggestions',
  },
  {
    icon: '🗺️',
    title: 'Migration Tracker',
    desc: 'See how students switch colleges between allotment rounds',
  },
  {
    icon: '📄',
    title: 'Document Toolkit',
    desc: 'Client-side photo resize, image-to-PDF, and PDF compression',
  },
];

export default function KeamShowcase() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.15 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="keam"
      ref={sectionRef}
      className="relative py-32 px-6"
    >
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <div
          className={`text-center mb-16 transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <span className="section-title">Featured Project</span>
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-black mt-4 mb-6">
            <span className="text-gradient">KEAM</span>{' '}
            <span className="text-white">Allotment Helper</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">
            A comprehensive tool helping thousands of engineering aspirants navigate
            CEE Kerala's allotment process with real data and intelligent predictions.
          </p>
        </div>

        {/* Main showcase card */}
        <div
          className={`glass-card p-1 mb-16 transition-all duration-700 delay-200 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="relative rounded-[18px] overflow-hidden bg-gradient-to-br from-galaxy-950/80 via-black/60 to-galaxy-950/80 p-8 sm:p-12">
            {/* Decorative elements */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-galaxy-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/3" />

            <div className="relative grid lg:grid-cols-2 gap-12 items-center">
              {/* Left: description */}
              <div>
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-galaxy-500 to-blue-500 flex items-center justify-center text-2xl shadow-lg shadow-galaxy-500/30">
                    🎓
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">
                      KEAM Allotment Helper
                    </h3>
                    <p className="text-xs text-gray-400 font-medium">
                      Live at gavinjoseph.in/keam
                    </p>
                  </div>
                </div>

                <p className="text-gray-300 leading-relaxed mb-6">
                  Built with <span className="text-galaxy-300 font-semibold">Flask</span>,{' '}
                  <span className="text-galaxy-300 font-semibold">SQLite</span>, and{' '}
                  <span className="text-galaxy-300 font-semibold">Bootstrap 5</span> — this tool
                  parses official CEE Kerala PDF allotment lists and presents them through an
                  interactive dashboard with server-side DataTables, Chart.js visualizations,
                  and D3-powered migration maps.
                </p>

                <div className="flex flex-wrap gap-2 mb-8">
                  {['Python', 'Flask', 'SQLite', 'Bootstrap 5', 'Chart.js', 'D3.js', 'Tailwind CSS'].map((tech) => (
                    <span key={tech} className="skill-badge">
                      {tech}
                    </span>
                  ))}
                </div>

                <div className="flex flex-wrap gap-3">
                  <a
                    href="/keam/"
                    className="btn-primary"
                  >
                    🚀 Launch App
                  </a>
                  <a
                    href="https://github.com/gavinjoseph"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                    Source Code
                  </a>
                </div>
              </div>

              {/* Right: Stats + preview */}
              <div className="space-y-4">
                {/* Live stats */}
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: 'Rows Indexed', value: '290K+' },
                    { label: 'Colleges', value: '142' },
                    { label: 'Active Years', value: '3' },
                  ].map((stat, i) => (
                    <div
                      key={stat.label}
                      className="glass rounded-xl p-4 text-center"
                    >
                      <div className="text-2xl font-black text-gradient mb-1">
                        {stat.value}
                      </div>
                      <div className="text-[11px] text-gray-500 font-medium uppercase tracking-wider">
                        {stat.label}
                      </div>
                    </div>
                  ))}
                </div>

                {/* App preview mockup */}
                <div className="glass rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-3 h-3 rounded-full bg-red-500/80" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                    <div className="w-3 h-3 rounded-full bg-green-500/80" />
                    <span className="text-[11px] text-gray-500 ml-2 font-mono">
                      gavinjoseph.in
                    </span>
                  </div>
                  <div className="bg-black/40 rounded-lg p-3 space-y-2">
                    <div className="flex gap-2">
                      <div className="h-6 flex-1 rounded bg-galaxy-500/20 flex items-center px-2">
                        <span className="text-[10px] text-galaxy-300">🎓 KEAM Allotment Helper</span>
                      </div>
                      <div className="h-6 w-16 rounded bg-emerald-500/20 flex items-center justify-center">
                        <span className="text-[10px] text-emerald-400">Predict</span>
                      </div>
                    </div>
                    <div className="grid grid-cols-4 gap-1">
                      {['Year', 'Phase', 'College', 'Course'].map((f) => (
                        <div key={f} className="h-5 rounded bg-white/5 flex items-center justify-center">
                          <span className="text-[9px] text-gray-500">{f}</span>
                        </div>
                      ))}
                    </div>
                    <div className="space-y-1">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="h-4 rounded bg-white/3 flex items-center px-2 gap-2">
                          <div className="w-8 h-2 rounded bg-galaxy-500/30" />
                          <div className="flex-1 h-2 rounded bg-white/5" />
                          <div className="w-12 h-2 rounded bg-emerald-500/20" />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Features grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((feature, i) => (
            <div
              key={feature.title}
              className={`glass-card p-6 transition-all duration-500 ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
              }`}
              style={{ transitionDelay: `${300 + i * 80}ms` }}
            >
              <div className="text-3xl mb-3">{feature.icon}</div>
              <h3 className="text-base font-bold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
