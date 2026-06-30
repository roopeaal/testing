import { motion } from 'motion/react'
import { Bug, Cloud, FileText, Network, RadioTower, ShieldCheck } from 'lucide-react'
import { Reveal } from '../components/Reveal'

const practices = [
  {
    title: 'Network first',
    detail: 'Start from connectivity, routing, ports, and failure points before assuming the application is the problem.',
    icon: Network,
  },
  {
    title: 'Device to service',
    detail: 'Think through how sensor data, edge devices, APIs, and hosted services move information end to end.',
    icon: RadioTower,
  },
  {
    title: 'Verify locally',
    detail: 'Prefer repeatable checks, small scripts, and documented baselines over vague manual confidence.',
    icon: ShieldCheck,
  },
  {
    title: 'Report clearly',
    detail: 'Write down setup, assumptions, test steps, and observed behavior so the next change has context.',
    icon: FileText,
  },
]

const flow = [
  { label: 'Observe', icon: Bug },
  { label: 'Isolate', icon: Network },
  { label: 'Validate', icon: ShieldCheck },
  { label: 'Document', icon: FileText },
  { label: 'Improve', icon: Cloud },
]

export function Systems() {
  return (
    <section id="systems" className="relative overflow-hidden border-y border-white/10 bg-[#0a0b09] px-5 py-24 sm:px-8 sm:py-32 lg:px-10">
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(120deg,rgba(255,255,255,0.055)_1px,transparent_1px),linear-gradient(180deg,rgba(214,155,99,0.08),transparent_42%)] bg-[size:92px_92px,100%_100%]" />
      <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.92fr_1.08fr] lg:items-start">
        <Reveal className="max-w-2xl">
          <p className="mb-4 text-xs font-semibold uppercase tracking-[0.28em] text-copper">
            Systems practice
          </p>
          <h2 className="text-balance text-4xl font-semibold leading-[0.96] text-paper sm:text-6xl">
            The portfolio is about how Roope approaches technical problems.
          </h2>
          <p className="mt-6 text-base leading-8 text-muted">
            The through-line is practical: understand the system, reduce the unknowns,
            test the behavior, and leave the work easier to continue.
          </p>
        </Reveal>

        <div className="grid gap-5">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-16%' }}
            transition={{ duration: 0.68, ease: [0.22, 1, 0.36, 1] }}
            className="relative overflow-hidden border border-white/10 bg-graphite p-5 sm:p-7"
          >
            <div className="absolute left-0 top-0 h-full w-px bg-copper/60" />
            <div className="grid gap-3 sm:grid-cols-5">
              {flow.map((item, index) => {
                const Icon = item.icon

                return (
                  <div key={item.label} className="relative border border-white/10 bg-[#0d0f0d] p-4">
                    <div className="mb-8 flex items-center justify-between">
                      <Icon size={18} className="text-copper" />
                      <span className="text-[0.65rem] font-semibold text-dim">0{index + 1}</span>
                    </div>
                    <p className="text-sm font-semibold text-paper">{item.label}</p>
                  </div>
                )
              })}
            </div>
          </motion.div>

          <div className="grid gap-4 sm:grid-cols-2">
            {practices.map((item, index) => {
              const Icon = item.icon

              return (
                <motion.article
                  key={item.title}
                  initial={{ opacity: 0, y: 22 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-14%' }}
                  transition={{ duration: 0.56, delay: index * 0.04, ease: [0.22, 1, 0.36, 1] }}
                  className="min-h-48 border border-white/10 bg-[#10120f] p-5 sm:p-6"
                >
                  <Icon size={22} className="text-copper" />
                  <h3 className="mt-9 text-xl font-semibold text-paper">{item.title}</h3>
                  <p className="mt-4 text-sm leading-7 text-muted">{item.detail}</p>
                </motion.article>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
