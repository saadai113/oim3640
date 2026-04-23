import os
import tempfile
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB limit

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt", "rtf", "html", "htm"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/match", methods=["POST"])
def match():
    files = request.files.getlist("resumes")
    job_description = request.form.get("job_description", "").strip()

    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "No resume files uploaded."}), 400
    if not job_description:
        return jsonify({"error": "Job description is required."}), 400

    bad = [f.filename for f in files if f.filename and not allowed_file(f.filename)]
    if bad:
        return jsonify({"error": f"Unsupported file type(s): {', '.join(bad)}"}), 400

    try:
        from matchllm import rank_candidates

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = []
            for f in files:
                if f.filename:
                    path = os.path.join(tmpdir, secure_filename(f.filename))
                    f.save(path)
                    paths.append((path, f.filename))

            results = []
            for path, original_name in paths:
                from resume_parser import parse_resume
                from matchllm import match_resume_to_job

                resume = parse_resume(path)
                if resume is None:
                    results.append({
                        "filename": original_name,
                        "name": original_name,
                        "error": "Could not extract text from this file.",
                    })
                    continue

                match_result = match_resume_to_job(resume, job_description)
                if match_result is None:
                    results.append({
                        "filename": original_name,
                        "name": resume.get("name", original_name),
                        "error": "Matching failed.",
                    })
                    continue

                results.append({
                    "filename": original_name,
                    "name": resume.get("name", original_name),
                    "email": resume.get("email", ""),
                    "location": resume.get("location", ""),
                    "years_of_experience": resume.get("years_of_experience", 0),
                    "skills": resume.get("skills", []),
                    "match": match_result,
                })

        results.sort(
            key=lambda r: r.get("match", {}).get("overall_score", -1),
            reverse=True,
        )
        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
