import { useRef } from 'react'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function useScrollTimelines() {
  const mainRef = useRef<HTMLElement>(null)

  useGSAP(
    () => {
      const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

      if (reduceMotion) {
        return
      }

      gsap.to('.signal-line', {
        scaleX: 1,
        transformOrigin: 'left center',
        ease: 'none',
        scrollTrigger: {
          trigger: '.signal-section',
          start: 'top 78%',
          end: 'bottom 40%',
          scrub: 0.9,
        },
      })

      gsap.utils.toArray<HTMLElement>('.project-card').forEach((card) => {
        gsap.fromTo(
          card,
          { y: 46, opacity: 0.35 },
          {
            y: 0,
            opacity: 1,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: card,
              start: 'top 86%',
              end: 'top 55%',
              scrub: 0.8,
            },
          },
        )
      })
    },
    { scope: mainRef },
  )

  return mainRef
}
