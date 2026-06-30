import { motion, useScroll, useTransform } from 'motion/react'
import { ArrowDownRight, MapPin, Network, RadioTower } from 'lucide-react'
import { navigation, profileStats } from '../data/portfolio'

export function Hero() {
  const { scrollYProgress } = useScroll()
  const y = useTransform(scrollYProgress, [0, 0.25], [0, -120])

  return (
    <section id="top" className="relative isolate min-h-screen overflow-hidden px-5 sm:px-8 lg:px-10">
      <div className="absolute inset-0 -z-20 bg-[linear-gradient(180deg,#090a09_0%,#11130f_54%,#090a09_100%)]" />
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(90deg,rgba(242,238,231,0.055)_1px,transparent_1px),linear-gradient(180deg,rgba(242,238,231,0.04)_1px,transparent_1px)] bg-[size:72px_72px] opacity-60" />
      <div className="absolute left-0 top-20 -z-10 h-px w-full bg-white/10" />
      <div className="absolute bottom-10 left-5 -z-10 hidden h-44 w-px bg-copper/40 lg:block" />

      <header className="mx-auto flex h-20 max-w-7xl items-center justify-between">
        <a href="#top" className="text-sm font-semibold uppercase tracking-[0.24em] text-paper">
          Roope Aaltonen
        </a>
        <nav className="hidden items-center gap-7 text-sm text-muted md:flex">
          {navigation.map((item) => (
            <a key={item} href={`#${item.toLowerCase()}`} className="transition hover:text-paper">
              {item}
            </a>
          ))}
        </nav>
        <a
          href="#contact"
          className="inline-flex h-10 items-center justify-center border border-white/12 px-4 text-xs font-semibold uppercase tracking-[0.18em] text-paper transition hover:border-copper hover:text-copper"
        >
          Contact
        </a>
      </header>

      <motion.div
        style={{ y }}
        className="mx-auto grid max-w-7xl gap-12 pb-20 pt-14 lg:min-h-[calc(100vh-5rem)] lg:grid-cols-[1.08fr_0.92fr] lg:items-end lg:pt-24"
      >
        <motion.div
          initial="hidden"
          animate="visible"
          transition={{ staggerChildren: 0.08 }}
          className="max-w-6xl"
        >
          <motion.div
            variants={{ hidden: { opacity: 0, y: 18 }, visible: { opacity: 1, y: 0 } }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="mb-8 inline-flex items-center gap-3 border border-white/10 bg-white/[0.025] px-4 py-2 text-xs font-medium uppercase tracking-[0.2em] text-soft"
          >
            <RadioTower size={15} className="text-copper" />
            Metropolia ICT engineering / Smart IoT Systems
          </motion.div>
          <motion.h1
            variants={{ hidden: { opacity: 0, y: 28 }, visible: { opacity: 1, y: 0 } }}
            transition={{ duration: 0.82, ease: [0.22, 1, 0.36, 1] }}
            className="max-w-6xl text-balance text-[clamp(3.4rem,9.4vw,9.6rem)] font-semibold leading-[0.86] tracking-normal text-paper"
          >
            Networks, IoT, testing, and practical technical problem solving.
          </motion.h1>
          <motion.div
            variants={{ hidden: { opacity: 0, y: 28 }, visible: { opacity: 1, y: 0 } }}
            transition={{ duration: 0.82, ease: [0.22, 1, 0.36, 1] }}
            className="mt-10 flex max-w-3xl flex-col gap-7 text-base leading-8 text-muted sm:flex-row sm:items-end sm:text-lg"
          >
            <p>
              I am Roope Aaltonen, a Finnish ICT engineering student at Metropolia
              University of Applied Sciences focused on Smart IoT Systems, IoT,
              networks, testing, cloud fundamentals, and cybersecurity basics.
            </p>
            <a
              href="#projects"
              className="inline-flex shrink-0 items-center gap-3 border-b border-copper pb-2 text-base font-medium text-paper"
            >
              View projects
              <ArrowDownRight size={18} />
            </a>
          </motion.div>
        </motion.div>

        <motion.aside
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.42, duration: 0.82, ease: [0.22, 1, 0.36, 1] }}
          className="relative border border-white/10 bg-graphite p-5 shadow-2xl shadow-black/40 sm:p-6"
        >
          <div className="absolute right-5 top-5 h-2 w-2 bg-copper" />
          <div className="mb-14 flex items-start justify-between gap-6">
            <Network className="mt-1 text-copper" size={26} />
            <div className="text-right text-sm leading-6 text-muted">
              <p className="inline-flex items-center justify-end gap-2 text-paper">
                <MapPin size={14} />
                Finland
              </p>
              <p>Building practical projects while developing as a developer and tester.</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-px bg-white/10">
            {profileStats.map(([label, value]) => (
              <div key={label} className="bg-graphite p-4">
                <div className="text-xs uppercase tracking-[0.18em] text-dim">{label}</div>
                <div className="mt-3 text-lg font-semibold text-paper">{value}</div>
              </div>
            ))}
          </div>
        </motion.aside>
      </motion.div>
    </section>
  )
}
