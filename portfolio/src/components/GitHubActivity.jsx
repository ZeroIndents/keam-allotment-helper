import React, { useState, useEffect, useRef } from 'react';

const GITHUB_USERNAME = 'ZeroIndents';

const EVENT_ICONS = {
  PushEvent: '🔨',
  CreateEvent: '📦',
  ForkEvent: '🍴',
  IssuesEvent: '🐛',
  PullRequestEvent: '🔀',
  ReleaseEvent: '🏷️',
  WatchEvent: '⭐',
  DeleteEvent: '🗑️',
};

function timeAgo(dateStr) {
  const now = new Date();
  const date = new Date(dateStr);
  const seconds = Math.floor((now - date) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return `${Math.floor(days / 30)}mo ago`;
}

export default function GitHubActivity() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const sectionRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    fetch(`/api/github/users/${GITHUB_USERNAME}/events/public?per_page=15`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setEvents(data.slice(0, 8));
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

  function formatEvent(event) {
    const repo = event.repo?.name || '';
    switch (event.type) {
      case 'PushEvent':
        const commits = event.payload?.commits?.length || 0;
        return `Pushed ${commits} commit${commits !== 1 ? 's' : ''} to ${repo}`;
      case 'CreateEvent':
        return `Created ${event.payload?.ref_type} ${event.payload?.ref || ''} in ${repo}`;
      case 'ForkEvent':
        return `Forked ${repo}`;
      case 'IssuesEvent':
        return `${event.payload?.action} issue in ${repo}`;
      case 'PullRequestEvent':
        return `${event.payload?.action} pull request in ${repo}`;
      case 'WatchEvent':
        return `Starred ${repo}`;
      default:
        return `${event.type?.replace('Event', '')} on ${repo}`;
    }
  }

  return (
    <section ref={sectionRef} className="relative py-20 px-6">
      <div className="max-w-3xl mx-auto">
        <div
          className={`transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="text-center mb-8">
            <span className="section-title">Live</span>
            <h2 className="text-3xl sm:text-4xl font-black mt-3 mb-2">
              <span className="text-white">GitHub </span>
              <span className="text-gradient">Activity</span>
            </h2>
            <p className="text-gray-400 text-sm">Recent activity from my GitHub profile</p>
          </div>

          <div className="glass-card p-6">
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-12 bg-white/5 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : events.length > 0 ? (
              <div className="space-y-1">
                {events.map((event, i) => (
                  <div
                    key={event.id}
                    className={`flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors ${
                      isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4'
                    }`}
                    style={{ transitionDelay: `${100 + i * 60}ms` }}
                  >
                    <span className="text-lg flex-shrink-0">
                      {EVENT_ICONS[event.type] || '📌'}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-300 truncate">{formatEvent(event)}</p>
                    </div>
                    <span className="text-[11px] text-gray-600 flex-shrink-0">
                      {timeAgo(event.created_at)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500 text-sm py-4">No recent activity</p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
