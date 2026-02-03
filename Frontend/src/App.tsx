import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { Toaster } from 'react-hot-toast'
import LandingPage from './pages/LandingPage'
import HomePage from './pages/HomePage'
import StoryPage from './pages/StoryPage'
import StoryReadPage from './pages/StoryReadPage'
import StoryTreePage from './pages/StoryTreePage'
import CreateStoryPage from './pages/CreateStoryPage'
import LibraryPage from './pages/LibraryPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import Layout from './components/layout/Layout'
import { ProtectedRoute } from './components/auth'

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Toaster
          position="top-right"
          toastOptions={{
            className: 'bg-story-muted border border-story-border text-gray-100',
            duration: 4000,
            style: {
              background: '#1a1a2e',
              color: '#f3f4f6',
              border: '1px solid #2a2a3e',
            },
          }}
        />
        <AnimatePresence mode="wait">
          <Routes>
            {/* Public landing page */}
            <Route path="/" element={<LandingPage />} />
            
            {/* Auth routes - no layout */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            
            {/* Protected routes with layout */}
            <Route path="/app" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
              <Route index element={<HomePage />} />
              <Route path="create" element={<CreateStoryPage />} />
              <Route path="library" element={<LibraryPage />} />
              <Route path="story/:storyId" element={<StoryPage />} />
              <Route path="story/:storyId/read" element={<StoryReadPage />} />
              <Route path="story/:storyId/tree" element={<StoryTreePage />} />
            </Route>
          </Routes>
        </AnimatePresence>
      </div>
    </Router>
  )
}

export default App
