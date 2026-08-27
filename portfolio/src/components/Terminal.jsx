import React, { useState, useRef, useEffect } from 'react';

const PROJECT_DETAILS = [
  {
    name: 'KEAM Allotment Helper',
    desc: 'Flask/SQLite app parsing 290K+ CEE Kerala allotment rows. Live at gavinjoseph.in/keam',
    link: '/keam/',
    tech: 'Python, Flask, SQLite, Jinja2',
  },
  {
    name: 'AppleMusic-Song-Downloader',
    desc: 'Download lossless ALAC, AAC 256kbps, or Dolby Atmos from Apple Music.',
    link: 'https://github.com/ZeroIndents/AppleMusic-Song-Downloader',
    tech: 'Python',
  },
  {
    name: 'Home Assistant + Frigate',
    desc: 'Smart home automation with Frigate NVR and custom-trained YOLOv9 object detection.',
    link: '',
    tech: 'Home Assistant, Frigate, YOLOv9, ESP32',
  },
  {
    name: 'Industrial Water Level Sensor',
    desc: 'Industrially tested IoT water level sensor — real-world deployment.',
    link: '',
    tech: 'ESP32, Sensors, IoT',
  },
  {
    name: 'Ultrasonic Dog Repeller',
    desc: 'Ultrasonic hardware device to safely repel dogs — designed and 3D-printed.',
    link: '',
    tech: 'Electronics, 3D Printing, Arduino',
  },
];

const COMMANDS = {
  help: 'Available commands:\n  help        — Show this message\n  about       — Who am I\n  projects    — List all projects\n  project <n> — Details for project #n (try: project 1)\n  skills      — My tech stack\n  keam        — KEAM Helper info\n  social      — All social links\n  clear       — Clear terminal\n  whoami      — Visitor info\n  neofetch    — System info',
  about: "I'm Gavin Joseph — EEE student at FISAT, Kerala. Developer & IoT enthusiast building tools that matter.\nCurrently building Home Assistant setups, Frigate configs, and more.",
  projects: PROJECT_DETAILS.map((p, i) => `${i + 1}. ${p.name}`).join('\n') + '\n\nType "project <number>" for details (e.g. project 1)',
  skills: 'Python · JavaScript · React · Flask · SQLite · ESP32 · Home Assistant · Docker · Linux · Tailwind CSS · Frigate · YOLOv9',
  keam: 'KEAM Allotment Helper: 290K+ rows, 142 colleges, 3 years of data.\nVisit: gavinjoseph.in/keam',
  social: 'GitHub: github.com/ZeroIndents\nLinkedIn: linkedin.com/in/gavin-joseph-792a433a8\nInstagram: instagram.com/gavin._.joseph\nEmail: gavinkalloor@gmail.com',
  clear: '__CLEAR__',
  whoami: 'gavin@fisat ~ $ You are a visitor exploring my portfolio! 🚀',
  neofetch: `       _____           gavin@portfolio
      /     \\          ─────────────────
     / () () \\         OS: Portfolio OS v1.0
    |  __^__  |        Host: gavinjoseph.in
    |_________|        Kernel: React 18 + Tailwind
     ||     ||         Shell: Interactive Terminal
     ||     ||         Theme: Galaxy Dark
                      Uptime: Since 2024`,
};

export default function Terminal() {
  const [lines, setLines] = useState([
    { type: 'system', text: 'Welcome to Gavin\'s Terminal! Type "help" to get started.' },
    { type: 'system', text: '─'.repeat(50) },
  ]);
  const [input, setInput] = useState('');
  const [history, setHistory] = useState([]);
  const [historyIdx, setHistoryIdx] = useState(-1);
  const inputRef = useRef(null);
  const termRef = useRef(null);
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

  useEffect(() => {
    if (termRef.current) {
      termRef.current.scrollTop = termRef.current.scrollHeight;
    }
  }, [lines]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const raw = input.trim();
    const cmd = raw.toLowerCase();
    if (!cmd) return;

    const newLines = [...lines, { type: 'input', text: `$ ${raw}` }];

    // Handle 'project <number>' command
    const projectMatch = cmd.match(/^project\s+(\d+)$/);
    if (projectMatch) {
      const idx = parseInt(projectMatch[1]) - 1;
      if (idx >= 0 && idx < PROJECT_DETAILS.length) {
        const p = PROJECT_DETAILS[idx];
        const detail = `${p.name}\n${p.desc}\nTech: ${p.tech}${p.link ? '\nLink: ' + p.link : ''}`;
        setLines([...newLines, { type: 'output', text: detail }]);
      } else {
        setLines([...newLines, { type: 'error', text: `No project #${projectMatch[1]}. There are ${PROJECT_DETAILS.length} projects. Try: projects` }]);
      }
    } else if (cmd === 'clear') {
      setLines([{ type: 'system', text: 'Terminal cleared. Type "help" for commands.' }]);
    } else if (COMMANDS[cmd]) {
      setLines([...newLines, { type: 'output', text: COMMANDS[cmd] }]);
    } else {
      setLines([...newLines, { type: 'error', text: `Command not found: ${cmd}. Type "help" for available commands.` }]);
    }

    setHistory((prev) => [cmd, ...prev]);
    setHistoryIdx(-1);
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIdx < history.length - 1) {
        const newIdx = historyIdx + 1;
        setHistoryIdx(newIdx);
        setInput(history[newIdx]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIdx > 0) {
        const newIdx = historyIdx - 1;
        setHistoryIdx(newIdx);
        setInput(history[newIdx]);
      } else {
        setHistoryIdx(-1);
        setInput('');
      }
    }
  };

  return (
    <section ref={sectionRef} className="relative py-20 px-6">
      <div className="max-w-3xl mx-auto">
        <div
          className={`transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="text-center mb-8">
            <span className="section-title">Interactive</span>
            <h2 className="text-3xl sm:text-4xl font-black mt-3 mb-2">
              <span className="text-white">Terminal</span>
            </h2>
            <p className="text-gray-400 text-sm">Type <code className="text-galaxy-300">help</code> to see what you can explore</p>
          </div>

          <div className="glass-card overflow-hidden">
            {/* Title bar */}
            <div className="flex items-center gap-2 px-4 py-3 bg-black/40 border-b border-white/5">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
              <span className="text-[11px] text-gray-500 ml-2 font-mono">gavin@portfolio ~ terminal</span>
            </div>

            {/* Terminal body */}
            <div
              ref={termRef}
              className="p-4 h-80 overflow-y-auto font-mono text-sm"
              onClick={() => inputRef.current?.focus()}
            >
              {lines.map((line, i) => (
                <div key={i} className={`mb-1 ${
                  line.type === 'input' ? 'text-galaxy-300' :
                  line.type === 'error' ? 'text-red-400' :
                  line.type === 'output' ? 'text-gray-300' :
                  'text-gray-500'
                }`}>
                  <pre className="whitespace-pre-wrap font-mono">{line.text}</pre>
                </div>
              ))}

              {/* Input line */}
              <form onSubmit={handleSubmit} className="flex items-center gap-2 mt-1">
                <span className="text-galaxy-300 font-mono">$</span>
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="flex-1 bg-transparent outline-none text-white font-mono caret-galaxy-400"
                  autoFocus
                  spellCheck={false}
                />
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
