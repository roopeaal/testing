import { SectionHeader } from '../components/SectionHeader'
import { Reveal } from '../components/Reveal'
import { experience, strengths } from '../data/portfolio'

export function Skills() {
  return (
    <section id="skills" className="border-y border-white/10 bg-ash px-5 py-24 sm:px-8 sm:py-32 lg:px-10">
      <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.82fr_1.18fr]">
        <SectionHeader
          kicker="Experience and skills"
          title="Developing breadth, with method."
          body="Current strength: learn the system, verify behavior, document what happened, and improve the implementation one constraint at a time."
        />
        <div className="grid gap-8">
          <div className="grid gap-px bg-white/10">
            {experience.map((item) => (
              <Reveal key={item.title} className="bg-ash p-6">
                <div className="grid gap-4 md:grid-cols-[0.34fr_0.66fr]">
                  <div>
                    <h3 className="text-xl font-semibold text-paper">{item.title}</h3>
                    <p className="mt-2 text-xs uppercase tracking-[0.2em] text-dim">{item.period}</p>
                  </div>
                  <p className="text-sm leading-7 text-muted">{item.detail}</p>
                </div>
              </Reveal>
            ))}
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {strengths.map((item) => {
              const Icon = item.icon

              return (
                <div key={item.title} className="flex items-center gap-4 border border-white/10 bg-[#10110f] p-4">
                  <Icon size={19} className="text-copper" />
                  <span className="font-medium text-paper">{item.title}</span>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
