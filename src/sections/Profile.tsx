import { Reveal } from '../components/Reveal'
import { SectionHeader } from '../components/SectionHeader'

export function Profile() {
  return (
    <section id="about" className="mx-auto grid max-w-7xl gap-10 px-5 py-24 sm:px-8 sm:py-32 lg:grid-cols-[0.78fr_1.22fr] lg:px-10">
      <SectionHeader
        kicker="About"
        title="A student portfolio with the volume turned down."
        body="The work is centered on understanding systems, validating assumptions, and making technical ideas clear enough to build, test, and improve."
      />
      <Reveal delay={0.08} className="grid gap-6 border-l border-white/10 pl-6 text-base leading-8 text-muted sm:pl-8">
        <p>
          I study ICT engineering at Metropolia University of Applied Sciences, with a
          focus on Smart IoT Systems, IoT, and Networks. I am especially interested in
          how connected devices, networked services, cloud environments, and software
          quality practices fit together in real projects.
        </p>
        <p>
          This portfolio is intentionally honest about level and scope. It presents
          practical student projects, prototypes, testing habits, cybersecurity curiosity,
          documentation, and modern web development as current work in progress.
        </p>
      </Reveal>
    </section>
  )
}
