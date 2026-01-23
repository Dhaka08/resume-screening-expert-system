# Resume Screening Expert System ✅

A Flask-based **Resume Screening Expert System** that evaluates a candidate’s resume against a Job Description (JD) and returns:

- ✅ Fit Score (0–100)
- ✅ Decision: SHORTLIST / MAYBE / REJECT
- ✅ Matched Skills & Missing Skills
- ✅ Explainable Rule-based Output (Expert System style)

---

## 🚀 Features

- PDF Resume Upload
- Job Description Text Input
- Skill Matching (Rule-based)
- TF-IDF Similarity (NLP)
- Bonus Rules (Internship / Projects / GitHub / Certifications)
- JSON API Response
- Browser Test Page (`/test`) for easy usage

---

## 🛠 Tech Stack

- Python
- Flask + Flask-CORS
- pdfplumber (PDF text extraction)
- scikit-learn (TF-IDF + Cosine Similarity)
- NumPy

---

## 📁 Project Structure

resume_screening_system/
└── backend/
├── uploads/
├── app.py
├── parser.py
├── scorer.py
└── requirements.txt

---

## ✅ Setup Instructions (Run Locally)

### 1) Clone the repository
```bash
git clone https://github.com/Dhaka08/resume-screening-expert-system
cd resume_screening_system
