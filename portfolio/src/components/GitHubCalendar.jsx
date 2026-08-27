import React, { useRef, useState, useEffect } from 'react';

const API_URL = '/api/github/contributions/ZeroIndents';

const LEVEL_COLORS = [
  '#161b22', // no contributions
  '#0e4429', // level 1
  '#006d32', // level 2
  '#26a641', // level 3
  '#39d353', // level 4
];

const DARK_LEVEL_COLORS = [
  '#161b22',
  '#0e4429',
  '#006d32',
  '#26a641',
  '#39d353',
];

function getWeeks(contributions) {
  if (!contributions || contributions.length === 0) return [];
  
  const weeks = [];
  let currentWeek = [];
  
  // Pad start to align with Monday
  const firstDate = new Date(contributions[0].date);
  const dayOfWeek = firstDate.getDay();
  const mondayOffset = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
  
  for (let i = 0; i < mondayOffset; i++) {
    currentWeek.push(null);
  }
  
  for (const day of contributions) {
    currentWeek.push(day);
    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  }
  
  if (currentWeek.length > 0) {
    while (currentWeek.length < 7) currentWeek.push(null);
    weeks.push(currentWeek);
  }
  
  return weeks;
}

function getMonthLabels(weeks) {
  const labels = [];
  let lastMonth = -1;
  
  weeks.forEach((week, i) => {
    const firstDay = week.find(d => d !== null);
    if (firstDay) {
      const month = new Date(firstDay.date).getMonth();
      if (month !== lastMonth) {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        labels.push({ index: i, label: monthNames[month] });
        lastMonth = month;
      }
    }
  });
  
  return labels;
}

export default function GitHubGraph() {
  const sectionRef = useRef(null);
  const [isVisible, setIsVisible] = useState(false);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

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
    fetch(API_URL)
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, []);

  const weeks = data ? getWeeks(data.contributions) : [];
  const monthLabels = getMonthLabels(weeks);
  const total = data?.total?.[new Date().getFullYear()] || 0;

  return (
    <section ref={sectionRef} className="relative py-20 px-6">
      <div className="max-w-4xl mx-auto">
        <div
          className={`transition-all duration-700 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="text-center mb-8">
            <span className="section-title">Activity</span>
            <h2 className="text-3xl sm:text-4xl font-black mt-3 mb-2">
              <span className="text-white">GitHub </span>
              <span className="text-gradient">Contributions</span>
            </h2>
            <p className="text-gray-400 text-sm">
              {loading ? 'Loading...' : error ? 'Could not load contributions' : `${total} contributions in the last year`}
            </p>
          </div>

          <div className="glass-card p-6 sm:p-8 overflow-x-auto">
            {loading ? (
              <div className="flex items-center justify-center h-32">
                <div className="w-6 h-6 border-2 border-galaxy-400 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : error ? (
              <div className="text-center text-gray-500 py-8">
                <p className="text-2xl mb-2">📊</p>
                <p>GitHub contributions couldn't be loaded right now.</p>
                <a href="https://github.com/ZeroIndents" target="_blank" rel="noopener noreferrer" className="text-galaxy-400 text-sm mt-2 inline-block hover:underline">
                  View profile →
                </a>
              </div>
            ) : (
              <div className="min-w-[700px]">
                {/* Month labels */}
                <div className="flex mb-1 ml-8">
                  {monthLabels.map((m, i) => (
                    <div
                      key={i}
                      className="text-[10px] text-gray-500"
                      style={{
                        position: 'relative',
                        left: `${m.index * 16}px`,
                        width: 0,
                      }}
                    >
                      {m.label}
                    </div>
                  ))}
                </div>

                <div className="flex gap-0">
                  {/* Day labels */}
                  <div className="flex flex-col gap-[3px] mr-1 justify-center">
                    {['', 'Mon', '', 'Wed', '', 'Fri', ''].map((d, i) => (
                      <div key={i} className="text-[10px] text-gray-500 h-[12px] leading-[12px]">
                        {d}
                      </div>
                    ))}
                  </div>

                  {/* Grid */}
                  <div className="flex gap-[3px]">
                    {weeks.map((week, wi) => (
                      <div key={wi} className="flex flex-col gap-[3px]">
                        {week.map((day, di) => (
                          <div
                            key={di}
                            className="w-[12px] h-[12px] rounded-[2px] transition-colors duration-200 hover:ring-1 hover:ring-white/30"
                            style={{
                              backgroundColor: day
                                ? DARK_LEVEL_COLORS[day.level]
                                : DARK_LEVEL_COLORS[0],
                            }}
                            title={
                              day
                                ? `${day.count} contribution${day.count !== 1 ? 's' : ''} on ${day.date}`
                                : ''
                            }
                          />
                        ))}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Legend */}
                <div className="flex items-center justify-end gap-1 mt-3 text-[10px] text-gray-500">
                  <span>Less</span>
                  {DARK_LEVEL_COLORS.map((color, i) => (
                    <div
                      key={i}
                      className="w-[12px] h-[12px] rounded-[2px]"
                      style={{ backgroundColor: color }}
                    />
                  ))}
                  <span>More</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
