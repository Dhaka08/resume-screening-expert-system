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

# ------------------ Helper Functions ------------------
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
        if skill in text:
            found.append(skill)
    return list(set(found))

# ------------------ Core Scoring Logic ------------------
def calculate_score(resume_text: str, jd_text: str):
    resume_text = resume_text.lower()
    jd_text = jd_text.lower()

    # ---- Skill Match (40) ----
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(matched_skills))

    if len(jd_skills) == 0:
        skill_match_percent = 0
        skill_score = 0
    else:
        skill_match_percent = round((len(matched_skills) / len(jd_skills)) * 100, 2)
        skill_score = round((skill_match_percent / 100) * 40, 2)

    # ---- JD Similarity (30) ----
    docs = [resume_text, jd_text]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(docs)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    similarity_percent = round(similarity * 100, 2)
    similarity_score = round(similarity * 30, 2)

    # ---- Bonus (30) ----
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

    # ---- Final Score ----
    total_score = round(skill_score + similarity_score + bonus, 2)

    # ---- Decision Rule ----
    if total_score >= 70:
        decision = "SHORTLIST ✅"
    elif total_score >= 50:
        decision = "MAYBE ⚠️"
    else:
        decision = "REJECT ❌"

    return {
        "total_score": total_score,
        "decision": decision,
        "skill_match_percent": skill_match_percent,
        "similarity_percent": similarity_percent,
        "skill_score": skill_score,
        "similarity_score": similarity_score,
        "bonus_score": bonus,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
    }

# ------------------ Streamlit UI ------------------
st.set_page_config(
    page_title="Resume Screening Expert System",
    page_icon="✅",
    layout="centered"
)

st.title("✅ Resume Screening Expert System")
st.write(
    "Upload a resume PDF and paste a Job Description (JD). "
    "The system will evaluate the resume using an AI-based expert scoring approach."
)

uploaded_resume = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area("📝 Paste Job Description", height=180)

if st.button("🚀 Screen Resume"):
    if uploaded_resume is None:
        st.error("Please upload a resume PDF.")
    elif job_description.strip() == "":
        st.error("Please paste the Job Description.")
    else:
        with st.spinner("Analyzing resume..."):
            resume_text = extract_text_from_pdf(uploaded_resume)

            if resume_text.strip() == "":
                st.error("Could not extract text from this PDF. Please try another file.")
            else:
                result = calculate_score(resume_text, job_description)

                # ---- Decision & Score ----
                st.success(f"Decision: {result['decision']}")
                st.metric("⭐ Total Score (out of 100)", result["total_score"])
                st.progress(min(int(result["total_score"]), 100))

                # ---- AI Explanation ----
                st.subheader("🧠 AI Explanation")
                st.info(
                    f"""
                    • Skill Match: **{result['skill_match_percent']}%**  
                    • JD Similarity: **{result['similarity_percent']}%**  
                    • Bonus Score: **{result['bonus_score']} / 30**  
                    """
                )

                # ---- Skills ----
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("✅ Matched Skills")
                    if result["matched_skills"]:
                        for skill in result["matched_skills"]:
                            st.success(skill.upper())
                    else:
                        st.write("No matched skills found.")

                with col2:
                    st.subheader("❌ Missing Skills")
                    if result["missing_skills"]:
                        for skill in result["missing_skills"]:
                            st.warning(skill.upper())
                    else:
                        st.write("No major missing skills detected.")

                # ---- Suggestions ----
                st.subheader("💡 AI Suggestions")
                if result["decision"].startswith("REJECT"):
                    st.write("• Resume does not align well with the job description.")
                    st.write("• Consider improving skill relevance and project descriptions.")
                elif result["decision"].startswith("MAYBE"):
                    st.write("• Add missing skills if you have hands-on experience.")
                    st.write("• Improve keyword alignment between resume and JD.")
                else:
                    st.write("• Strong profile. Proceed with interview preparation.")
