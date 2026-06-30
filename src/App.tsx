import { Contact } from './sections/Contact'
import { Hero } from './sections/Hero'
import { Lab } from './sections/Lab'
import { Profile } from './sections/Profile'
import { Projects } from './sections/Projects'
import { Skills } from './sections/Skills'
import { Systems } from './sections/Systems'
import { TechStack } from './sections/TechStack'
import { useLenis } from './hooks/useLenis'
import { useScrollTimelines } from './hooks/useScrollTimelines'

function App() {
  useLenis()
  const mainRef = useScrollTimelines()

  return (
    <main ref={mainRef} className="min-h-screen overflow-hidden bg-ink text-paper">
      <Hero />
      <Profile />
      <TechStack />
      <Lab />
      <Systems />
      <Projects />
      <Skills />
      <Contact />
    </main>
  )
}

export default App
