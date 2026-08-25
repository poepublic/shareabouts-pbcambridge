# PB Cambridge Annual Rollout Runbook

This runbook documents the annual process for configuring, provisioning, deploying, and verifying a new cycle of the Participatory Budgeting (PB) instance for Cambridge, MA.

> **Tip**: You can track this rollout interactively by opening a new GitHub issue using the [Annual PB Rollout Issue Template](.github/ISSUE_TEMPLATE/annual_pb_rollout.md) on GitHub (**Issues &rarr; New Issue &rarr; Annual PB Rollout Checklist**).

---

## Rollout Overview

```
  1. FLAVOR & CODE PREPARATION
     ├─ Copy & adapt flavor: src/flavors/cambridgefyXX/
     ├─ Update config.yml, templates, categories & translations
     └─ Update Dockerfile build arg (ARG SHAREABOUTS_FLAVOR=cambridgefyXX)
               │
               ▼
  2. API & DATASET SETUP (shareaboutsapi.poepublic.com)
     ├─ Create new dataset mimicking previous year's dataset config
     ├─ Generate API Key & copy Dataset Root URL
     └─ Update .env.gcp-stg and .env.gcp-prod
               │
               ▼
  3. STAGING DEPLOYMENT & REVIEW
     ├─ Push to staging branch & deploy to Cloud Run
     ├─ Execute staging verification checklist
     └─ City review & stakeholder sign-off
               │
               ▼
  4. PRODUCTION LAUNCH
     ├─ Merge to prod branch & update Cloud Run production service
     └─ Live smoke test & analytics verification
               │
               ▼
  5. CYCLE CLOSURE & DATA EXPORT
     ├─ Submission window close
     └─ Export ideas CSV for City staff
```

---

## Step-by-Step Checklist

### 0. Tracking Setup
- [ ] Open a tracking issue on GitHub using the **Annual PB Rollout Checklist** template.
- [ ] Record target cycle metadata:
  - **Fiscal Year**: `FY20__` (e.g., `FY28`)
  - **Flavor Name**: `cambridgefy__` (e.g., `cambridgefy28`)
  - **Submission Window**: `YYYY-MM-DD` to `YYYY-MM-DD`

---

### 1. Flavor & Code Preparation

1. **Create Flavor Directory**
   - Copy the previous cycle's flavor directory:
     ```bash
     cp -r src/flavors/cambridgefy<PREV> src/flavors/cambridgefy<NEW>
     ```
2. **Update Flavor Configuration**
   - In `src/flavors/cambridgefy<NEW>/config.yml`:
     - Update `app.tagline`, `app.meta_description`, and timeline dates.
     - Verify `place_types` categories, colors, and marker icon definitions.
     - Review submission form fields in `place.items` and post-submission surveys.
   - Recompile gettext translation catalogs:
     ```bash
     python src/manage.py flavormessages
     ```
   - Update UI assets (logos, seals, boundaries) in `src/flavors/cambridgefy<NEW>/static/` if updated by the City.

3. **Update Dockerfile Build Flavor**
   - In `Dockerfile`, update the build argument to target the new flavor:
     ```dockerfile
     ARG SHAREABOUTS_FLAVOR=cambridgefy<NEW>
     ```

4. **Verify Local Build**
   - Start the local dev server or build the container to ensure static assets and translations compile cleanly.

---

### 2. API & Dataset Setup (`shareaboutsapi.poepublic.com`)

1. **Provision New Dataset**
   - Log into the Shareabouts API admin at `https://shareaboutsapi.poepublic.com/admin`.
   - Create a new dataset that **mimics the settings and schema of the previous year's dataset**:
     - **Owner**: `cambridge`
     - **Slug / Name**: `pb-fy20XX` (e.g., `pb-fy2028`)
     - **Submission Sets**: Enable `places`, `comments`, `support`, and `surveys`.
     - **Moderators & Permissions**: Set moderator group to `cambridge-staff`.
     - **CORS / Allowed Origins**: Add staging and production origins (e.g., `pb.cambridgema.gov`, `shareabouts-pbcambridge-stg.a.run.app`, `shareabouts-pbcambridge-prod.a.run.app`, `localhost:8000`).
2. **Generate API Key & Record Dataset URL**
   - Generate a new API Key for the dataset.
   - Note the dataset root URL: `https://shareaboutsapi.poepublic.com/api/v2/cambridge/datasets/pb-fy20XX`

