# Profile assets

- `workshop-*.svg` and `workshop-*.gif`: isometric workshop illustration created for this profile using the Anatomy kit. Kit license: [MIT](licenses/anatomy-MIT.txt).
- `badges/`: locally stored technology badges from Shields.io. Product names and logos identify their respective owners.
- `visuals/`: domain symbols, contact links and personal-interest gauges created for this profile. The gauges express interests, not proficiency scores.
- `psd-i.png`: Scrum.org Professional Scrum Developer I credential badge supplied by Samuel Aulotte; [verification](https://www.credly.com/badges/484a67ca-3bf4-4104-98ee-7201c8e2186c/linked_in_profile).
- `project-images/`: captures from Samuel’s project work. Warevia and HumaPace use lab/synthetic data; Resilient UAS Lab shows a mock simulation; Conductor shows the pedagogical portfolio demonstration.

The Conductor portfolio capture contains an adapted rendering of [MacBook Pro M3 16 inch 2024](https://sketchfab.com/3d-models/macbook-pro-m3-16-inch-2024-8e34fc2b303144f78490007d91ff57c4) by **jackbaeten**, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The model is articulated and used as the portfolio display.

- `contributions/`: calendar generated from [Samuel’s public GitHub contribution calendar](https://github.com/users/samaulotte/contributions), with the title “We add value, every day”. Dates, counts and levels come from that unauthenticated public endpoint; no private repository data is accessed. The SVG shows the snapshot’s final date, and `data.json` records the source and daily values.
- Visual inspiration: [Avi Vashishta’s “Every day, in blue” card](https://github.com/AVIVASHISHTA29/AVIVASHISHTA29). This renderer is written for Samuel; the other profile’s data and artwork are not copied. The existing README content and assets remain intact.
- `fonts/`: unmodified Instrument Serif regular and italic from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/instrumentserif), under [SIL OFL 1.1](fonts/OFL.txt). These fonts are embedded in the generated SVGs, with no external font request.

## Updating the contribution card

Run `python3 scripts/update_contributions.py` to fetch the public calendar and regenerate all four variants, or pass `--html path/to/saved-response.html` for an offline check. Run `python3 -m unittest discover -s tests` to validate parsing and date preservation. No dependencies or personal token are required.

The GitHub Actions workflow runs daily at 06:23 UTC once merged into the default branch, and can also be triggered manually. Scheduled runs may be delayed or disabled by GitHub after prolonged repository inactivity. An invalid or incomplete response fails the job and leaves the last committed calendar intact. The image’s update date makes an old snapshot visible. Desktop shows the complete calendar on one grid; narrow screens split the same weeks across two grids, without dropping dates.

- `certifications/`: CertiProf Lead Auditor and Lead Implementer badge images supplied by Samuel, copied without modification. Names, issue/expiry dates and verification links match the certifications already documented in his portfolio. The original PSD I credential remains present.
