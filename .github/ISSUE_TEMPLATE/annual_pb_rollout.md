---
name: Annual PB Rollout Checklist
about: Step-by-step checklist for deploying a new PB Cambridge cycle
title: 'PB Cambridge FY20__ Rollout'
labels: ['deployment', 'annual-cycle']
---

## Cycle Information

- **Target Fiscal Year**: FY20__ (e.g., FY28)
- **Flavor Name**: `cambridgefy__` (e.g., `cambridgefy28`)
- **Submission Dates**: `YYYY-MM-DD` to `YYYY-MM-DD`
- **Dataset Slug**: `pb-fy20__` (e.g., `pb-fy2028`)

---

## 1. Flavor & Code Preparation

- [ ] **Create New Flavor Directory**
  - [ ] Copy previous cycle's flavor: `cp -r src/flavors/cambridgefy<PREV> src/flavors/cambridgefy<NEW>`
  - [ ] Update `config.yml` (dates, categories, survey questions, district bounds, text copy)
  - [ ] Compile gettext translation messages: `python src/manage.py flavormessages`
  - [ ] Update any revised static assets (logos, seals, boundaries) in `src/flavors/cambridgefy<NEW>/static/`
- [ ] **Update Dockerfile Build Flavor**
  - [ ] Update `ARG SHAREABOUTS_FLAVOR=cambridgefy<NEW>` in `Dockerfile`
- [ ] **Local Build Verification**
  - [ ] Verify static assets and translations build and render locally

---

## 2. API & Dataset Setup (`shareaboutsapi.poepublic.com`)

- [ ] **Provision Dataset**
  - [ ] Log into `https://shareaboutsapi.poepublic.com/admin`
  - [ ] Create a new dataset mimicking the previous cycle's configuration:
    - **Owner**: `cambridge`
    - **Slug**: `pb-fy20XX`
    - **Submission sets**: `places`, `comments`, `support`, `surveys`
    - **Moderator group**: `cambridge-staff`
    - **CORS origins**: Add staging and production origins
- [ ] **Configure API Key & Environment Files**
  - [ ] Generate API key for the new dataset
  - [ ] Update `.env.gcp-stg` with dev/staging dataset root and key
  - [ ] Update `.env.gcp-prod` with production dataset root, API key, and window dates (`SHAREABOUTS__PLACE__ADDING_SUPPORTED__FROM` / `...__UNTIL`)

---

## 3. Staging Deployment & Verification

- [ ] **Deploy to Staging**
  - [ ] Merge `main` into `staging` branch and push:
    ```bash
    git checkout -B staging
    git merge main
    git push origin staging
    ```
  - [ ] Apply staging env vars to Cloud Run:
    ```bash
    gcloud run services update shareabouts-pbcambridge-stg \
      --env-vars-file=<(cat .env.gcp-stg | python3 env2yml.py) \
      --region=us-central1
    ```
- [ ] **Run Staging Verification Checklist**
  - [ ] Map loads centered on Cambridge with boundary overlay
  - [ ] Address search / geocoding autocomplete functions properly
  - [ ] Category marker icons display at all zoom levels
  - [ ] Point idea submission works
  - [ ] City-wide idea submission works
  - [ ] Post-submission demographic survey records responses
  - [ ] Multilingual translations render in English, Spanish, Portuguese, Haitian Creole, Amharic, Arabic, Chinese
  - [ ] Postmark notification emails trigger
  - [ ] Staff admin login and moderation features work
- [ ] **City Review & Approval**
  - [ ] Share staging link with Cambridge PB team for final review and sign-off

---

## 4. Production Launch

- [ ] **Deploy to Production**
  - [ ] Merge `main` into `prod` branch and push:
    ```bash
    git checkout prod
    git merge main
    git push origin prod
    ```
  - [ ] Update Cloud Run production service configuration:
    ```bash
    gcloud run services update shareabouts-pbcambridge-prod \
      --env-vars-file=<(cat .env.gcp-prod | python3 env2yml.py) \
      --region=us-central1
    ```
- [ ] **Production Sanity Smoke Test**
  - [ ] Verify production domain (`pb.cambridgema.gov`) serves the new flavor
  - [ ] Confirm submission form is open and accepting submissions
  - [ ] Submit one live test idea, verify in API, and delete/hide
  - [ ] Check Sentry error logging dashboard
  - [ ] Verify Google Analytics page view tracking

---

## 5. Post-Launch Operations & Data Export

- [ ] **Submission Window Closure**
  - [ ] Verify submissions close automatically after deadline (or manually set `SHAREABOUTS__PLACE__ADDING_SUPPORTED="False"`)
- [ ] **Data Export**
  - [ ] Run CSV export script:
    ```bash
    python scripts/data/writeplacescsv.py \
      --earliest "YYYY-MM-DD" \
      --latest "YYYY-MM-DD" \
      --outfile pb_cambridge_fy20XX_ideas.csv
    ```
  - [ ] Deliver exported data to Cambridge PB team
