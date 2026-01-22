from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Skills dictionary for matching (you can expand later)
DEFAULT_SKILLS = [
    "python", "java", "c++", "sql", "mongodb",
    "machine learning", "deep learning", "data science",
    "flask", "django", "react", "node", "html", "css", "javascript",
    "power bi", "excel",
    "numpy", "pandas", "scikit-learn", "tensorflow", "pytorch"
]

def extract_skills(text: str, skill_list=DEFAULT_SKILLS):
    """
    Extracts skills found in the text using a predefined skill list.
    """
    text = text.lower()
    found = []
    for skill in skill_list:
        if skill.lower() in text:
            found.append(skill)
    return list(set(found))  # unique


def calculate_score(resume_text: str, jd_text: str):
    """
    Resume Screening Expert System Scoring:
    - Skills Match (40)
    - TF-IDF Similarity (30)
    - Bonus Rules (30)
    Total = 100
    """
    resume_text = resume_text.lower()
    jd_text = jd_text.lower()

    # ---- 1) Skill Match Score (40) ----
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

    # ---- 2) Text Similarity Score (30) ----
    docs = [resume_text, jd_text]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(docs)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    similarity_score = round(similarity * 30, 2)

    # ---- 3) Bonus Rule Score (30) ----
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

    # ---- Expert Decision Rule ----
    if total_score >= 70:
        decision = "SHORTLIST ✅"
    elif total_score >= 50:
        decision = "MAYBE ⚠️"
    else:
        decision = "REJECT ❌"

    # ---- Explanation ----
    explanation = [
        f"Skill Match: {round(skill_match_percent * 100, 2)}% → {skill_score}/40",
        f"JD Similarity: {round(similarity * 100, 2)}% → {similarity_score}/30",
        f"Bonus Score: {bonus}/30 (internship/project/github/certification)"
    ]

    if matched_skills:
        explanation.append("Matched Skills: " + ", ".join(sorted(matched_skills)))
    if missing_skills:
        explanation.append("Missing Skills: " + ", ".join(sorted(missing_skills)))

    return {
        "total_score": total_score,
        "decision": decision,
        "skill_score": skill_score,
        "similarity_score": similarity_score,
        "bonus_score": bonus,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "similarity_percent": round(similarity * 100, 2),
        "explanation": explanation
    }
