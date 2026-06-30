import {
  Braces,
  Cloud,
  FileCheck2,
  Globe2,
  Network,
  RadioTower,
  ShieldCheck,
  Terminal,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

export type Project = {
  title: string
  label: string
  status: string
  description: string
  note: string
  stack: string[]
}

export type Skill = {
  title: string
  detail: string
  icon: LucideIcon
}

export const navigation = ['About', 'Stack', 'Lab', 'Systems', 'Projects', 'Skills', 'Contact']

export const profileStats = [
  ['Metropolia UAS', 'ICT engineering'],
  ['Focus', 'Smart IoT Systems'],
  ['Direction', 'IoT and Networks'],
  ['Mode', 'Practical builder'],
]

export const projects: Project[] = [
  {
    title: 'Security Verification Live USB',
    label: 'Security prototype',
    status: 'Prototype',
    description:
      'Ubuntu Live USB concept for checking a device against a known baseline with a small Python interface and a local validation flow.',
    note: 'Built around repeatable checks, clear limits, and documentation instead of broad security claims.',
    stack: ['Python', 'Ubuntu Live USB', 'Baseline checks', 'Documentation'],
  },
  {
    title: 'GeoHunt',
    label: 'Map game concept',
    status: 'In progress',
    description:
      'Browser game concept where the player reads map clues, narrows down a location, and gets feedback through a simple challenge loop.',
    note: 'Useful for practicing interface state, map interaction, scoring rules, and iteration from playtesting.',
    stack: ['React', 'Maps', 'Game logic', 'UX iteration'],
  },
  {
    title: 'Portfolio Interface',
    label: 'Frontend build',
    status: 'Current build',
    description:
      'This React and TypeScript portfolio, built as a custom technical interface with restrained motion, responsive sections, and an integrated 3D network object.',
    note: 'The goal is to present current direction honestly while keeping the implementation clean and maintainable.',
    stack: ['React', 'TypeScript', 'Vite', 'Motion', 'Three.js'],
  },
  {
    title: 'Airport Guessing Game',
    label: 'Full-stack exercise',
    status: 'Student project',
    description:
      'Python, Flask, and MySQL airport guessing game with distance hints, score tracking, and a simple gameplay loop for learning backend fundamentals.',
    note: 'A practical exercise in routing, database queries, server-rendered views, and basic game feedback.',
    stack: ['Python', 'Flask', 'MySQL', 'Scoring'],
  },
]

export const stack: Skill[] = [
  {
    title: 'Networks',
    detail: 'Routing basics, connectivity checks, troubleshooting, and understanding how services actually reach each other.',
    icon: Network,
  },
  {
    title: 'IoT Systems',
    detail: 'Smart device concepts, sensor-to-service flows, edge constraints, and practical validation.',
    icon: RadioTower,
  },
  {
    title: 'Cloud',
    detail: 'Hosted services, deployment fundamentals, environment configuration, and infrastructure-minded development.',
    icon: Cloud,
  },
  {
    title: 'Cybersecurity',
    detail: 'Security verification basics, baseline comparison, careful setup notes, and cautious threat thinking.',
    icon: ShieldCheck,
  },
  {
    title: 'Modern Web',
    detail: 'React, TypeScript, Vite, responsive UI, component structure, and readable implementation patterns.',
    icon: Braces,
  },
  {
    title: 'Testing',
    detail: 'Manual verification, bug isolation, edge-case thinking, and clear reports that make issues reproducible.',
    icon: FileCheck2,
  },
]

export const experience = [
  {
    title: 'ICT Engineering Student',
    period: 'Metropolia University of Applied Sciences',
    detail:
      'Studying ICT engineering with focus on Smart IoT Systems, IoT, and Networks while building practical software and technical projects.',
  },
  {
    title: 'Developer and Tester Mindset',
    period: 'Current direction',
    detail:
      'Improving through web development, software testing, cybersecurity exercises, cloud fundamentals, and hands-on troubleshooting.',
  },
  {
    title: 'Technical Documentation',
    period: 'Working habit',
    detail:
      'Prioritising clear setup notes, validation steps, constraints, and reproducible explanations over vague project descriptions.',
  },
]

export const strengths = [
  { title: 'Problem solving', icon: Terminal },
  { title: 'Networks and IoT', icon: Network },
  { title: 'Web development', icon: Globe2 },
  { title: 'Testing and validation', icon: FileCheck2 },
]
