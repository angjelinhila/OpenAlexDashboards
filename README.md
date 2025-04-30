# Dash Research Dashboard

This is an interactive data dashboard built using [Plotly Dash](https://dash.plotly.com/) to visualize research trends, topics, citations, and co-authorship networks.

## 🚀 Features

- 📊 Publications by year and topic
- 🧠 Topic evolution and citation trends
- 📋 Author table sorted by citations and paper count
- 🔗 Interactive co-authorship network
- 🧩 Author-paper bipartite graph
- 🔍 Keyword and topic filtering

## 🗂 Dataset

The dashboard uses a CSV file (`dashboard_data_with_abstract.csv`) which must be included in the root directory of the app.

## 🛠 Files

- `app.py`: Main Dash app script
- `requirements.txt`: Dependencies for deployment
- `Procfile`: Tells Render how to launch the app
- `dashboard_data_with_abstract.csv`: Dataset used by the app

## 🌐 Live Deployment (Optional)

This app is designed to be deployed on [Render](https://render.com):

### ✅ Steps:
1. Push this repository to GitHub
2. Go to [https://render.com](https://render.com) and create a new **Web Service**
3. Connect to this GitHub repo
4. Set:
   - **Runtime**: Python 3
   - **Start Command**: `python app.py`
5. Wait for deployment → you’ll get a public URL!

## 📦 Local Setup (Optional)

To run locally:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
pip install -r requirements.txt
python app.py
```

Then visit `http://127.0.0.1:8050/` in your browser.

---

Made with 🧠 and 🐍 using Dash, Plotly, and a bit of wizardry.