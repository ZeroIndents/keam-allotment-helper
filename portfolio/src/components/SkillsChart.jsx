import React, { useRef, useState, useEffect } from 'react';

const SKILLS = [
  { name: 'Python', level: 90, color: '#3572A5' },
  { name: 'JavaScript', level: 75, color: '#f1e05a' },
  { name: 'React', level: 70, color: '#61DAFB' },
  { name: 'Flask', level: 85, color: '#000000' },
  { name: 'SQLite', level: 80, color: '#003B57' },
  { name: 'IoT/ESP32', level: 85, color: '#E60012' },
  { name: 'Docker', level: 60, color: '#2496ED' },
  { name: 'Linux', level: 80, color: '#FCC624' },
  { name: 'CSS/Tailwind', level: 75, color: '#06B6D4' },
  { name: 'Git', level: 80, color: '#F05032' },
];

export default function SkillsChart() {
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
      <div className="max-w-4xl mx-auto">
        <div
          className={`transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="text-center mb-10">
            <span className="section-title">Expertise</span>
            <h2 className="text-3xl sm:text-4xl font-black mt-3 mb-2">
              <span style={{color: 'var(--text-heading)'}}>Tech </span>
              <span className="text-gradient">Skills</span>
            </h2>
          </div>

          <div className="glass-card p-6 sm:p-8">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {SKILLS.map((skill, i) => (
                <div
                  key={skill.name}
                  className={`transition-all duration-500 ${
                    isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4'
                  }`}
                  style={{ transitionDelay: `${100 + i * 50}ms` }}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm font-medium" style={{color: 'var(--text-primary)'}}>{skill.name}</span>
                    <span className="text-xs font-bold" style={{color: 'var(--text-muted)'}}>{skill.level}%</span>
                  </div>
                  <div className="h-2.5 rounded-full overflow-hidden" style={{background: 'var(--accent-glow)'}}>
                    <div
                      className="h-full rounded-full transition-all duration-1000 ease-out"
                      style={{
                        width: isVisible ? `${skill.level}%` : '0%',
                        background: `linear-gradient(90deg, ${skill.color}88, ${skill.color})`,
                        boxShadow: `0 0 8px ${skill.color}40`,
                        transitionDelay: `${200 + i * 80}ms`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
