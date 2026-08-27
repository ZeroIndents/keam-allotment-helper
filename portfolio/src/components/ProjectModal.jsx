import React, { useEffect } from 'react';

export default function ProjectModal({ project, onClose }) {
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleEsc);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="p-6 border-b" style={{borderColor: 'var(--border-subtle)'}}>
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold mb-1" style={{color: 'var(--text-heading)'}}>
                {project.name}
              </h2>
              {project.description && (
                <p className="text-sm" style={{color: 'var(--text-secondary)'}}>{project.description}</p>
              )}
            </div>
            <button
              onClick={onClose}
              className="transition-colors p-1 -m-1"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3">
            {project.language && (
              <div className="glass rounded-xl p-3 text-center">
                <div className="text-sm font-bold" style={{color: 'var(--text-heading)'}}>{project.language}</div>
                <div className="text-[10px] uppercase tracking-wider mt-1" style={{color: 'var(--text-muted)'}}>Language</div>
              </div>
            )}
            <div className="glass rounded-xl p-3 text-center">
              <div className="text-sm font-bold" style={{color: 'var(--text-heading)'}}>⭐ {project.stargazers_count}</div>
              <div className="text-[10px] uppercase tracking-wider mt-1" style={{color: 'var(--text-muted)'}}>Stars</div>
            </div>
            <div className="glass rounded-xl p-3 text-center">
              <div className="text-sm font-bold" style={{color: 'var(--text-heading)'}}>🍴 {project.forks_count}</div>
              <div className="text-[10px] uppercase tracking-wider mt-1" style={{color: 'var(--text-muted)'}}>Forks</div>
            </div>
          </div>

          {/* Topics */}
          {project.topics && project.topics.length > 0 && (
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider mb-2" style={{color: 'var(--text-muted)'}}>
                Topics
              </h4>
              <div className="flex flex-wrap gap-2">
                {project.topics.map((topic) => (
                  <span
                    key={topic}
                    className="text-xs px-3 py-1 rounded-full" style={{background: 'var(--skill-badge-bg)', color: 'var(--text-accent)', border: '1px solid var(--skill-badge-border)'}}
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Details */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span style={{color: 'var(--text-muted)'}}>Created</span>
              <span className="font-medium" style={{color: 'var(--text-primary)'}}>{formatDate(project.created_at)}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span style={{color: 'var(--text-muted)'}}>Last Updated</span>
              <span className="font-medium" style={{color: 'var(--text-primary)'}}>{formatDate(project.updated_at)}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span style={{color: 'var(--text-muted)'}}>Size</span>
              <span className="font-medium" style={{color: 'var(--text-primary)'}}>{(project.size / 1024).toFixed(1)} MB</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span style={{color: 'var(--text-muted)'}}>License</span>
              <span className="font-medium" style={{color: 'var(--text-primary)'}}>{project.license?.name || 'None'}</span>
            </div>
            {project.homepage && (
              <div className="flex items-center justify-between text-sm">
                <span style={{color: 'var(--text-muted)'}}>Website</span>
                <a
                  href={project.homepage}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium"
                >
                  {project.homepage}
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t flex gap-3" style={{borderColor: 'var(--border-subtle)'}}>
          <a
            href={project.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary flex-1 justify-center"
          >
            View on GitHub →
          </a>
          {project.homepage && (
            <a
              href={project.homepage}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary flex-1 justify-center"
            >
              Live Demo →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
