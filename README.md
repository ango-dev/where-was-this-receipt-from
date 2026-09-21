# Where was this receipt from?

An educational tool that shows how much a sales tax line gives away about where a purchase happened.

US sales tax is stacked from state, county, city and district rates, so the combined rate on a receipt works like a rough fingerprint. Enter a subtotal and the tax charged, and the page works out which rates could have produced that tax, lists every place that charges one of them, and crosses off the states that can't match.

It is a single static page. There is no server, no tracking, and nothing you type leaves your browser.

## What it shows

- **Rounding matters.** Tax is rounded to the cent, so a $3.50 coffee fits a band of rates about 0.29 points wide and matches over a thousand places. A $184 shop narrows the band to a single rate.
- **Several receipts narrow it further.** Receipts from the same place are intersected; only rates that fit all of them survive.
- **Fee lines beat tax rates.** A named fee such as California's CRV or a Colorado retail delivery fee identifies the state outright. Tick the ones printed on the receipt.
- **It rarely pinpoints.** Hundreds of towns share common rates, exempt items distort the math, and online orders are taxed at the delivery address. The page explains each limit.

The privacy lesson: a receipt photo with the store name cropped out can still say roughly where someone shops. Crop the totals too.

## Run it

Open `docs/index.html` in a browser. That's all.

To serve it locally with Docker:

```
docker compose up -d
```

Then open http://localhost:8080.

## Host it on GitHub Pages

1. Create an empty public repository on GitHub (no README, no license).
2. Push this repository to it:

   ```
   git remote add origin https://github.com/ango-dev/where-was-this-receipt-from.git
   git push -u origin main
   ```

3. In the repository, open Settings, then Pages. Set the source to "Deploy from a branch", choose `main` and `/docs`, and save.
4. After a minute the site is live at `https://ango-dev.github.io/where-was-this-receipt-from/`.

Any static host works the same way: publish the contents of `docs/`.

## The rate table

The built-in table holds 14,037 tax regions across all 50 states, DC and Puerto Rico. It was built from Avalara's free ZIP-level rate tables for September 2026 by merging ZIP codes that share a region name and rate.

The table lives in two places: embedded in `docs/index.html`, so the page works when opened as a file, and as `docs/rates.csv`, which the page loads at startup when it is served over HTTP. **The CSV wins when both are present**, so updating the CSV is enough for a hosted copy.

Rates change every quarter. To refresh:

1. Download new tables (Avalara's free per-state CSVs, or a state revenue department's list) into `downloads/`.
2. Run `python3 build_rates.py downloads/`. Add `--state CA` for a file that has no state column.
3. Commit the new `docs/rates.csv` and push.

You can also import CSV files straight in the browser from the "Rates table" section at the bottom of the page. That changes only your current session.

### Known quirks in the data

- **Entries are tax regions, not strictly cities.** Most are cities; some are counties or special districts.
- **Rates above about 12% are mostly artifacts.** For tribal lands and some special districts, the source tables add a replacement tax on top of the regular one, so a Las Vegas tourism district shows 16.75% where a receipt would show 8.375%. The data is left as published, and the page shows a caution for rates that high.
- **Check the source's terms before republishing.** The rate tables come from Avalara. If their terms don't allow redistribution, replace the embedded table and `docs/rates.csv` with your own data before making the repository public.

## Fee lines

The fee list is the `FEES` array near the top of the script in `docs/index.html`. Each entry has a label, a short detail, and the states that charge it. Only the two California electronics fees were verified against current sources when this was written; treat the rest as a starting point and correct them as needed.

## Files

| Path | Purpose |
| --- | --- |
| `docs/index.html` | The whole site: markup, styles, script and the embedded rate table |
| `docs/rates.csv` | The rate table as CSV: state, county, place, combined rate (%) |
| `build_rates.py` | Merges downloaded rate CSVs into `docs/rates.csv` |
| `Dockerfile`, `docker-compose.yml` | Serve `docs/` with nginx |
| `downloads/` | Drop raw rate files here; ignored by git |
| `LICENSE` | GNU AGPL v3: free to use, changes must stay open |

## License

Copyright (C) 2026 where-was-this-receipt-from contributors

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License, version 3, as published by the Free Software Foundation. It is distributed without any warranty. See `LICENSE` for the full text.

In practice: anyone may use, copy, change and host it, for any purpose. Anyone who distributes it or runs a modified copy as a website must make their source available under this same license, so every version stays open.

The license does not cover the rate data, which comes from Avalara's published tables and stays subject to their terms.

## Disclaimer

This is an educational demonstration, not tax software. Don't use it to calculate, collect or file tax, and don't treat its matches as proof of where anyone was.
