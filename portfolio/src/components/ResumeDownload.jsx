import React, { useRef, useState, useEffect } from 'react';

export default function ResumeDownload() {
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
      <div className="max-w-3xl mx-auto">
        <div
          className={`glass-card p-8 sm:p-12 text-center transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="text-5xl mb-4">📄</div>
          <h2 className="text-2xl sm:text-3xl font-black text-white mb-3">
            Download My Resume
          </h2>
          <p className="text-gray-400 mb-8 max-w-md mx-auto">
            Get a detailed overview of my skills, projects, and experience in a clean PDF format.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <a
              href="/resume.pdf"
              download
              className="btn-primary text-base"
            >
              📥 Download PDF
            </a>
            <a
              href="mailto:gavinkalloor@gmail.com?subject=Resume%20Request"
              className="btn-secondary text-base"
            >
              ✉️ Email Me
            </a>
          </div>

          <p className="text-[11px] text-gray-600 mt-6">
            Last updated: August 2026
          </p>
        </div>
      </div>
    </section>
  );
}
