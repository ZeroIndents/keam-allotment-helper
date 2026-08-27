import React, { useState, useEffect, useRef } from 'react';

export default function Blog() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const sectionRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    fetch('/api/blogs')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setPosts(data);
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

  function renderContent(content) {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code style="background:rgba(124,58,237,0.15);padding:2px 6px;border-radius:4px;font-size:13px">$1</code>')
      .replace(/\n/g, '<br/>');
  }

  return (
    <section id="blog" ref={sectionRef} className="relative py-32 px-6">
      <div className="max-w-4xl mx-auto">
        <div
          className={`text-center mb-16 transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <span className="section-title">Blog</span>
          <h2 className="text-4xl sm:text-5xl font-black mt-4 mb-4">
            <span style={{color: 'var(--text-heading)'}}>Latest </span>
            <span className="text-gradient">Writeups</span>
          </h2>
          <p className="text-lg max-w-xl mx-auto" style={{color: 'var(--text-secondary)'}}>
            Thoughts on IoT, AI, and building things that matter.
          </p>
        </div>

        {loading ? (
          <div className="space-y-5">
            {[1, 2].map((i) => (
              <div key={i} className="glass-card p-8 animate-pulse">
                <div className="h-5 rounded w-1/2 mb-4" style={{background: 'var(--accent-glow)'}} />
                <div className="h-3 rounded w-full mb-2" style={{background: 'var(--accent-glow)'}} />
                <div className="h-3 rounded w-3/4" style={{background: 'var(--accent-glow)'}} />
              </div>
            ))}
          </div>
        ) : posts.length > 0 ? (
          <div className="space-y-5">
            {posts.map((post, i) => (
              <div
                key={post.id}
                className={`glass-card p-8 transition-all duration-500 ${
                  isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
                }`}
                style={{ transitionDelay: `${200 + i * 80}ms` }}
              >
                <div className="flex items-center gap-3 mb-3 flex-wrap">
                  <span className="text-xs text-gray-500">
                    {new Date(post.created_at).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                    })}
                  </span>
                  <span className="text-xs text-gray-600">·</span>
                  <span className="text-xs text-gray-500">{post.read_time || '3 min read'}</span>
                </div>
                <h3 className="text-xl font-bold mb-3" style={{color: 'var(--text-heading)'}}>{post.title}</h3>                <div className="text-sm leading-relaxed mb-4"
                  dangerouslySetInnerHTML={{
                    __html: renderContent(
                      post.content.length > 300
                        ? post.content.slice(0, 300) + '...'
                        : post.content
                    ),
                  }}
                />
                {post.tags && post.tags.length > 0 && (
                  <div className="flex gap-2 flex-wrap">
                    {post.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-[11px] px-3 py-1 rounded-full" style={{background: 'var(--skill-badge-bg)', color: 'var(--text-accent)', border: '1px solid var(--skill-badge-border)'}}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 glass-card">
            <div className="text-4xl mb-4">📝</div>
            <p className="text-lg mb-2" style={{color: 'var(--text-secondary)'}}>No posts yet</p>
            <p className="text-sm" style={{color: 'var(--text-muted)'}}>
              Blog posts will appear here once published.
              <br />
              <a
                href="/admin/blogs"
                className="hover:underline mt-2 inline-block" style={{color: 'var(--text-accent)'}}
              >
                Write your first post →
              </a>
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
