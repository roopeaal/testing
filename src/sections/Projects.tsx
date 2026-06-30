import { ArrowUpRight } from 'lucide-react'
import { SectionHeader } from '../components/SectionHeader'
import { projects } from '../data/portfolio'

export function Projects() {
  return (
    <section id="projects" className="mx-auto max-w-7xl px-5 py-24 sm:px-8 sm:py-32 lg:px-10">
      <div className="mb-14 flex flex-col justify-between gap-6 md:flex-row md:items-end">
        <SectionHeader
          kicker="Projects"
          title="Real builds and learning projects, without inflated packaging."
          body="Each card explains what the project is, what it exercises, and where it sits today, with the emphasis on practical learning and technical clarity."
        />
        <a
          href="#contact"
          className="inline-flex items-center gap-3 border-b border-copper pb-2 text-sm font-medium text-paper"
        >
          Get in touch
          <ArrowUpRight size={16} />
        </a>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {projects.map((project, index) => (
          <article key={project.title} className="project-card border border-white/10 bg-graphite p-6 sm:p-7">
            <div className="mb-10 flex items-start justify-between gap-6">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-copper">
                  {project.label}
                </p>
                <h3 className="mt-4 text-2xl font-semibold leading-tight text-paper sm:text-3xl">
                  {project.title}
                </h3>
              </div>
              <span className="shrink-0 border border-white/10 px-3 py-1 text-xs text-soft">
                {project.status}
              </span>
            </div>
            <p className="max-w-xl text-base leading-8 text-muted">{project.description}</p>
            <div className="mt-6 border-l border-copper/50 pl-4 text-sm leading-7 text-soft">
              {project.note}
            </div>
            <div className="mt-8 flex flex-wrap gap-2">
              {project.stack.map((item) => (
                <span key={item} className="bg-white/[0.045] px-3 py-1 text-xs text-soft">
                  {item}
                </span>
              ))}
            </div>
            <div className="mt-10 flex items-center justify-between border-t border-white/10 pt-4 text-xs text-dim">
              <span>Project 0{index + 1}</span>
              <span>Roope Aaltonen</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
