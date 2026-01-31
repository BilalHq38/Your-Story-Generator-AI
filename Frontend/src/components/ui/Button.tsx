import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { forwardRef, ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      disabled,
      className = '',
      ...props
    },
    ref
  ) => {
    const baseStyles = `
      relative inline-flex items-center justify-center gap-2
      font-medium rounded-lg transition-all duration-200
      focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-story-dark
      disabled:opacity-50 disabled:cursor-not-allowed
    `

    const variantStyles = {
      primary: `
        bg-story-accent text-white
        hover:bg-story-accent-light
        focus:ring-story-accent
        btn-glow
      `,
      secondary: `
        bg-story-muted text-gray-200 border border-story-border
        hover:bg-story-border hover:border-story-accent/50
        focus:ring-story-accent/50
      `,
      ghost: `
        bg-transparent text-gray-300
        hover:bg-story-muted hover:text-white
        focus:ring-story-accent/30
      `,
      danger: `
        bg-red-600/20 text-red-400 border border-red-600/30
        hover:bg-red-600/30 hover:border-red-500
        focus:ring-red-500
      `,
    }

    const sizeStyles = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    }

    return (
      <motion.button
        ref={ref}
        className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
        disabled={disabled || isLoading}
        whileHover={{ scale: disabled ? 1 : 1.02 }}
        whileTap={{ scale: disabled ? 1 : 0.98 }}
        {...(props as any)}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          leftIcon
        )}
        {children}
        {rightIcon && !isLoading && rightIcon}
      </motion.button>
    )
  }
)

Button.displayName = 'Button'

export default Button
