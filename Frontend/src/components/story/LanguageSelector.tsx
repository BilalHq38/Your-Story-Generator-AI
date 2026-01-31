import { motion } from 'framer-motion'
import { STORY_LANGUAGES, StoryLanguage } from '@/types'

interface LanguageSelectorProps {
  value: StoryLanguage
  onChange: (language: StoryLanguage) => void
}

export default function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
  const languages = Object.entries(STORY_LANGUAGES) as [StoryLanguage, typeof STORY_LANGUAGES[StoryLanguage]][]

  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-2">Story Language</h2>
      <p className="text-sm text-gray-400 mb-6">
        Choose the language for your story narration
      </p>
      
      <div className="grid grid-cols-2 gap-4">
        {languages.map(([key, language]) => (
          <motion.button
            key={key}
            type="button"
            onClick={() => onChange(key)}
            className={`relative p-5 rounded-xl border-2 transition-all text-left ${
              value === key
                ? 'border-purple-500 bg-purple-500/10'
                : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {/* Selection indicator */}
            {value === key && (
              <motion.div
                className="absolute top-3 right-3 w-3 h-3 rounded-full bg-purple-500"
                layoutId="languageIndicator"
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              />
            )}

            {/* Language icon */}
            <div className="text-4xl mb-3">{language.icon}</div>
            
            {/* Language names */}
            <div className="mb-2">
              <h3 className={`text-lg font-semibold ${value === key ? 'text-purple-400' : 'text-white'}`}>
                {language.name}
              </h3>
              <p className={`text-base ${language.direction === 'rtl' ? 'font-urdu text-right' : ''}`}
                 style={{ fontFamily: language.direction === 'rtl' ? '"Noto Nastaliq Urdu", "Jameel Noori Nastaleeq", serif' : 'inherit' }}>
                {language.nativeName}
              </p>
            </div>
            
            {/* Description */}
            <p className={`text-sm ${value === key ? 'text-gray-300' : 'text-gray-500'} ${language.direction === 'rtl' ? 'text-right' : ''}`}
               style={{ fontFamily: language.direction === 'rtl' ? '"Noto Nastaliq Urdu", "Jameel Noori Nastaleeq", serif' : 'inherit' }}>
              {language.description}
            </p>
          </motion.button>
        ))}
      </div>
    </div>
  )
}
