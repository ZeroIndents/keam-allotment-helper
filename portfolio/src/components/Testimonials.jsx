import React, { useRef, useState, useEffect } from 'react';

const HIGHLIGHTS = [
  {
    icon: '📊',
    title: '290K+ Rows Processed',
    desc: 'Every official KEAM allotment row parsed and indexed — no data skipped.',
  },
  {
    icon: '🏛️',
    title: '142 Colleges Covered',
    desc: 'Every engineering college in Kerala mapped with cutoff trends across 3 years.',
  },
  {
    icon: '⚡',
    title: 'Instant Search',
    desc: 'Search through 290K+ rows in milliseconds — no PDF digging required.',
  },
  {
    icon: '🔓',
    title: 'Free & Open',
    desc: 'No login, no paywall, no ads. Built for students, by a student.',
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
          <span className="section-title">Why It Matters</span>
          <h2 className="text-3xl sm:text-4xl font-black mt-3 mb-2">
            <span className="text-white">Built With </span>
            <span className="text-gradient">Real Data</span>
          </h2>
          <p className="text-gray-400 text-sm max-w-lg mx-auto">
            Not a mockup. Not a prototype. Every number below comes from actual CEE Kerala allotment data.
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
              <h3 className="text-base font-bold text-white mb-2">{h.title}</h3>
              <p className="text-xs text-gray-400 leading-relaxed">{h.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
