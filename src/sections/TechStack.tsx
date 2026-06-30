import { motion } from 'motion/react'
import { SectionHeader } from '../components/SectionHeader'
import { stack } from '../data/portfolio'

export function TechStack() {
  return (
    <section id="stack" className="border-y border-white/10 bg-ash px-5 py-24 sm:px-8 sm:py-32 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionHeader
          kicker="Working stack"
          title="Tools and concepts tied to real troubleshooting."
          body="The stack is practical by design: networks, IoT, cloud basics, testing, documentation, security verification, and modern frontend implementation."
        />
        <div className="mt-14 grid gap-px bg-white/10 sm:grid-cols-2 lg:grid-cols-3">
          {stack.map((item, index) => {
            const Icon = item.icon

            return (
              <motion.article
                key={item.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-12%' }}
                whileHover={{ y: -5 }}
                transition={{ duration: 0.45, delay: index * 0.035, ease: 'easeOut' }}
                className="group min-h-56 bg-[#10110f] p-6"
              >
                <div className="mb-10 flex items-start justify-between">
                  <Icon className="text-copper" size={24} />
                  <span className="text-[0.68rem] font-semibold text-dim">0{index + 1}</span>
                </div>
                <h3 className="text-2xl font-semibold text-paper">{item.title}</h3>
                <p className="mt-4 text-sm leading-7 text-muted">{item.detail}</p>
                <span className="mt-8 block h-px w-12 origin-left scale-x-50 bg-copper/70 transition group-hover:scale-x-100" />
              </motion.article>
            )
          })}
        </div>
      </div>
    </section>
  )
}
