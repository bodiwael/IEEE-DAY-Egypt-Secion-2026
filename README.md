# IEEE Day 2026 – v3

## Files
- `Master_Sheet.xlsx` – single source of data (attendee tabs + `Staff` tab). **Private – not in git.**
- `build.py` – turns the sheet into the app. Run after ANY change to the sheet: `pip install openpyxl cryptography` then `python3 build.py`
- `site/` – the web app. Safe to publish: attendee data inside is encrypted and the key lives only in the backend.
- `backend/Code.gs` – paste into Google Sheet > Extensions > Apps Script. **Private – holds the data key. Not in git.**
- `staff_codes.csv` – Staff ID + 6-digit code per person. Hand out individually. **Private – not in git.**
- `api_url.txt` (optional) – your Apps Script `/exec` URL; build.py bakes it into the site so phones need no link.

Every build creates a new data key, so **always deploy `site/` and `Code.gs` from the same build**. The app shows a red warning if they don't match.

## Event flow (stations)
| Station | Who scans |
|---|---|
| 🚌 Morning Bus | Bus lead – each scan **auto-emails** the attendee (bus, National ID, T-shirt, lead phone, stay-on-your-bus notice) 1 min later. Undo within that minute cancels the email. |
| 🚪 Arrival · no bus | Registration – people who come by themselves |
| 🎒 Kit, 🍽️ Lunch | Registration / Packages / Bus leads |
| ⛰️ Mountain, 🏜️ Sandboard, 💦 Falls, 🏁 Return | Bus lead – only their own passengers. Another bus's passenger → red **WRONG BUS** (override is logged on the dashboard). Someone not on any bus → "Add to Bus X" (assigns them + emails them). |

Roles (Staff tab): `admin` = Lead (dashboard + everything), `joker` = same as admin, `reg` = Arrival/Kit/Lunch, `kit` = Kit/Lunch, `bus` = bus lead (Bus = number, Point = Ramsis/October).

## Setup
1. Google Sheet > Extensions > Apps Script: replace ALL code with `backend/Code.gs`. Delete old `Events` and `Mail` tabs (test data).
2. Put your email in `TEST_TO` while testing. Run `setup` once (check the log: mail quota – a normal Gmail account sends only ~100/day; use a Google Workspace account for 400+).
3. Deploy > New deployment > Web app > Execute as **Me** > Access **Anyone**. Copy the `/exec` URL into `api_url.txt` and run `python3 build.py` again, then paste the NEW `Code.gs` and Deploy > Manage deployments > ✏️ > **New version** (the URL stays the same).
4. Host `site/` (below). Sign in with a Staff ID (e.g. `B1`) + 6-digit code. Sign-in needs internet once; after that the phone works offline.
5. Before the event: `TEST_TO=''`, Manage deployments > New version. Clear test rows in `Events` and `Mail`.

## Hosting `site/`
- **Netlify Drop (fastest):** app.netlify.com/drop → drag the `site` folder → you get `https://xxx.netlify.app`. To update: Site > Deploys > drag the folder again (same URL).
- **Cloudflare Pages / Vercel:** connect this repo, build command none, output directory `site`.
- Staff open the URL on their phone → Share/menu → **Add to Home Screen**.

## Changing staff / bus assignments
Edit the `Staff` tab, `python3 build.py`, re-upload `site/`, paste the new `Code.gs`, deploy a new version. Existing staff keep their codes (from `staff_codes.csv`).
