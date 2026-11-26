# Get a public link for the web app

Your code is already public on GitHub:
**https://github.com/BuildWithAni/python-project**

## Option A — Streamlit Community Cloud (recommended, free)

1. Open **https://share.streamlit.io** and sign in with your GitHub account
   (`BuildWithAni`).
2. Click **New app**.
3. Fill in the form:
   - **Repository:** `BuildWithAni/python-project`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
4. Click **Deploy**. The first build takes 1–3 minutes.
5. You get a link like `https://python-project.streamlit.app` — that is the link
   you can send to anyone.

No extra settings are needed: dependencies are installed automatically from
`requirements.txt`.

## Option B — Hugging Face Spaces (alternative, free)

1. Go to **https://huggingface.co/new-space**.
2. Name it (e.g. `student-report-card`), choose **Streamlit** as the SDK, set it
   to **Public**, and create the space.
3. Upload these files, keeping the folder structure:
   - `streamlit_app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - the whole `src/` folder
   - `data/students.csv`
4. The space builds automatically. Your link is
   `https://huggingface.co/spaces/<your-username>/<space-name>`.

You can also upload with Git instead of the browser:

```bash
git clone https://huggingface.co/spaces/<your-username>/<space-name>
cd <space-name>
copy the project files here
git add -A
git commit -m "Deploy report card app"
git push
```

## Option C — quick temporary link on your Wi-Fi

```bash
python -m streamlit run streamlit_app.py --server.address 0.0.0.0
```

Share the **Network URL** printed in the terminal. This works only for people on
the same network and stops when you close the terminal.

## Things to know

- Free hosts put apps to sleep. The first visit after a while may take ~30 seconds.
- Changes made in the app are kept in a CSV for that session; on free hosts the
  file resets when the app restarts. Use **Download full report (CSV)** to keep a copy.
- To update the live app later, push new code and Streamlit Cloud redeploys it:

```bash
git add -A
git commit -m "Update app"
git push
```

## Test it locally first

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
