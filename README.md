# IEEE Day 2026 – v3

## Files
- `Master_Sheet.xlsx` – single source of data (attendee tabs + `Staff` tab). **Private – not in git.**
- `build.py` – turns the sheet into the app. Run after ANY change to the sheet: `pip install openpyxl cryptography` then `python3 build.py`
- `site/` – the web app. Safe to publish: attendee data inside is encrypted and the key lives only in the backend.
- `backend/Code.gs` – paste into Google Sheet > Extensions > Apps Script. **Private – holds the data key. Not in git.**
- `staff_codes.csv` – Staff ID + 6-digit code per person. Hand out individually. **Private – not in git.**
- `api_url.txt` (optional) – your Apps Script `/exec` URL; build.py bakes it into the site so phones need no link.

The data key is reused from the last `backend/Code.gs`, so a new site works with an older `Code.gs` and vice versa. `python3 build.py --new-key` rotates it (then redeploy both). Bus WhatsApp links live in the `WhatsApp` column of the Staff tab (or edit `WHATSAPP` directly in Apps Script).

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
- **Vercel (from GitHub):** vercel.com/new → Import this repo → Framework Preset **Other**, Root Directory **`site`**, no build command → Deploy. Every push to the production branch (`main`) redeploys. Give staff the **production** URL (`https://<project>.vercel.app`); preview URLs ask for a Vercel login.
- **Vercel (CLI, no GitHub):** `npx vercel login` once, then `npx vercel deploy site --prod`. Run the same command after every rebuild.
- **Netlify Drop / Cloudflare Pages:** drag `site` to app.netlify.com/drop, or connect the repo with output directory `site`.
- Staff open the URL on their phone → Share/menu → **Add to Home Screen**.

## Changing staff / bus assignments
Edit the `Staff` tab, `python3 build.py`, re-upload `site/`, paste the new `Code.gs`, deploy a new version. Existing staff keep their codes (from `staff_codes.csv`).
