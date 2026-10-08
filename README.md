# Wade Compliance Solutions — website

Marketing site for [wadecompliance.com](https://wadecompliance.com/). Plain HTML, CSS and JavaScript — no build step.

| File | Purpose |
| --- | --- |
| `index.html` | Page content and structure |
| `styles.css` | Design tokens (colors, type), layout, 3D effects, animations |
| `main.js` | Scroll reveals, pointer-driven 3D tilt, sticky header state, contact form |
| `favicon.svg` | Browser tab icon |

## Run locally

```sh
python3 -m http.server 8080
# open http://localhost:8080
```

## Deploy

Upload the four files above to any static host (Netlify, Vercel, GitHub Pages, Cloudflare Pages, or your current web host) and point `wadecompliance.com` at it.

## Editing

- **Accent color:** change `--accent` at the top of `styles.css`.
- **Contact form:** currently opens the visitor's email app addressed to `donta@wadecompliance.com`. To receive submissions directly, point the form at a form service (Formspree, Netlify Forms, etc.) and remove the `mailto` handler in `main.js`.
- **Motion:** all animation is disabled automatically for visitors who set "reduce motion" on their device.
