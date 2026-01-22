import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from parser import extract_text_from_pdf
from scorer import calculate_score

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Resume Screening Expert System API running ✅",
        "endpoints": {
            "GET /": "Health check",
            "GET /test": "Browser upload page",
            "POST /screen": "Upload resume PDF + job_description text"
        }
    })


@app.route("/test", methods=["GET"])
def test_page():
    return """
    <h2>Resume Screening Test Page ✅</h2>
    <form action="/screen" method="POST" enctype="multipart/form-data">
      <label>Resume PDF:</label><br>
      <input type="file" name="resume" accept=".pdf" required><br><br>

      <label>Job Description:</label><br>
      <textarea name="job_description" rows="10" cols="70" required></textarea><br><br>

      <button type="submit">Screen Resume</button>
    </form>
    """


@app.route("/screen", methods=["POST"])
def screen_resume():
    # Debug prints
    print("FILES KEYS:", list(request.files.keys()))
    print("FORM DATA:", request.form)

    # Accept resume file from any key (resume/file/upload)
    resume_file = None
    for key in ["resume", "file", "upload"]:
        if key in request.files:
            resume_file = request.files[key]
            break

    if resume_file is None:
        return jsonify({
            "error": "Resume PDF not provided",
            "hint": "Send file with key name 'resume'",
            "received_file_keys": list(request.files.keys())
        }), 400

    job_description = request.form.get("job_description", "").strip()
    if job_description == "":
        return jsonify({"error": "Job description is empty"}), 400

    # Save uploaded file
    filename = resume_file.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    resume_file.save(save_path)

    # Extract text from PDF
    resume_text = extract_text_from_pdf(save_path)
    if not resume_text:
        return jsonify({"error": "Could not extract text from PDF"}), 400

    # Score resume
    result = calculate_score(resume_text, job_description)

    return jsonify({
        "resume_filename": filename,
        "result": result
    })


if __name__ == "__main__":
    app.run(debug=True)
