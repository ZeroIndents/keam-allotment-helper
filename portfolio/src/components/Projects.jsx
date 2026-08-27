import React, { useState, useEffect, useRef } from 'react';

const GITHUB_USERNAME = 'gavinjoseph';

const LANGUAGE_COLORS = {
  Python: '#3572A5',
  JavaScript: '#f1e05a',
  TypeScript: '#3178c6',
  HTML: '#e34c26',
  CSS: '#563d7c',
  Shell: '#89e051',
  'Jupyter Notebook': '#DA5B0B',
  Dockerfile: '#384d54',
  Makefile: '#427819',
};

export default function Projects({ onSelectProject }) {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const sectionRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    fetch(`https://api.github.com/users/${GITHUB_USERNAME}/repos?sort=updated&per_page=30`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setRepos(data.filter((r) => !r.fork));
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

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

  const languages = ['all', ...new Set(repos.map((r) => r.language).filter(Boolean))];

  const filtered = filter === 'all' ? repos : repos.filter((r) => r.language === filter);

  return (
    <section id="projects" ref={sectionRef} className="relative py-32 px-6">
      <div className="max-w-6xl mx-auto">
        <div
          className={`text-center mb-16 transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <span className="section-title">Portfolio</span>
          <h2 className="text-4xl sm:text-5xl font-black mt-4 mb-4">
            <span className="text-white">My </span>
            <span className="text-gradient">Projects</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            Open-source work and experiments — all available on GitHub.
          </p>
        </div>

        {/* Language filter pills */}
        <div
          className={`flex flex-wrap justify-center gap-2 mb-12 transition-all duration-700 delay-200 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          {languages.slice(0, 8).map((lang) => (
            <button
              key={lang}
              onClick={() => setFilter(lang)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                filter === lang
                  ? 'bg-galaxy-500/30 text-galaxy-200 border border-galaxy-400/40'
                  : 'glass text-gray-400 hover:text-white hover:border-gray-500'
              }`}
            >
              {lang === 'all' ? 'All' : lang}
              {lang !== 'all' && (
                <span
                  className="inline-block w-2 h-2 rounded-full ml-2"
                  style={{ background: LANGUAGE_COLORS[lang] || '#8b8b8b' }}
                />
              )}
            </button>
          ))}
        </div>

        {/* Projects grid */}
        {loading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="glass-card p-6 animate-pulse">
                <div className="h-4 bg-white/5 rounded w-3/4 mb-4" />
                <div className="h-3 bg-white/5 rounded w-full mb-2" />
                <div className="h-3 bg-white/5 rounded w-2/3 mb-4" />
                <div className="flex gap-2">
                  <div className="h-5 bg-white/5 rounded-full w-12" />
                  <div className="h-5 bg-white/5 rounded-full w-16" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((repo, i) => (
              <ProjectCard
                key={repo.id}
                repo={repo}
                index={i}
                isVisible={isVisible}
                onClick={() => onSelectProject(repo)}
              />
            ))}
          </div>
        )}

        {!loading && filtered.length === 0 && (
          <div className="text-center py-16 text-gray-500">
            <p className="text-lg">No projects found for this filter.</p>
          </div>
        )}

        {!loading && repos.length > 0 && (
          <div
            className={`text-center mt-12 transition-all duration-700 delay-500 ${
              isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
            }`}
          >
            <a
              href={`https://github.com/${GITHUB_USERNAME}?tab=repositories`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              View All on GitHub →
            </a>
          </div>
        )}
      </div>
    </section>
  );
}

function ProjectCard({ repo, index, isVisible, onClick }) {
  return (
    <div
      className={`glass-card shimmer p-6 cursor-pointer group transition-all duration-500 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      }`}
      style={{ transitionDelay: `${200 + index * 60}ms` }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-base font-bold text-white group-hover:text-galaxy-300 transition-colors truncate pr-2">
          {repo.name}
        </h3>
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="w-4 h-4 text-gray-600 group-hover:text-galaxy-400 transition-colors flex-shrink-0 mt-1"
        >
          <path d="M7 17L17 7M17 7H7M17 7v10" />
        </svg>
      </div>

      <p className="text-sm text-gray-400 leading-relaxed mb-4 line-clamp-2 min-h-[2.5rem]">
        {repo.description || 'No description provided.'}
      </p>

      <div className="flex items-center gap-3 flex-wrap">
        {repo.language && (
          <span
            className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full"
            style={{
              background: `${LANGUAGE_COLORS[repo.language] || '#8b8b8b'}15`,
              color: LANGUAGE_COLORS[repo.language] || '#8b8b8b',
            }}
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{ background: LANGUAGE_COLORS[repo.language] || '#8b8b8b' }}
            />
            {repo.language}
          </span>
        )}

        {repo.stargazers_count > 0 && (
          <span className="inline-flex items-center gap-1 text-xs text-gray-500">
            ⭐ {repo.stargazers_count}
          </span>
        )}

        {repo.forks_count > 0 && (
          <span className="inline-flex items-center gap-1 text-xs text-gray-500">
            🍴 {repo.forks_count}
          </span>
        )}

        {repo.topics && repo.topics.length > 0 && (
          <div className="flex gap-1 flex-wrap mt-1">
            {repo.topics.slice(0, 3).map((topic) => (
              <span
                key={topic}
                className="text-[10px] px-2 py-0.5 rounded-full bg-galaxy-500/10 text-galaxy-300 border border-galaxy-500/20"
              >
                {topic}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
