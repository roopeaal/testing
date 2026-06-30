import { Reveal } from './Reveal'

type SectionHeaderProps = {
  kicker: string
  title: string
  body?: string
}

export function SectionHeader({ kicker, title, body }: SectionHeaderProps) {
  return (
    <Reveal className="max-w-4xl">
      <p className="mb-4 text-xs font-semibold uppercase tracking-[0.32em] text-copper">
        {kicker}
      </p>
      <h2 className="text-balance text-4xl font-semibold leading-[0.98] tracking-normal text-paper sm:text-6xl">
        {title}
      </h2>
      {body ? <p className="mt-6 max-w-2xl text-base leading-8 text-muted">{body}</p> : null}
    </Reveal>
  )
}
