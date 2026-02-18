"""Starlette Blog — Blog webapp with auth, CRUD, and lime-green theme."""

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
POSTS_FILE = DATA_DIR / "posts.json"
USERS_FILE = DATA_DIR / "users.json"
SECRET_KEY_FILE = DATA_DIR / ".secret_key"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def youtube_thumb(url: str) -> str:
    """Extract YouTube video ID and return thumbnail URL."""
    m = re.search(r"(?:v=|youtu\.be/|/embed/|/shorts/)([\w-]{11})", url or "")
    if m:
        return f"https://img.youtube.com/vi/{m.group(1)}/hqdefault.jpg"
    return ""


templates.env.filters["youtube_thumb"] = youtube_thumb


def _cache_bust() -> str:
    """Return a version string based on static file modification times."""
    ts = 0
    for f in (BASE_DIR / "static").iterdir():
        ts = max(ts, int(f.stat().st_mtime))
    return str(ts)


STATIC_VERSION = _cache_bust()
templates.env.globals["v"] = STATIC_VERSION


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_secret_key() -> str:
    """Return a persistent secret key, creating one if needed."""
    if SECRET_KEY_FILE.exists():
        return SECRET_KEY_FILE.read_text().strip()
    key = secrets.token_hex(32)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SECRET_KEY_FILE.write_text(key)
    return key


def load_posts() -> list[dict]:
    if not POSTS_FILE.exists():
        return []
    with open(POSTS_FILE) as f:
        return json.load(f)


def save_posts(posts: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=2)


def load_users() -> list[dict]:
    if not USERS_FILE.exists():
        return []
    with open(USERS_FILE) as f:
        return json.load(f)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return hashed.hex(), salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    candidate, _ = hash_password(password, salt)
    return secrets.compare_digest(candidate, hashed)


def read_time(body: str) -> int:
    words = len(body.split())
    return max(1, round(words / 200))


def get_user(request: Request) -> dict | None:
    username = request.session.get("username")
    if not username:
        return None
    users = load_users()
    for u in users:
        if u["username"] == username:
            return u
    return None


def make_teaser(body: str, teaser: str = "") -> str:
    if teaser.strip():
        return teaser.strip()
    plain = body[:200]
    if len(body) > 200:
        plain += "..."
    return plain


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

async def homepage(request: Request):
    posts = load_posts()
    posts.sort(key=lambda p: p.get("created", ""), reverse=True)

    tag = request.query_params.get("tag", "")
    all_tags_set = set()
    for p in posts:
        for t in p.get("tags", []):
            all_tags_set.add(t)
    all_tags = sorted(all_tags_set)

    if tag:
        filtered = [p for p in posts if tag in p.get("tags", [])]
    else:
        filtered = posts

    featured = filtered[0] if filtered else None
    grid_posts = filtered[1:] if filtered else []

    user = get_user(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "posts": grid_posts,
        "featured": featured,
        "all_tags": all_tags,
        "active_tag": tag,
        "user": user,
    })


async def post_detail(request: Request):
    slug = request.path_params["slug"]
    posts = load_posts()
    post = next((p for p in posts if p["slug"] == slug), None)
    if not post:
        return RedirectResponse(url="/", status_code=302)
    user = get_user(request)
    return templates.TemplateResponse("post.html", {
        "request": request,
        "post": post,
        "user": user,
    })


async def login(request: Request):
    user = get_user(request)
    if request.method == "GET":
        return templates.TemplateResponse("login.html", {
            "request": request,
            "user": user,
            "error": "",
        })

    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "")

    users = load_users()
    for u in users:
        if u["username"] == username and verify_password(password, u["password"], u["salt"]):
            request.session["username"] = username
            return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "user": None,
        "error": "Invalid username or password.",
    })


async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


