# BT Paint & Body Work website

Website for **Bruno Tiopisto – Pintura e Bate-Chapas**, a car paint and body work shop in Portugal.

The site will be a fully responsive static website (phone, tablet and desktop) that shows the shop's services and lets customers send photos of damage to their car so the owner can give a price and book the job in.

## Planned features

- **Responsive static site**: plain HTML, CSS and a little JavaScript, no build step needed to run it.
- **Pages / sections**: home, services (paint, body repair, dent and scratch repair, bumpers, polishing), recent work gallery, about, contact and location.
- **Damage photo upload**: customers fill in a short form (name, phone, email, car make/model, description of the damage) and attach photos of the damage. The submission goes straight to the owner so they can price the repair and arrange a booking.
- **Booking requests**: customers pick a preferred date/time with the quote request; the owner confirms by phone or email.
- **Contact shortcuts**: tap-to-call, WhatsApp and map links for mobile users.
- **Portuguese first**, with English as an option.

The photo upload is the only part that needs something outside a static site, because files have to be stored and delivered to the owner. The plan is to use a hosted form service that accepts file uploads (for example Formspree, Netlify Forms or a small serverless function) so the site itself stays static and free/cheap to host.

## Project structure

```
.
├── README.md
├── index.html               # home page (Portuguese)
├── css/style.css
├── js/main.js               # mobile menu, photo previews, form submit
└── assets/
    └── logo/
        ├── logo.svg                 # main badge, transparent background (use this on the site)
        ├── logo-600.png / -1200 / -2400.png
        ├── logo-on-dark.svg         # badge on a dark background
        ├── logo-on-dark-1200.png / -2400.png
        ├── logo-icon.svg            # car mark only, square (favicon / app icon)
        ├── icon-32.png / -180.png / -512.png
        └── source/build_logo.py     # script that regenerates all logo files
```

Before going live, set the form `action` in `index.html` to a real endpoint (e.g. a Formspree form ID) so photo uploads reach the owner.

## Pending actions

- [ ] **Connect the quote form to Formspree** (or similar): create a form, then replace `YOUR_FORM_ID` in the form `action` in `index.html`. Until then the photo upload only works as a demo and nothing reaches the owner.
- [ ] Services section was removed for now; bring it back if wanted.

## Running it locally

No install is needed. Clone the repo and either open `index.html` in a browser, or serve the folder so links and uploads behave like they will online:

```bash
git clone https://github.com/RicardoIT-Web/bt-paint-body-website.git
cd bt-paint-body-website
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploying

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, Render static sites). Point the host at the repository root; there is no build command.

## Brand

| Use | Colour |
| --- | --- |
| Green (text, frame) | `#8DC63F` |
| Green gradient (car) | `#B2E05A` → `#6AAE34` |
| Light grey (rim, subtitle) | `#D9DEE2` |
| Charcoal (background) | `#232628` |

Fonts: **Orbitron** Bold for the name, **Open Sans** Bold for "Pintura e Bate-Chapas" (both free Google Fonts). In the logo files the text is already converted to outlines, so they display the same everywhere.
