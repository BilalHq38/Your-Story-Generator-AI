import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  hoverable?: boolean
  onClick?: () => void
}

export default function Card({ 
  children, 
  className = '', 
  hoverable = false,
  onClick 
}: CardProps) {
  return (
    <motion.div
      className={`
        card-ambient p-6
        ${hoverable ? 'cursor-pointer hover:border-story-accent/50 hover:shadow-lg hover:shadow-story-accent/10' : ''}
        ${className}
      `}
      onClick={onClick}
      whileHover={hoverable ? { y: -4 } : undefined}
      whileTap={hoverable ? { scale: 0.98 } : undefined}
    >
      {children}
    </motion.div>
  )
}
