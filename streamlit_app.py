import streamlit as st
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------ Expert System Skill List ------------------
DEFAULT_SKILLS = [
    "python", "java", "c++", "sql", "mongodb",
    "machine learning", "deep learning", "data science",
    "flask", "django", "react", "node", "html", "css", "javascript",
    "power bi", "excel",
    "numpy", "pandas", "scikit-learn", "tensorflow", "pytorch"
]

def extract_text_from_pdf(uploaded_file) -> str:
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_skills(text: str, skill_list=DEFAULT_SKILLS):
    text = text.lower()
    found = []
    for skill in skill_list:
        if skill.lower() in text:
            found.append(skill)
    return list(set(found))

def calculate_score(resume_text: str, jd_text: str):
    resume_text = resume_text.lower()
    jd_text = jd_text.lower()

    # Skill Match (40)
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(matched_skills))

    if len(jd_skills) == 0:
        skill_match_percent = 0
        skill_score = 0
    else:
        skill_match_percent = len(matched_skills) / len(jd_skills)
        skill_score = round(skill_match_percent * 40, 2)

    # Similarity (30)
    docs = [resume_text, jd_text]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(docs)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    similarity_score = round(similarity * 30, 2)

    # Bonus (30)
    bonus = 0
    if "internship" in resume_text:
        bonus += 8
    if "project" in resume_text:
        bonus += 8
    if "github" in resume_text:
        bonus += 7
    if "certification" in resume_text or "certified" in resume_text:
        bonus += 7

    bonus = min(bonus, 30)

    total_score = round(skill_score + similarity_score + bonus, 2)

    # Decision
    if total_score >= 70:
        decision = "SHORTLIST ✅"
    elif total_score >= 50:
        decision = "MAYBE ⚠️"
    else:
        decision = "REJECT ❌"

    explanation = [
        f"Skill Match: {round(skill_match_percent * 100, 2)}% → {skill_score}/40",
        f"JD Similarity: {round(similarity * 100, 2)}% → {similarity_score}/30",
        f"Bonus Score: {bonus}/30 (internship/project/github/certification)"
    ]

    return {
        "total_score": total_score,
        "decision": decision,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "explanation": explanation
    }

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Resume Screening Expert System", page_icon="✅", layout="centered")

st.title("✅ Resume Screening Expert System")
st.write("Upload a resume PDF and paste a Job Description (JD) to get a screening score and decision.")

uploaded_resume = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area("📝 Paste Job Description", height=180)

if st.button("🚀 Screen Resume"):
    if uploaded_resume is None:
        st.error("Please upload a resume PDF.")
    elif job_description.strip() == "":
        st.error("Please paste the Job Description.")
    else:
        with st.spinner("Screening resume..."):
            resume_text = extract_text_from_pdf(uploaded_resume)

            if resume_text.strip() == "":
                st.error("Could not extract text from this PDF. Try another resume file.")
            else:
                result = calculate_score(resume_text, job_description)

                st.success(f"✅ Decision: {result['decision']}")
                st.metric("⭐ Total Score", result["total_score"])

                st.subheader("📌 Explanation")
                for line in result["explanation"]:
                    st.write("•", line)

                st.subheader("✅ Matched Skills")
                st.write(result["matched_skills"] if result["matched_skills"] else "None")

                st.subheader("❌ Missing Skills")
                st.write(result["missing_skills"] if result["missing_skills"] else "None")
