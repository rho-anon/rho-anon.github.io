# Anonymous project page

Live at <https://rho-anon.github.io>, linked from the ICRA submission abstract.

**This page must stay anonymous until review completes.** RAS rules state:
"There should be no links to external websites that reveal identity
(e.g., YouTube, GitHub, or authors' institute pages)." Author names,
affiliations and the citation block go in only after acceptance.

## Editing

Content lives in one file:

    source/app/src/content/article.mdx

Sections present but empty: Abstract, Method, Results, Demos, Hardware.
The BibTeX section and the footer citation block are commented out
(`source/app/src/components/Footer.astro`) and can be restored later.

Live preview while writing:

    cd source/app && npm run dev        # http://localhost:4321

## Publishing

    ./publish.sh "optional commit message"

Builds, copies the static site to the repo root, refuses to publish if any
identity string appears, commits as `RHO Authors <anonymous@users.noreply.github.com>`,
and pushes. GitHub Pages serves the repo root; it takes about a minute.

## Template

[Research Article Template](https://huggingface.co/spaces/tfrere/research-article-template)
by Thibaud Frere, CC-BY 4.0. Uses the `article` variant, which provides the
sticky sidebar table of contents. The `paper` variant has no sidebar.

## Animated splash

The hero uses `source/app/src/components/RhoWalkthrough.astro`. Its figure is
`source/app/public/rho-figure.webp`. Six steps animate repository sampling, harness
edits, benchmark trials, feedback, retention, and deployment. The final step opens
a self-contained Viser recording of Franka and Kinova Gen3. Motion is illustrative;
replace with measured trajectories before describing it as experimental evidence.
Playback controls, keyboard step selection, reduced motion, and a static fallback
are included. Robot model licenses accompany the viewer.

No publishing or Git-history changes are needed to preview: build the app and serve
`source/app/dist`, or use the development command above.