async def new_post(request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    if request.method == "GET":
        return templates.TemplateResponse("editor.html", {
            "request": request,
            "user": user,
            "post": None,
            "error": "",
        })

    form = await request.form()
    title = form.get("title", "").strip()
    tags_raw = form.get("tags", "").strip()
    tags = tags_raw.split() if tags_raw else []
    teaser = form.get("teaser", "").strip()
    body = form.get("body", "").strip()
    youtube_url = form.get("youtube_url", "").strip()
    github_url = form.get("github_url", "").strip()
    huggingface_url = form.get("huggingface_url", "").strip()
    twitter_url = form.get("twitter_url", "").strip()
    arxiv_url = form.get("arxiv_url", "").strip()
    image = form.get("image")

    if not title or not body:
        return templates.TemplateResponse("editor.html", {
            "request": request,
            "user": user,
            "post": {"title": title, "tags": tags, "teaser": teaser, "body": body,
                     "youtube_url": youtube_url, "github_url": github_url,
                     "huggingface_url": huggingface_url, "twitter_url": twitter_url,
                     "arxiv_url": arxiv_url},
            "error": "Title and body are required.",
        })

    slug = slugify(title)
    posts = load_posts()
    existing_slugs = {p["slug"] for p in posts}
    if slug in existing_slugs:
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    image_filename = ""
    if image and hasattr(image, "filename") and image.filename:
        ext = Path(image.filename).suffix or ".jpg"
        image_filename = f"{slug}{ext}"
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        dest = UPLOADS_DIR / image_filename
        contents = await image.read()
        with open(dest, "wb") as f:
            f.write(contents)

    now = datetime.now(timezone.utc).isoformat()
    post = {
        "title": title,
        "slug": slug,
        "tags": tags,
        "teaser": make_teaser(body, teaser),
        "body": body,
        "image": image_filename,
        "youtube_url": youtube_url,
        "github_url": github_url,
        "huggingface_url": huggingface_url,
        "twitter_url": twitter_url,
        "arxiv_url": arxiv_url,
        "author": user.get("display_name", user["username"]),
        "created": now,
        "updated": now,
        "read_time": read_time(body),
    }
    posts.append(post)
    save_posts(posts)
    return RedirectResponse(url=f"/post/{slug}", status_code=302)


async def edit_post(request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    slug = request.path_params["slug"]
    posts = load_posts()
    post = next((p for p in posts if p["slug"] == slug), None)
    if not post:
        return RedirectResponse(url="/", status_code=302)

    if request.method == "GET":
        return templates.TemplateResponse("editor.html", {
            "request": request,
            "user": user,
            "post": post,
            "error": "",
        })

    form = await request.form()
    title = form.get("title", "").strip()
    tags_raw = form.get("tags", "").strip()
    tags = tags_raw.split() if tags_raw else []
    teaser = form.get("teaser", "").strip()
    body = form.get("body", "").strip()
    youtube_url = form.get("youtube_url", "").strip()
    github_url = form.get("github_url", "").strip()
    huggingface_url = form.get("huggingface_url", "").strip()
    twitter_url = form.get("twitter_url", "").strip()
    arxiv_url = form.get("arxiv_url", "").strip()
    image = form.get("image")

    if not title or not body:
        post_data = {**post, "title": title, "tags": tags, "teaser": teaser, "body": body,
                     "youtube_url": youtube_url, "github_url": github_url,
                     "huggingface_url": huggingface_url, "twitter_url": twitter_url,
                     "arxiv_url": arxiv_url}
        return templates.TemplateResponse("editor.html", {
            "request": request,
            "user": user,
            "post": post_data,
            "error": "Title and body are required.",
        })

    post["title"] = title
    post["tags"] = tags
    post["teaser"] = make_teaser(body, teaser)
    post["body"] = body
    post["youtube_url"] = youtube_url
    post["github_url"] = github_url
    post["huggingface_url"] = huggingface_url
    post["twitter_url"] = twitter_url
    post["arxiv_url"] = arxiv_url
    post["updated"] = datetime.now(timezone.utc).isoformat()
    post["read_time"] = read_time(body)

    if image and hasattr(image, "filename") and image.filename:
        ext = Path(image.filename).suffix or ".jpg"
        image_filename = f"{post['slug']}{ext}"
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        dest = UPLOADS_DIR / image_filename
        contents = await image.read()
        with open(dest, "wb") as f:
            f.write(contents)
        post["image"] = image_filename

    save_posts(posts)
    return RedirectResponse(url=f"/post/{post['slug']}", status_code=302)


async def delete_post(request: Request):
    user = get_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    slug = request.path_params["slug"]
    posts = load_posts()
    post = next((p for p in posts if p["slug"] == slug), None)

    if post:
        if post.get("image"):
            img_path = UPLOADS_DIR / post["image"]
            if img_path.exists():
                img_path.unlink()
        posts = [p for p in posts if p["slug"] != slug]
        save_posts(posts)

    return RedirectResponse(url="/", status_code=302)


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

routes = [
    Route("/", homepage),
    Route("/post/{slug}", post_detail),
    Route("/login", login, methods=["GET", "POST"]),
    Route("/logout", logout),
    Route("/new", new_post, methods=["GET", "POST"]),
    Route("/edit/{slug}", edit_post, methods=["GET", "POST"]),
    Route("/delete/{slug}", delete_post, methods=["POST"]),
    Mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static"),
    Mount("/uploads", StaticFiles(directory=str(BASE_DIR / "uploads")), name="uploads"),
]

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = Starlette(
    routes=routes,
    middleware=[
        Middleware(SessionMiddleware, secret_key=get_secret_key()),
    ],
)

if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
