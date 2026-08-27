import React, { useRef, useState, useEffect } from 'react';

const SKILLS = [
  { category: 'Languages', items: ['Python', 'JavaScript', 'TypeScript', 'SQL', 'HTML/CSS'] },
  { category: 'Frameworks', items: ['Flask', 'React', 'Node.js', 'Bootstrap', 'Tailwind CSS'] },
  { category: 'Databases', items: ['SQLite', 'PostgreSQL', 'MongoDB'] },
  { category: 'Tools', items: ['Git', 'Docker', 'Nginx', 'Linux', 'Vim'] },
  { category: 'Concepts', items: ['REST APIs', 'Data Pipelines', 'PDF Parsing', 'OCR', 'Web Scraping'] },
];

const STATS = [
  { value: '3+', label: 'Years Coding' },
  { value: '10+', label: 'Projects Built' },
  { value: '290K+', label: 'Data Rows Processed' },
  { value: '142', label: 'Colleges Indexed' },
];

export default function About() {
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
    <section id="about" ref={sectionRef} className="relative py-32 px-6">
      <div className="max-w-6xl mx-auto">
        <div
          className={`text-center mb-16 transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <span className="section-title">About Me</span>
          <h2 className="text-4xl sm:text-5xl font-black mt-4 mb-4">
            <span className="text-white">Who </span>
            <span className="text-gradient">Am I</span>
          </h2>
        </div>

        {/* Bio card */}
        <div
          className={`glass-card p-8 sm:p-12 mb-12 transition-all duration-700 delay-200 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="grid lg:grid-cols-3 gap-10 items-start">
            <div className="lg:col-span-2 space-y-5">
              <p className="text-gray-300 text-lg leading-relaxed">
                I'm a developer and engineer passionate about building tools that solve
                real problems. My work spans full-stack web development, data engineering,
                and creating applications that make complex information accessible.
              </p>
              <p className="text-gray-400 leading-relaxed">
                My flagship project, the <span className="text-galaxy-300 font-semibold">KEAM Allotment Helper</span>,
                helps thousands of engineering aspirants in Kerala navigate the college admission
                process. It parses official CEE PDF documents into a searchable database and
                provides intelligent predictions, cutoff analysis, and migration tracking.
              </p>
              <p className="text-gray-400 leading-relaxed">
                I believe in building things that matter — tools that are fast, reliable, and
                genuinely useful. Every project I take on is an opportunity to learn something
                new and push the boundaries of what's possible.
              </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4">
              {STATS.map((stat, i) => (
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
          </div>
        </div>

        {/* Skills */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {SKILLS.map((group, i) => (
            <div
              key={group.category}
              className={`glass-card p-6 transition-all duration-500 ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
              }`}
              style={{ transitionDelay: `${400 + i * 80}ms` }}
            >
              <h3 className="text-sm font-bold text-galaxy-300 mb-3 uppercase tracking-wider">
                {group.category}
              </h3>
              <div className="flex flex-wrap gap-2">
                {group.items.map((skill) => (
                  <span key={skill} className="skill-badge">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
