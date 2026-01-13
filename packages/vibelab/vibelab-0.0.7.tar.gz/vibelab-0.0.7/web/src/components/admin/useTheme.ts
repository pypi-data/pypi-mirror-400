import { useState, useEffect } from 'react'

/**
 * Hook to detect current theme from document data-theme attribute
 */
export function useTheme(): 'light' | 'dark' {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')
  
  useEffect(() => {
    const updateTheme = () => {
      const dataTheme = document.documentElement.getAttribute('data-theme')
      if (dataTheme === 'light' || dataTheme === 'dark') {
        setTheme(dataTheme)
      } else {
        // Check system preference
        setTheme(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      }
    }
    
    updateTheme()
    
    // Watch for theme changes
    const observer = new MutationObserver(updateTheme)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    
    // Also watch for system preference changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', updateTheme)
    
    return () => {
      observer.disconnect()
      mediaQuery.removeEventListener('change', updateTheme)
    }
  }, [])
  
  return theme
}

