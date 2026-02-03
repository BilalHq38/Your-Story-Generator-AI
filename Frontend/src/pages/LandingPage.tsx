import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { BookOpen, Sparkles, TreePine, Mail, Linkedin, Github, Heart, Zap, Globe, Menu, X } from 'lucide-react'
import { Button } from '@/components/ui'

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Close mobile menu with Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false)
      }
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [mobileMenuOpen])

  // Smooth scroll to section
  const scrollToSection = (sectionId: string) => {
    setMobileMenuOpen(false)
    const element = document.getElementById(sectionId)
    if (element) {
      const offset = 80 // Account for fixed navbar
      const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
      window.scrollTo({
        top: elementPosition - offset,
        behavior: 'smooth'
      })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-story-bg via-story-muted to-story-bg">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-story-bg/80 backdrop-blur-lg border-b border-story-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <motion.div 
              className="flex items-center gap-2"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <BookOpen className="w-8 h-8 text-story-accent" />
              <span className="text-xl font-bold text-white">Story Generator AI</span>
            </motion.div>
            
            {/* Desktop Navigation */}
            <motion.div 
              className="hidden md:flex items-center gap-4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <button 
                onClick={() => scrollToSection('about')} 
                className="text-gray-300 hover:text-white transition-colors"
              >
                About
              </button>
              <button 
                onClick={() => scrollToSection('features')} 
                className="text-gray-300 hover:text-white transition-colors"
              >
                Features
              </button>
              <button 
                onClick={() => scrollToSection('contact')} 
                className="text-gray-300 hover:text-white transition-colors"
              >
                Contact
              </button>
              <Link to="/login">
                <Button variant="secondary" size="sm">Login</Button>
              </Link>
              <Link to="/signup">
                <Button size="sm">Get Started</Button>
              </Link>
            </motion.div>

            {/* Mobile Menu Button */}
            <motion.button
              className="md:hidden text-white p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </motion.button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <motion.div
              className="md:hidden py-4 border-t border-story-border"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <div className="flex flex-col gap-3">
                <button 
                  onClick={() => scrollToSection('about')} 
                  className="text-gray-300 hover:text-white transition-colors text-left py-2"
                >
                  About
                </button>
                <button 
                  onClick={() => scrollToSection('features')} 
                  className="text-gray-300 hover:text-white transition-colors text-left py-2"
                >
                  Features
                </button>
                <button 
                  onClick={() => scrollToSection('contact')} 
                  className="text-gray-300 hover:text-white transition-colors text-left py-2"
                >
                  Contact
                </button>
                <div className="flex flex-col gap-2 pt-2">
                  <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="secondary" size="sm" className="w-full">Login</Button>
                  </Link>
                  <Link to="/signup" onClick={() => setMobileMenuOpen(false)}>
                    <Button size="sm" className="w-full">Get Started</Button>
                  </Link>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div 
            className="text-center max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              Create Your Own
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-story-accent to-purple-400">
                Interactive Adventures
              </span>
            </h1>
            <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto">
              Powered by advanced AI, craft unique branching stories where every choice matters. 
              Your imagination is the only limit.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/signup">
                <Button size="lg" className="text-lg px-8 py-6">
                  <Sparkles className="w-5 h-5 mr-2" />
                  Start Creating Free
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="secondary" className="text-lg px-8 py-6">
                  Sign In
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Hero Visual */}
          <motion.div 
            className="mt-16 relative"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
          >
            <div className="bg-gradient-to-br from-story-muted to-story-bg border border-story-border rounded-2xl p-8 shadow-2xl">
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-story-bg/50 rounded-lg p-6 border border-story-border hover:border-story-accent transition-colors">
                  <TreePine className="w-12 h-12 text-story-accent mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Branching Narratives</h3>
                  <p className="text-gray-400">Every choice creates a unique path through your story</p>
                </div>
                <div className="bg-story-bg/50 rounded-lg p-6 border border-story-border hover:border-story-accent transition-colors">
                  <Zap className="w-12 h-12 text-story-accent mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">AI-Powered</h3>
                  <p className="text-gray-400">Advanced language models bring your stories to life</p>
                </div>
                <div className="bg-story-bg/50 rounded-lg p-6 border border-story-border hover:border-story-accent transition-colors">
                  <Globe className="w-12 h-12 text-story-accent mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Multi-Language</h3>
                  <p className="text-gray-400">Create stories in multiple languages with audio narration</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 scroll-mt-20">
        <div className="max-w-7xl mx-auto">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-xl text-gray-400">Everything you need to create immersive interactive stories</p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                title: 'Real-Time Story Generation',
                description: 'Watch your story unfold in real-time with streaming AI generation',
                icon: Sparkles,
              },
              {
                title: 'Multiple Genres',
                description: 'Fantasy, Sci-Fi, Horror, Mystery, Romance, and more',
                icon: BookOpen,
              },
              {
                title: 'Story Branching',
                description: 'Create complex narrative trees with multiple endings',
                icon: TreePine,
              },
              {
                title: 'Voice Narration',
                description: 'Text-to-speech audio for immersive storytelling',
                icon: Zap,
              },
              {
                title: 'Story Library',
                description: 'Save and manage all your created adventures',
                icon: Heart,
              },
              {
                title: 'Multiple Atmospheres',
                description: 'Set the mood: Dark, Magical, Peaceful, Tense, or Whimsical',
                icon: Globe,
              },
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="bg-story-muted border border-story-border rounded-lg p-6 hover:border-story-accent transition-all hover:transform hover:scale-105"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
              >
                <feature.icon className="w-10 h-10 text-story-accent mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 px-4 sm:px-6 lg:px-8 bg-story-muted/30 scroll-mt-20">
        <div className="max-w-4xl mx-auto">
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">About Story Generator AI</h2>
            <p className="text-lg text-gray-300 mb-6 leading-relaxed">
              Story Generator AI is an innovative platform that combines the power of advanced artificial 
              intelligence with human creativity. We believe everyone has stories to tell, and our mission 
              is to provide the tools to bring those stories to life.
            </p>
            <p className="text-lg text-gray-300 leading-relaxed">
              Whether you're a writer looking for inspiration, an educator creating interactive learning 
              experiences, or simply someone who loves storytelling, our platform empowers you to create 
              engaging, branching narratives with just a few clicks.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 px-4 sm:px-6 lg:px-8 scroll-mt-20">
        <div className="max-w-4xl mx-auto">
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">Get In Touch</h2>
            <p className="text-lg text-gray-300 mb-10">
              Have questions or feedback? We'd love to hear from you!
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
              <a 
                href="mailto:mbilalhq4u@gmail.com"
                className="flex items-center gap-3 bg-story-muted border border-story-border rounded-lg px-6 py-4 hover:border-story-accent transition-colors group"
              >
                <Mail className="w-6 h-6 text-story-accent group-hover:scale-110 transition-transform" />
                <div className="text-left">
                  <div className="text-sm text-gray-400">Email</div>
                  <div className="text-white font-medium">mbilalhq4u@gmail.com</div>
                </div>
              </a>
              
              <a 
                href="https://linkedin.com/in/m-bilal-hashmi"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 bg-story-muted border border-story-border rounded-lg px-6 py-4 hover:border-story-accent transition-colors group"
              >
                <Linkedin className="w-6 h-6 text-story-accent group-hover:scale-110 transition-transform" />
                <div className="text-left">
                  <div className="text-sm text-gray-400">LinkedIn</div>
                  <div className="text-white font-medium">M Bilal Hashmi</div>
                </div>
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 sm:px-6 lg:px-8 border-t border-story-border">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <BookOpen className="w-6 h-6 text-story-accent" />
              <span className="text-gray-400">© 2026 Story Generator AI. All rights reserved.</span>
            </div>
            
            <div className="flex items-center gap-6">
              <a 
                href="mailto:mbilalhq4u@gmail.com"
                className="text-gray-400 hover:text-story-accent transition-colors"
                aria-label="Email"
              >
                <Mail className="w-5 h-5" />
              </a>
              <a 
                href="https://linkedin.com/in/m-bilal-hashmi"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-story-accent transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a 
                href="https://github.com/BilalHq38/Your-Story-Generator-AI"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-story-accent transition-colors"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
