# tscircuit organizers

Printable workshop organizers, with downloadable models and an interactive viewer. The Docusaurus site is hosted at [organizers.tscircuit.com](https://organizers.tscircuit.com).

Run `npm ci` and `npm start` for local development. Run `npm run deploy` with Wrangler authenticated to the tscircuit Cloudflare account to build and publish the static site.

To regenerate the metric bolt tray, install `models/requirements.txt` into a Python virtual environment and run `python models/metric_bolt_tray.py`. The script writes the 3MF, STL and viewer geometry into `static/models/metric-bolt-tray/`.
