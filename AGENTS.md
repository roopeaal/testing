# Project Rules

## Stack
- React + TypeScript + Vite is the application stack.
- Tailwind CSS is configured through `@tailwindcss/vite`; do not add a parallel PostCSS setup unless Vite integration is removed.
- Use `motion` for normal UI animation.
- Use GSAP only for advanced scroll or timeline animation.
- Use Lenis for smooth scrolling and clean it up on unmount.
- Use React Three Fiber and Drei for the integrated 3D section.
- Use `lucide-react` for icons.
- Use `clsx` and `tailwind-merge` through the shared `cn()` utility when class merging is needed.
- Do not add Spline until a separate Spline-specific task asks for it.

## Structure
- Keep reusable UI in `src/components`.
- Keep page sections in `src/sections`.
- Keep hooks in `src/hooks`.
- Keep reusable data in `src/data`.
- Keep utilities in `src/lib`.
- Avoid unused starter assets, dead CSS, and isolated demo pages.

## Design
- Build for Roope Aaltonen: Finnish ICT engineering student at Metropolia UAS focused on Smart IoT Systems, IoT, and Networks.
- Keep the tone credible: do not invent fake companies, client work, or senior-level achievements.
- Design should feel premium, dark, technical, and custom.
- Avoid generic AI gradients, random glassmorphism, purple/blue SaaS styling, lorem ipsum, clutter, and excessive animation.
- Use strong typography, controlled color, clean spacing, subtle depth, and purposeful motion.
- Respect `prefers-reduced-motion` where reasonable.
- Keep desktop, tablet, and mobile layouts polished.

## Validation
- Run `npm run build` after implementation.
- Run `npm run lint` when available and fix reasonable issues.
- Do not finish with TypeScript, import, Vite, or build errors.
