import io
import os

import anyio.to_thread
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from . import db
from .qr import generate_qr_png
from .questions import CATEGORY_LABELS, CATEGORY_LABELS_RUBY, CHOICES, QUESTIONS, TOTAL_QUESTIONS
from .scoring import compute_scores, determine_hero

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "maniwa-gx-admin")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

BASE_DIR = os.path.dirname(__file__)
HEROES_IMAGE_DIR = os.path.join(BASE_DIR, "static", "images", "heroes")
HEROES_IMAGE_EXTENSIONS = ["svg", "png", "jpg", "jpeg", "webp"]


def resolve_hero_image_url(slug: str) -> str:
    """heroesフォルダ内に置かれている実際の拡張子を自動判定する。
    差し替え作業者は拡張子を気にせず同じファイル名（例: mori_science_ranger.png）を置くだけでよい。"""
    for ext in HEROES_IMAGE_EXTENSIONS:
        if os.path.isfile(os.path.join(HEROES_IMAGE_DIR, f"{slug}.{ext}")):
            return f"/static/images/heroes/{slug}.{ext}"
    return f"/static/images/heroes/{slug}.svg"

app = FastAPI(title="GXヒーロー診断")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site="lax")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.on_event("startup")
def on_startup() -> None:
    db.init_db()
    # 同時接続最大100人を想定し、デフォルトのスレッドプール上限（既定40）を引き上げておく
    anyio.to_thread.current_default_thread_limiter().total_tokens = 150


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"total": TOTAL_QUESTIONS})


@app.post("/start")
def start(request: Request):
    request.session["answers"] = [None] * TOTAL_QUESTIONS
    request.session["saved"] = False
    return RedirectResponse("/question/1", status_code=303)


@app.get("/question/{n}", response_class=HTMLResponse)
def question(request: Request, n: int):
    answers = request.session.get("answers")
    if not answers or n < 1 or n > TOTAL_QUESTIONS:
        return RedirectResponse("/", status_code=303)
    q = QUESTIONS[n - 1]
    return templates.TemplateResponse(
        request,
        "question.html",
        {
            "question": q,
            "category_label": CATEGORY_LABELS_RUBY[q["category"]],
            "n": n,
            "total": TOTAL_QUESTIONS,
            "progress": round(n / TOTAL_QUESTIONS * 100),
            "choices": CHOICES,
            "selected": answers[n - 1],
        },
    )


@app.post("/question/{n}")
def answer_question(request: Request, n: int, value: int = Form(...)):
    answers = request.session.get("answers")
    if not answers or n < 1 or n > TOTAL_QUESTIONS or value < 1 or value > 5:
        return RedirectResponse("/", status_code=303)
    answers[n - 1] = value
    request.session["answers"] = answers
    if n < TOTAL_QUESTIONS:
        return RedirectResponse(f"/question/{n + 1}", status_code=303)
    return RedirectResponse("/result", status_code=303)


@app.get("/result", response_class=HTMLResponse)
def result(request: Request):
    answers = request.session.get("answers")
    if not answers or any(a is None for a in answers):
        return RedirectResponse("/", status_code=303)

    scores, max_in_category = compute_scores(answers)
    hero = determine_hero(scores, max_in_category)

    if not request.session.get("saved"):
        db.save_response(answers, scores, hero["name"], request.headers.get("user-agent"))
        request.session["saved"] = True

    hero_image_url = resolve_hero_image_url(hero["slug"])
    return templates.TemplateResponse(
        request, "result.html", {"hero": hero, "hero_image_url": hero_image_url}
    )


# ---- 管理画面 ----

def _is_admin(request: Request) -> bool:
    return bool(request.session.get("admin_auth"))


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, qr_url: str | None = None):
    if not _is_admin(request):
        return templates.TemplateResponse(request, "admin_login.html", {"error": None})
    rows = db.list_responses()
    return templates.TemplateResponse(
        request,
        "admin.html",
        {"rows": rows, "category_labels": CATEGORY_LABELS, "qr_url": qr_url},
    )


@app.get("/admin/qr")
def admin_qr(request: Request, url: str):
    if not _is_admin(request):
        return RedirectResponse("/admin", status_code=303)
    png_bytes = generate_qr_png(url)
    return StreamingResponse(io.BytesIO(png_bytes), media_type="image/png")


@app.post("/admin/login")
def admin_login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["admin_auth"] = True
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        request, "admin_login.html", {"error": "パスワードが違います"}, status_code=401
    )


@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session["admin_auth"] = False
    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/export.csv")
def admin_export(request: Request):
    if not _is_admin(request):
        return RedirectResponse("/admin", status_code=303)
    csv_text = db.export_csv()
    return StreamingResponse(
        io.StringIO(csv_text),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=gx_hero_responses.csv"},
    )
