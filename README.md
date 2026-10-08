# Wade Compliance Solutions — website

Marketing site for [wadecompliance.com](https://wadecompliance.com/). Plain HTML, CSS and JavaScript — no build step.

| File | Purpose |
| --- | --- |
| `index.html` | Page content and structure |
| `styles.css` | Design tokens (colors, type), layout, 3D effects, animations |
| `main.js` | Path chooser, SOC 2 self-check, service tabs, 3-step demo booking, scroll progress, 3D pointer effects |
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
- **Demo booking:** the 3-step form opens the visitor's email app with a pre-filled request to `donta@wadecompliance.com`. To receive bookings directly, connect it to a form or scheduling service (Formspree, Cal.com, Calendly) in the submit handler in `main.js`.
- **SOC 2 self-check:** questions and result tiers live in `index.html` (`#soc2`) and `TIERS` in `main.js`. Answers stay in the visitor's browser.
- **Motion:** all animation is disabled automatically for visitors who set "reduce motion" on their device.
