# Running Career Orchestrator on SAP BTP (branch `sap-btp`)

Nothing in this guide has been run against a real SAP system by the assistant that wrote it. A step counts as "tested" only after you have run it and seen it work.
Keep your demo on the local run. Treat this as a bonus and as a fallback URL.

## Part A. Deploy the app to Cloud Foundry (Slice 1)

1. Sign in to your SAP BTP **trial** cockpit. Open your trial subaccount. In **Overview**, note the **Cloud Foundry Environment** section: API Endpoint, Org Name, and Space (usually `dev`).
2. Install the Cloud Foundry command line tool (version 8): `brew install cloudfoundry/tap/cf-cli@8`. Check with `cf version`.
3. Log in: `cf login -a <API Endpoint from step 1> --sso`. Open the link it prints, copy the one-time passcode, paste it back. Pick your org and space.
4. In the project folder: `git switch sap-btp`. Make sure there is no `.env` in the folder you push from, or keep the `.cfignore` that is already there (it blocks `.env`).
5. Push: `cf push`. Staging takes a few minutes.
6. Get the address: `cf app career-orchestrator`. Look at `routes:`. Open `https://<that route>` in the browser, and also `https://<that route>/api/v1/meta`. You should see JSON with `"mode":"replay"`.
7. Optional, live Gemini on the deployed app (type the key yourself, never paste it into a chat):
   `cf set-env career-orchestrator APP_MODE live`, `cf set-env career-orchestrator LLM_PROVIDER gemini`, `cf set-env career-orchestrator LLM_API_KEY <your key>`, then `cf restage career-orchestrator`.
   Check `/api/v1/meta` again: mode should be `live`.

If it fails:
- `cf logs career-orchestrator --recent` shows why.
- "No matching Python version": run `cf buildpacks`, find the python_buildpack, then add a file `runtime.txt` with one line such as `python-3.12.x` using a version that buildpack supports, and push again.
- The database is stored in `/tmp` and is wiped when the app restarts. That is expected for a demo.

## Part B. Mirror the agent activity log to SAP HANA Cloud (Slice 2)

What it does: every line of "What ran for you" is also written to a table `CO_AGENT_TRACE` in SAP HANA Cloud. SQLite still runs the app. If HANA is stopped or unreachable, the app does not notice.
It sends only the short summaries the dashboard already shows, the agent name, the mode and a time. No names and no CV text.

1. In the BTP cockpit, open your trial subaccount, then **Service Marketplace**, and open **SAP HANA Cloud**. Create the subscription / open **SAP HANA Cloud Central** if the page asks you to.
2. In HANA Cloud Central choose **Create Instance**, then **SAP HANA Database**. Give it a name (for example `co-hana`). Set the `DBADMIN` password and write it down.
3. In **Advanced Settings** set connections to **Allow all IP addresses**, so your laptop and Cloud Foundry can reach it. Create the instance and wait until it shows **Running**.
4. On the instance, open the **Actions** menu and choose **Copy SQL Endpoint**. It looks like `xxxx.hana.trial-eu10.hanacloud.ondemand.com:443`. The part before `:443` is your `HANA_HOST`.
5. Test from your laptop first:
   `pip install -r backend/requirements-sap.txt`
   `HANA_HOST=<host> HANA_USER=DBADMIN HANA_PASSWORD='<password>' python3 tools_hana_check.py`
   It should print "Connected" and a row count. If it cannot connect, fix this before going on (usual causes: instance stopped, or "Allow all IP addresses" not set).
6. Give the deployed app the settings:
   `cf set-env career-orchestrator HANA_HOST <host>`
   `cf set-env career-orchestrator HANA_USER DBADMIN`
   `cf set-env career-orchestrator HANA_PASSWORD '<password>'`
   `cf restage career-orchestrator`
7. Use the app once (sign in, build a profile, choose a role). Then in HANA Cloud Central, on your instance choose **Open in SAP HANA Database Explorer**, open your database, then **Tables**, then `CO_AGENT_TRACE`, then **Open Data**. You should see the rows. Take a screenshot for your slides.
8. **Every day before the demo:** a trial HANA instance shuts down by itself at the end of the day. In HANA Cloud Central use **Actions, Start**, and wait for Running. If you forget, the app still works; only the HANA copy is missing.

Using a dedicated database user instead of `DBADMIN` is better practice. For a demo, `DBADMIN` is acceptable, but do not reuse that password anywhere else.

## What to say on stage (accurate wording)
- "The app is deployed on SAP BTP Cloud Foundry." (only after Part A step 6 works)
- "Each agent step is also stored in SAP HANA Cloud." (only after Part B step 7 works)
- For anything below, say "can be replaced by", not "uses".

## Parts of the code that could be replaced by SAP services (not built, not tested)
Availability in a trial account has not been checked for any row below, so confirm before you promise it.

| Part of Career Orchestrator | Where in the code | SAP service that could take its place |
|---|---|---|
| Web hosting of the FastAPI app | `backend/app/main.py` | SAP BTP Cloud Foundry runtime (used in Part A) |
| Database for profiles and the agent log | `backend/app/db.py`, `schema.sql` | SAP HANA Cloud (the agent log is mirrored in Part B) |
| Language model calls (Gemini) | `backend/app/llm.py`, one function `ask_json` | SAP Generative AI Hub in SAP AI Core |
| Reading a CV (PDF or Word) | `engine/cv.py` | SAP Document Information Extraction |
| Skill list and matching of skills | `data/v2/skills.json`, `engine/extract_rules.py` | Skills and talent data in SAP SuccessFactors (Talent Intelligence Hub) |
| Course catalogue | `data/v2/role_courses.json` | SAP Learning content, or SuccessFactors Learning |
| The six agents as one flow | `backend/app/orchestrator.py` | SAP Joule Studio agents / SAP Build Process Automation |
| Demo sign-in | `frontend/screens/signin.js` | SAP Identity Authentication Service with SAP Authorization and Trust Management |
| Job roles and openings | `data/v2/roles.json` | SuccessFactors Recruiting or Opportunity Marketplace |
| Screens | `frontend/` | SAPUI5 / SAP Fiori, or SAP Build Apps |
| Logs | server console | SAP Cloud Logging |
