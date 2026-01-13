import { useLayoutEffect, useRef, useState } from 'react'

export interface ElementSize {
  width: number
  height: number
}

export function useElementSize<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)
  const [size, setSize] = useState<ElementSize>({ width: 0, height: 0 })

  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return

    const ro = new ResizeObserver((entries) => {
      const entry = entries[0]
      if (!entry) return
      const cr = entry.contentRect
      setSize({ width: Math.round(cr.width), height: Math.round(cr.height) })
    })

    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  return { ref, size }
}




