import { Mail } from 'lucide-react'
import { Reveal } from '../components/Reveal'

export function Contact() {
  return (
    <footer id="contact" className="px-5 py-20 sm:px-8 sm:py-28 lg:px-10">
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[1fr_0.48fr] lg:items-end">
        <Reveal>
          <p className="mb-4 text-xs font-semibold uppercase tracking-[0.32em] text-copper">
            Contact
          </p>
          <h2 className="max-w-5xl text-balance text-4xl font-semibold leading-[0.95] text-paper sm:text-7xl">
            Open to practical technical work, testing tasks, and junior developer opportunities.
          </h2>
        </Reveal>
        <Reveal delay={0.08} className="border border-white/10 bg-graphite p-6">
          <Mail className="mb-12 text-copper" size={24} />
          <p className="text-base leading-8 text-muted">
            Best fit: technical teams that value clear documentation, careful validation,
            and steady improvement.
          </p>
          <p className="mt-8 border-t border-white/10 pt-5 text-sm leading-7 text-soft">
            For contact, use the email or profile link shared with this portfolio.
          </p>
        </Reveal>
      </div>
    </footer>
  )
}
