import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import KeamShowcase from './components/KeamShowcase';
import Projects from './components/Projects';
import GitHubCalendar from './components/GitHubCalendar';
import GitHubActivity from './components/GitHubActivity';
import Timeline from './components/Timeline';
import Terminal from './components/Terminal';
import SkillsChart from './components/SkillsChart';
import About from './components/About';
import Blog from './components/Blog';
import Testimonials from './components/Testimonials';
import Contact from './components/Contact';
import Footer from './components/Footer';
import GalaxyBackground from './components/GalaxyBackground';
import ProjectModal from './components/ProjectModal';
import ScrollProgress from './components/ScrollProgress';
import CustomCursor from './components/CustomCursor';
import EasterEgg from './components/EasterEgg';

export default function App() {
  const [selectedProject, setSelectedProject] = useState(null);

  return (
    <div className="relative min-h-screen">
      <GalaxyBackground />
      <ScrollProgress />
      <CustomCursor />
      <EasterEgg />
      <div className="relative z-10">
        <Navbar />
        <Hero />
        <KeamShowcase />
        <Projects onSelectProject={setSelectedProject} />
        <GitHubCalendar />
        <GitHubActivity />
        <Timeline />
        <Terminal />
        <SkillsChart />
        <About />
        <Blog />
        <Testimonials />
        <Contact />
        <Footer />
      </div>
      {selectedProject && (
        <ProjectModal
          project={selectedProject}
          onClose={() => setSelectedProject(null)}
        />
      )}
    </div>
  );
}
