# WorkLab 📝  
An advanced To-Do application built with **FastAPI** (backend) and **Streamlit** (frontend).  
WorkLab helps you manage daily tasks, track progress with a clean dashboard, and generate detailed reports with an intuitive UI.  

## 🚀 Features
- ✅ Manage daily tasks with ease  
- 📊 Interactive dashboard for productivity insights  
- 📝 Export and view reports  
- 🎨 Modern, user-friendly interface  
- ⚡ Powered by FastAPI (backend) and Streamlit (frontend)  
- 👤 Developed by [Om Pandey](https://iamompandey.it)  

---

## 📂 Project Structure
```
WorkLab/
│── models.py        # Database models  
│── main.py          # FastAPI backend entry point  
│── app.py           # Streamlit frontend entry point  
│── requirements.txt # Dependencies  
│── README.md        # Project documentation  
```

---

## 🔧 Installation

Clone the repository:

```bash
git clone https://github.com/ompandey07/WorkLab.git
cd WorkLab
```

Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

### 1. Start the FastAPI Backend  
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start the Streamlit Frontend  
```bash
streamlit run app.py
```

- Backend will run on: [http://localhost:8000](http://localhost:8000)  
- Frontend will run on: [http://localhost:8501](http://localhost:8501)  

---

## 📸 Screenshots
(Add screenshots of dashboard, reports, and task management here)  

---

## 🌐 Links
- GitHub Repo: [WorkLab](https://github.com/ompandey07/WorkLab)  
- Developer Portfolio: [iamompandey.it](https://iamompandey.it)  

---

## 🤝 Contributing
Contributions are welcome!  
- Fork the repo  
- Create a new branch (`feature-xyz`)  
- Commit changes  
- Open a Pull Request  

---

## 📜 License
This project is licensed under the **MIT License**.  