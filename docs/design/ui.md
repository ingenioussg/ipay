# iPay UI design system

Source of truth: `static/css/design-system/variables.css` (tokens and components) and `static/javascript/design-system/app.js` (behaviour).

## Principles (from research, 2026-10-21)

- **Neutrals carry the UI.** Minimalist SaaS products are 80-90% neutral surfaces, with one accent colour used sparingly. A cool slate base reads as "product" rather than marketing. Status colours (success, warning, danger, info) mark state only, never decoration. ([SaaS frontend design guide](https://mcpservers.org/de/agent-skills/cloudflare/frontend-design-saas))
- **One accent, as a ramp.** Indigo, with hover, pressed, soft-fill and text shades all taken from the same hue (Linear uses a similar indigo).
- **Perceptual colour space.** Linear generates its light and dark themes from one generator in LCH, using surface lightness for elevation ([How we redesigned the Linear UI](https://linear.app/blog/how-we-redesigned-the-linear-ui)). Tailwind v4 moved its palette to OKLCH ([OKLCH explained for designers](https://uxdesign.cc/oklch-explained-for-designers-dc6af4433611)). iPay defines every colour in OKLCH: light and dark use the same hues (`--hue: 265`, accent 275) at matched perceived lightness.

## Tokens

| Group | Tokens |
| --- | --- |
| Surfaces | `--bg`, `--surface`, `--surface-2`, `--surface-3`, `--border`, `--border-strong` |
| Text | `--text`, `--text-2` (secondary), `--text-3` (muted) |
| Accent | `--accent`, `-hover`, `-press`, `-soft`, `-text`, `--on-accent`, `--ring` |
| Status | `--success`, `--warning`, `--danger`, `--info`, each with `-soft` |
| Country | `--sg` (red), `--my` (blue) |
| Shape | radius 8 / 12 / 16 / 22 px; spacing on a 4 px grid; three shadow levels |
| Type | Inter; 12-34 px scale; `.num` gives tabular figures for money |
| Motion | `--ease-out` (expo), `--ease-spring` (slight overshoot); 120 / 220 / 380 ms |

## Behaviour

- **Every error opens an animated modal.** Server errors reply `4xx/5xx` with JSON `{title, message, errors}`. The modal lists the problems, and the matching fields get a red ring, a shake and inline text. Network failures and expired sessions get their own modals.
- **Successes show toasts**, sent by `HX-Trigger: {"toast": ...}` or by `flash()` before a navigation. They slide in, show a progress bar, and pause on hover.
- **Smooth navigation.** htmx boosts links and forms; View Transitions fade between pages; a top progress bar runs during requests; buttons show a spinner while they submit.
- **Responsive.** Below 1024 px the sidebar becomes a drawer with a scrim; below 640 px modals become bottom sheets and toasts centre.
- **Dark mode.** Cycles system, light, dark; stored per browser and applied before first paint, so there is no flash.
- **Reduced motion.** `prefers-reduced-motion` turns animation off.
