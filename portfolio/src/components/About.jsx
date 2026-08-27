import React, { useRef, useState, useEffect } from 'react';

const SKILLS = [
  { category: 'Languages', items: ['Python', 'JavaScript', 'SQL', 'HTML/CSS', 'Bash'] },
  { category: 'Web & Frameworks', items: ['Flask', 'React', 'Tailwind CSS', 'Bootstrap', 'Nginx'] },
  { category: 'IoT & Hardware', items: ['ESP32', 'Arduino', 'Home Assistant', 'Frigate NVR', 'YOLOv9'] },
  { category: 'Virtualization', items: ['Proxmox VE', 'Docker', 'Linux', 'VMs', 'LXC Containers'] },
  { category: 'Data & Backend', items: ['SQLite', 'PDF Parsing', 'REST APIs', 'Data Pipelines', 'Web Scraping'] },
  { category: 'Tools', items: ['Git', 'Vim', 'Cloudflare', 'Gunicorn', 'systemd'] },
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
          <div className="space-y-5">
              <p className="text-gray-300 text-lg leading-relaxed">
                I'm <span className="text-white font-semibold">Gavin Joseph</span>, an engineering student at <span className="text-galaxy-300 font-semibold">Federal Institute of Science and Technology (FISAT)</span>, Kerala, studying <span className="text-galaxy-300 font-semibold">Electrical & Electronics Engineering</span>. I build things — from full-stack web apps to IoT devices that run in the real world.
              </p>
              <p className="text-gray-400 leading-relaxed">
                I run a <span className="text-galaxy-300 font-semibold">Proxmox virtualization lab</span> at home with <span className="text-galaxy-300 font-semibold">Home Assistant</span> powering my smart home, <span className="text-galaxy-300 font-semibold">Frigate NVR</span> with custom-trained <span className="text-galaxy-300 font-semibold">YOLOv9 models</span> for real-time object detection, and various <span className="text-galaxy-300 font-semibold">ESP32-based IoT devices</span> I designed and built myself — including an industrially tested water level sensor and an ultrasonic dog repeller.
              </p>
              <p className="text-gray-400 leading-relaxed">
                My flagship project, the <span className="text-galaxy-300 font-semibold">KEAM Allotment Helper</span>, helps thousands of engineering aspirants in Kerala navigate the college admission process. It parses 290K+ official CEE PDF documents into a searchable database with rank prediction, cutoff analysis, and migration tracking.
              </p>
              <p className="text-gray-400 leading-relaxed">
                I believe in building things that are fast, reliable, and genuinely useful. Whether it's a web dashboard, an IoT sensor, or a Proxmox VM — if it solves a real problem, I'm interested.
              </p>
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
