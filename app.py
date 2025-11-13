#!/usr/bin/env python3
# Simple Flask quiz app: carga questions.json, muestra 10 preguntas al azar,
# baraja preguntas y opciones, guarda la selección en session para calificar,
# y al enviar muestra la misma pantalla en modo "revisión" marcando respuestas.
import json
import os
import random
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    session,
)

# APP_USER ya no es necesario - eliminado para simplificar
QUESTIONS_FILE = "questions.json"
RESULTS_DIR = "results"
NUM_QUESTIONS = 10
SHUFFLE_DEFAULT = True  # barajar preguntas y opciones

app = Flask(__name__)
# Configuración de clave secreta: usa variable de entorno en producción
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))


def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        qs = json.load(f)
    return qs


def prepare_quiz(
    questions, num_questions=NUM_QUESTIONS, shuffle_questions=True, shuffle_options=True
):
    """
    Selecciona num_questions aleatorias (sin repetir) a partir de questions,
    y para cada una prepara las opciones (posible barajado) y calcula
    los índices correctos relativos al orden mostrado.
    Devuelve una lista con preguntas preparadas (serializable).
    """
    if num_questions >= len(questions):
        sample = list(questions)
    else:
        sample = random.sample(questions, k=num_questions)

    if shuffle_questions:
        random.shuffle(sample)

    prepared = []
    for q in sample:
        opts = list(q["options"])
        indexed = list(enumerate(opts))  # (orig_idx, text)
        if shuffle_options:
            random.shuffle(indexed)
        display_options = [t[1] for t in indexed]
        # orig_correct (set of original indices)
        orig_correct = set(q.get("answer", []))
        # compute displayed indices that correspond to orig_correct
        display_correct = [
            i for i, (orig_idx, _) in enumerate(indexed) if orig_idx in orig_correct
        ]
        prepared.append(
            {
                "id": q.get("id", ""),
                "question": q.get("question", ""),
                "options": display_options,
                "correct_display": display_correct,
            }
        )
    return prepared


@app.route("/", methods=["GET"])
def quiz():
    questions = load_questions()
    prepared = prepare_quiz(
        questions, shuffle_questions=SHUFFLE_DEFAULT, shuffle_options=SHUFFLE_DEFAULT
    )
    # Guardar en sesión para usar en submit
    session["current_quiz"] = prepared
    # We'll render all questions in one form.
    return render_template("quiz.html", questions=prepared)


@app.route("/debug", methods=["GET"])
def quiz_debug():
    questions = load_questions()
    prepared = prepare_quiz(questions, shuffle_questions=False, shuffle_options=False)
    # We'll render all questions in one form.
    return render_template("quiz_debug.html", questions=prepared)


@app.route("/submit", methods=["POST"])
def submit():
    # Recuperamos la selección que estaba en session
    prepared = session.get("current_quiz")
    if not prepared:
        flash("No hay examen en curso. Se generará uno nuevo.")
        return redirect(url_for("quiz"))

    total = 0
    max_score = len(prepared)
    details = []

    for q in prepared:
        qid = q.get("id")
        name = f"q_{qid}"
        # read chosen indices relative to displayed order
        raw = request.form.getlist(name)
        chosen = set()
        for r in raw:
            try:
                chosen.add(int(r))
            except Exception:
                pass
        correct_set = set(q.get("correct_display", []))
        is_correct = chosen == correct_set
        score = 1 if is_correct else 0
        total += score
        details.append(
            {
                "qid": q.get("id"),
                "question": q.get("question"),
                "options": q.get("options"),
                "correct_display": sorted(list(correct_set)),
                "chosen": sorted(list(chosen)),
                "score": score,
            }
        )

    percent = (total / max_score) * 100 if max_score else 0.0

    # Guardar resultados en JSON
    os.makedirs(RESULTS_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"results_{ts}.json"
    outpath = os.path.join(RESULTS_DIR, filename)
    out = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_score": total,
        "max_score": max_score,
        "percent": percent,
        "details": details,
    }
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # En modo review volvemos a renderizar la misma plantilla de quiz pero con review=True
    # y le pasamos los detalles para que marque las respuestas.
    return render_template(
        "quiz.html",
        questions=prepared,
        review=True,
        summary={
            "total": total,
            "max_score": max_score,
            "percent": percent,
            "result_file": filename,
        },
        details_map={d["question"]: d for d in details},
    )


@app.route("/results/<path:filename>")
def get_result_file(filename):
    return send_from_directory(RESULTS_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    # Para desarrollo local
    app.run(debug=True, port=5000)
else:
    # Para producción (Heroku, etc.)
    # Usar una clave secreta fija en producción
    app.secret_key = os.environ.get('SECRET_KEY', 'tu-clave-secreta-aqui-cambiar-en-produccion')
