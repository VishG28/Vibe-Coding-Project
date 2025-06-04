# Skimp Maps

Skimp Maps is a simple web app to crowdsource reports of Chipotle restaurants that skimp on portions. The site consists of three pages:

1. **Landing page** (`index.html`) – Explains what the project is and links to the map and submission form.
2. **Map page** (`map.html`) – Displays a map with known Chipotle locations from `chipotle_locations.json`.
3. **Add page** (`add.html`) – Lets users search for a Chipotle by ZIP code and submit their own report.
   The search tries to fetch live store data from the OpenStreetMap Overpass API
   and falls back to the bundled `chipotle_locations.json` if that request
   fails.

To view the site locally just open `index.html` in a modern browser.

## Deploying with GitHub Pages

1. Commit the site files to a repository on GitHub.
2. In the repository settings, enable GitHub Pages and choose the `main` branch as the source.
3. After a few minutes your site will be available at `https://<username>.github.io/<repo>/`.