3. **Update Environment Files**
   - In `.env.gcp-stg`:
     - Set `SHAREABOUTS_FLAVOR=cambridgefy<NEW>`
     - Set `SHAREABOUTS_DATASET_ROOT` and `SHAREABOUTS_DATASET_KEY` (use dev/staging dataset for testing).
   - In `.env.gcp-prod`:
     - Set `SHAREABOUTS_FLAVOR=cambridgefy<NEW>`
     - Set `SHAREABOUTS_DATASET_ROOT=https://shareaboutsapi.poepublic.com/api/v2/cambridge/datasets/pb-fy20XX`
     - Set `SHAREABOUTS_DATASET_KEY=<new_prod_api_key>`
     - Set `SHAREABOUTS__PLACE__ADDING_SUPPORTED__FROM="YYYY-MM-DD HH:MM -0400"`
     - Set `SHAREABOUTS__PLACE__ADDING_SUPPORTED__UNTIL="YYYY-MM-DD HH:MM -0400"`
     - Set `SHAREABOUTS__SURVEY__ADDING_SUPPORTED__FROM="YYYY-MM-DD HH:MM -0400"`
     - Set `SHAREABOUTS__SURVEY__ADDING_SUPPORTED__UNTIL="YYYY-MM-DD HH:MM -0400"`

---

### 3. Staging Deployment & Verification

1. **Deploy to Staging**
   - Push code to the `staging` branch to trigger the Cloud Build pipeline:
     ```bash
     git checkout -B staging
     git merge main
     git push origin staging
     ```
   - Update Cloud Run staging environment variables:
     ```bash
     gcloud run services update shareabouts-pbcambridge-stg \
       --env-vars-file=<(cat .env.gcp-stg | python3 env2yml.py) \
       --region=us-central1
     ```

2. **Pre-Launch Verification Checklist (Staging)**
   - [ ] **Map & Geocoding**: Cambridge boundary renders; Mapbox address search autocompletes properly.
   - [ ] **Marker Icons**: Category markers display correctly at low, medium, and high zoom levels.
   - [ ] **Location vs City-Wide**: Test submitting a point idea on the map; test submitting a city-wide idea.
   - [ ] **Submission Validation**: Required fields (title, description, impact, category) validate properly.
   - [ ] **Post-Submission Survey**: Survey prompts display and store answers correctly.
   - [ ] **Multilingual Support**: Switch between English, Spanish, Portuguese, Haitian Creole, Amharic, Arabic, and Chinese to verify translations.
   - [ ] **Email Notifications**: Ensure confirmation emails trigger via Postmark (if enabled).
   - [ ] **Admin & Moderation**: Log in as `cambridge-staff` to verify moderation dashboard and hidden/private views.

3. **City Review**
   - Share staging URL with City of Cambridge PB coordinators for final review and sign-off.

---

### 4. Production Launch

1. **Deploy to Production**
   - Merge `main` into `prod` and push:
     ```bash
     git checkout prod
     git merge main
     git push origin prod
     ```
   - Update Cloud Run production environment variables:
     ```bash
     gcloud run services update shareabouts-pbcambridge-prod \
       --env-vars-file=<(cat .env.gcp-prod | python3 env2yml.py) \
       --region=us-central1
     ```

2. **Production Smoke Test**
   - [ ] Confirm custom domain (`pb.cambridgema.gov`) serves the new flavor.
   - [ ] Confirm submission form is open and accepting submissions.
   - [ ] Submit one live test idea, verify it appears in the API dataset, then delete or mark hidden.
   - [ ] Check Sentry error dashboard for any uncaught exceptions.
   - [ ] Verify Google Analytics real-time tracking is receiving page views.

---

### 5. Post-Launch Operations & Data Export

1. **Submission Window Closure**
   - The submission window will close automatically based on `SHAREABOUTS__PLACE__ADDING_SUPPORTED__UNTIL`.
   - To manually close submissions if needed:
     ```bash
     # In .env.gcp-prod set SHAREABOUTS__PLACE__ADDING_SUPPORTED="False"
     gcloud run services update shareabouts-pbcambridge-prod \
       --env-vars-file=<(cat .env.gcp-prod | python3 env2yml.py) \
       --region=us-central1
     ```

2. **Export Ideas Data for City Staff**
   - Run the CSV export script from `scripts/data/`:
     ```bash
     python scripts/data/writeplacescsv.py \
       --earliest "YYYY-MM-DD" \
       --latest "YYYY-MM-DD" \
       --outfile pb_cambridge_fy20XX_ideas.csv
     ```
   - Provide the exported CSV to the Cambridge PB committee.
