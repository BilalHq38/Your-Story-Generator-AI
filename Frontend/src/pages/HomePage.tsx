import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Sparkles, BookOpen, Wand2, GitBranch, Users } from 'lucide-react'
import { Button, Card, LoadingSpinner } from '@/components/ui'
import { StoryCard } from '@/components/story'
import { storyApi } from '@/api'

const features = [
  {
    icon: Wand2,
    title: 'AI-Powered Stories',
    description: 'Advanced AI creates unique, engaging narratives tailored to your choices.',
  },
  {
    icon: Users,
    title: 'Unique Narrators',
    description: 'Choose from 5 distinct narrator personas, each with their own storytelling style.',
  },
  {
    icon: GitBranch,
    title: 'Branching Paths',
    description: 'Every choice matters. Explore different storylines and endings.',
  },
]

export default function HomePage() {
  const { data: storiesData, isLoading } = useQuery({
    queryKey: ['stories', 'recent'],
    queryFn: () => storyApi.getStories(1, 3),
  })

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 md:py-32 overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 bg-gradient-radial from-story-accent/10 via-transparent to-transparent" />
        <div className="absolute top-20 left-1/4 w-72 h-72 bg-story-accent/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-story-accent/10 border border-story-accent/30 text-story-accent text-sm mb-8">
              <Sparkles className="w-4 h-4" />
              AI-Powered Interactive Fiction
            </div>

            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6">
              Your Story,{' '}
              <span className="text-gradient">Your Choices</span>
            </h1>

            <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10">
              Immerse yourself in AI-generated adventures where every decision shapes your unique narrative. 
              Choose your narrator, set the atmosphere, and let the story unfold.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/create">
                <Button size="lg" leftIcon={<Wand2 className="w-5 h-5" />}>
                  Create Your Story
                </Button>
              </Link>
              <Link to="/library">
                <Button variant="secondary" size="lg" leftIcon={<BookOpen className="w-5 h-5" />}>
                  Browse Stories
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 border-t border-story-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              What Makes Us Different
            </h2>
            <p className="text-gray-400 max-w-xl mx-auto">
              Experience storytelling like never before with our unique features
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Card className="h-full text-center">
                  <div className="inline-flex p-3 rounded-xl bg-story-accent/20 text-story-accent mb-4">
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 text-sm">
                    {feature.description}
                  </p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Recent Stories Section */}
      <section className="py-20 border-t border-story-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-white">
              Recent Adventures
            </h2>
            <Link to="/library">
              <Button variant="ghost" size="sm">
                View All →
              </Button>
            </Link>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner text="Loading stories..." />
            </div>
          ) : storiesData?.items && storiesData.items.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {storiesData.items.map((story) => (
                <StoryCard key={story.id} story={story} />
              ))}
            </div>
          ) : (
            <Card className="text-center py-12">
              <BookOpen className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-300 mb-2">
                No stories yet
              </h3>
              <p className="text-gray-500 mb-6">
                Be the first to create an adventure!
              </p>
              <Link to="/create">
                <Button leftIcon={<Wand2 className="w-4 h-4" />}>
                  Create Story
                </Button>
              </Link>
            </Card>
          )}
        </div>
      </section>
    </div>
  )
}
