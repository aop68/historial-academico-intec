from flask import Flask, render_template, request, send_file
from io import BytesIO
from pdf_gen import generate_pdf
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generar", methods=["POST"])
def generar():
    student_data = {
        "id":               request.form.get("id", ""),
        "matricula":        request.form.get("matricula", ""),
        "nombre":           request.form.get("nombre", ""),
        "programa":         request.form.get("programa", ""),
        "cond_ac":          request.form.get("cond_ac", ""),
        "estatus":          request.form.get("estatus", ""),
        "cred_convalidados": request.form.get("cred_convalidados", ""),
        "cred_aprobados":   request.form.get("cred_aprobados", ""),
        "cred_programa":    request.form.get("cred_programa", ""),
        "asig_aprobadas":   request.form.get("asig_aprobadas", ""),
        "asig_total":       request.form.get("asig_total", ""),
    }

    # Parse trimester data sent as JSON
    trimesters_json = request.form.get("trimesters_data", "[]")
    trimesters = json.loads(trimesters_json)

    pdf_bytes = generate_pdf(student_data, trimesters)

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="Historial_Academico.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)
