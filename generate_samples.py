"""Generate sample blog posts, hero images, and an admin user."""

import hashlib
import json
import math
import os
import random
import secrets
from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"

# ---------------------------------------------------------------------------
# Helper: password hashing (same logic as app.py)
# ---------------------------------------------------------------------------

def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return hashed.hex(), salt


# ---------------------------------------------------------------------------
# Sample posts
# ---------------------------------------------------------------------------

POSTS = [
    {
        "title": "Builder Story: From Solo Dev to Shipping at Scale",
        "tags": ["Builders", "Engineering"],
        "teaser": "How one developer grew from weekend side projects to leading a team that ships to millions of users every day.",
        "body": (
            "Every great product starts with a single developer and an idea. This is the story of "
            "how a solo weekend project turned into a platform serving millions.\n\n"
            "It began in a coffee shop in Portland. Armed with nothing but a laptop and a vague idea "
            "about making project management less painful, I started writing code. No frameworks, no "
            "fancy tooling — just Python and a SQLite database.\n\n"
            "The first version was embarrassingly simple. A todo list with due dates and a calendar "
            "view. But people started using it. First five, then fifty, then five hundred users signed "
            "up in a single week.\n\n"
            "Scaling brought new challenges. The SQLite database that worked fine for fifty users "
            "started choking at five thousand. I migrated to PostgreSQL, added caching with Redis, and "
            "learned more about database indexing in one weekend than in four years of college.\n\n"
            "The team grew too. First a designer who made the UI actually usable. Then a backend "
            "engineer who knew more about distributed systems than I ever would. Each hire taught me "
            "something new about leadership and letting go of control.\n\n"
            "Today we serve over two million active users. The codebase has been rewritten twice. "
            "The original SQLite database is long gone. But the core idea — making project management "
            "less painful — remains exactly the same.\n\n"
            "If you're a solo developer with an idea, start building. Ship early, listen to users, "
            "and don't be afraid to throw code away and start over."
        ),
    },
    {
        "title": "Building Modern Web Apps with Spec-Driven Development",
        "tags": ["Engineering", "How-tos"],
        "teaser": "Spec-driven development puts the API contract first, letting frontend and backend teams work in parallel with confidence.",
        "body": (
            "Spec-driven development is a methodology where you define your API specification before "
            "writing any implementation code. Think of it as writing the contract before building the house.\n\n"
            "The core idea is simple: define your API using OpenAPI (formerly Swagger), then generate "
            "server stubs and client SDKs from that specification. Both teams can work in parallel, "
            "knowing exactly what the interface will look like.\n\n"
            "We adopted this approach at AgenticEdge six months ago, and the results have been "
            "remarkable. Integration bugs dropped by 60%. Sprint velocity increased because frontend "
            "and backend developers no longer blocked each other.\n\n"
            "The workflow looks like this: product defines requirements, engineering writes the "
            "OpenAPI spec, both teams review it, then implementation begins simultaneously. Mock "
            "servers let the frontend team build against realistic responses from day one.\n\n"
            "Tools like Stoplight Studio make spec authoring visual and collaborative. Prism "
            "generates mock servers automatically. TypeScript SDK generators ensure type safety "
            "end-to-end.\n\n"
            "The biggest pushback we got was that writing specs feels slow. And it is, initially. "
            "But the time you invest upfront saves multiples downstream. No more 'the API changed' "
            "surprises during integration week.\n\n"
            "If your team struggles with API integration issues or frontend-backend coordination, "
            "give spec-driven development a try. Start small with one endpoint, prove the value, "
            "then expand."
        ),
    },
    {
        "title": "How to Get SaaS Product Ideas: 7 Proven Methods",
        "tags": ["How-tos"],
        "teaser": "Finding the right SaaS idea is half the battle. Here are seven methods that consistently produce viable product concepts.",
        "body": (
            "The best SaaS ideas come from real problems. Here are seven proven methods to find "
            "ideas worth building.\n\n"
            "1. Scratch Your Own Itch\n\n"
            "The most successful SaaS products often start as internal tools. Slack started as a "
            "gaming company's internal chat tool. Basecamp started as a project management tool for "
            "a web design agency. Look at the tools you build for yourself.\n\n"
            "2. Mine Support Forums\n\n"
            "Browse Reddit, Stack Overflow, and niche forums for recurring complaints. When you see "
            "the same problem described fifty different ways, you've found a market.\n\n"
            "3. Talk to Small Business Owners\n\n"
            "Small businesses have spreadsheets they wish were software. Every awkward Excel "
            "workflow is a potential SaaS product. Ask them what takes too long.\n\n"
            "4. Unbundle Large Platforms\n\n"
            "Salesforce does everything, which means it does many things poorly. Find a feature in "
            "a large platform that deserves to be its own product.\n\n"
            "5. Improve Existing Solutions\n\n"
            "Find a SaaS tool with terrible UX and 2-star reviews. Build the same thing but better. "
            "Execution often matters more than originality.\n\n"
            "6. Follow Regulatory Changes\n\n"
            "New regulations create compliance needs. GDPR spawned dozens of successful privacy "
            "tools. Stay ahead of regulatory changes in your domain.\n\n"
            "7. Watch Adjacent Markets\n\n"
            "A solution that works in one industry often works in another. Construction project "
            "management and film production management have surprising overlap."
        ),
    },
    {
        "title": "Introducing the AI Product Planner",
        "tags": ["Updates", "Engineering"],
        "teaser": "Our new AI Product Planner helps you go from idea to spec in minutes, not weeks.",
        "body": (
            "Today we're thrilled to announce the AI Product Planner — our most ambitious feature "
            "yet. It takes a product idea and generates a complete specification document, including "
            "user stories, technical requirements, and a suggested architecture.\n\n"
            "How It Works\n\n"
            "Start by describing your product idea in plain English. The AI Product Planner asks "
            "clarifying questions, explores edge cases, and then generates a comprehensive spec.\n\n"
            "The output includes:\n"
            "- User personas and journey maps\n"
            "- Detailed user stories with acceptance criteria\n"
            "- Technical architecture recommendations\n"
            "- Database schema suggestions\n"
            "- API endpoint definitions\n"
            "- Estimated complexity and timeline\n\n"
            "Why We Built This\n\n"
            "We watched our users spend weeks going from idea to actionable spec. For solo founders "
            "and small teams, this planning phase is often where momentum dies. The AI Product "
            "Planner compresses weeks of planning into minutes of conversation.\n\n"
            "Early Access\n\n"
            "The AI Product Planner is available today in beta for all Pro plan subscribers. We'd "
            "love your feedback as we continue to refine the experience.\n\n"
            "Try it now from your dashboard under Tools > AI Product Planner."
        ),
    },
    {
        "title": "Why We Chose Python for Our Backend",
        "tags": ["Opinion", "Engineering"],
        "teaser": "In a world of Go, Rust, and Node, we chose Python — and we'd do it again. Here's why.",
        "body": (
            "When we started building AgenticEdge's backend in 2023, the obvious question was: what "
            "language? The decision wasn't as straightforward as you might think.\n\n"
            "We evaluated four serious contenders: Go, Rust, Node.js, and Python. Each had "
            "compelling strengths. Go's concurrency model is elegant. Rust's performance is "
            "unmatched. Node.js offers full-stack JavaScript. Python has... readability?\n\n"
            "Actually, Python has a lot more than readability. Here's what tipped the scales:\n\n"
            "Hiring Speed\n\n"
            "We needed to hire fast. Python has the largest pool of web developers, and most can "
            "be productive on day one. Our first three backend hires were writing production code "
            "within their first week.\n\n"
            "Library Ecosystem\n\n"
            "For our use case — data processing, API serving, and AI integration — Python's library "
            "ecosystem is unmatched. NumPy, pandas, scikit-learn, and the entire Hugging Face "
            "ecosystem are Python-native.\n\n"
            "Async Performance\n\n"
            "Modern Python with asyncio is fast enough. Our API endpoints respond in under 50ms "
            "on average. For the hot paths where Python is too slow, we write Rust extensions "
            "using PyO3.\n\n"
            "Developer Happiness\n\n"
            "This one is hard to measure but impossible to ignore. Our developers enjoy writing "
            "Python. They write tests voluntarily. They refactor proactively. Happy developers "
            "write better code.\n\n"
            "Would we choose differently today? No. Python continues to be the right choice for "
            "our team and our product."
        ),
    },
    {
        "title": "Company Update: Q1 2026 Roadmap",
        "tags": ["Company", "News"],
        "teaser": "A look at what the AgenticEdge team is building in Q1 2026 — from new integrations to performance improvements.",
        "body": (
            "Happy new year from the AgenticEdge team! We're kicking off 2026 with our most "
            "ambitious quarter yet. Here's what's on the roadmap.\n\n"
            "New Integrations\n\n"
            "We're adding native integrations with Linear, Notion, and Figma. These were the top "
            "three requests from our user survey, and we're committed to making AgenticEdge fit "
            "seamlessly into your existing workflow.\n\n"
            "Performance Overhaul\n\n"
            "Our engineering team is undertaking a major performance initiative. The goal: reduce "
            "average page load time from 1.2 seconds to under 400 milliseconds. This involves "
            "moving to edge computing for our API layer and implementing aggressive caching.\n\n"
            "Mobile App\n\n"
            "The most requested feature of all time is finally happening. We're building native "
            "iOS and Android apps using React Native. Beta testing starts in March.\n\n"
            "Team Growth\n\n"
            "We're growing from 15 to 25 people this quarter. We're hiring across engineering, "
            "design, and customer success. If you're interested, check our careers page.\n\n"
            "Community\n\n"
            "We're launching a community forum for AgenticEdge users to share templates, workflows, "
            "and feedback. The beta opens in February.\n\n"
            "Thank you for being part of the AgenticEdge journey. We couldn't build this without "
            "our amazing users and community."
        ),
    },
]


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

# Color palettes for gradient backgrounds
PALETTES = [
    ((44, 62, 80), (52, 152, 219)),      # Dark blue -> light blue
    ((142, 68, 173), (41, 128, 185)),     # Purple -> blue
    ((39, 174, 96), (22, 160, 133)),      # Green -> teal
    ((211, 84, 0), (243, 156, 18)),       # Orange -> yellow
    ((192, 57, 43), (231, 76, 60)),       # Dark red -> light red
    ((44, 62, 80), (197, 230, 54)),       # Dark -> lime green
]


def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def generate_gradient_image(filepath: Path, title: str, tag: str, palette_idx: int):
    """Generate an 800x500 gradient image with text overlay."""
    width, height = 800, 500
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    c1, c2 = PALETTES[palette_idx % len(PALETTES)]

    # Draw gradient
    for y in range(height):
        t = y / height
        color = lerp_color(c1, c2, t)
        draw.line([(0, y), (width, y)], fill=color)

    # Add some decorative circles
    random.seed(palette_idx)
    for _ in range(5):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        r = random.randint(30, 120)
        opacity_color = lerp_color(c1, c2, 0.5)
        lighter = tuple(min(255, c + 30) for c in opacity_color)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=lighter, outline=None)

    # Try to use a reasonable font, fall back to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except (OSError, IOError):
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 32)
            font_small = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 18)
        except (OSError, IOError):
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

    # Wrap title text
    max_chars = 30
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line = f"{current_line} {word}".strip()
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Draw text with shadow
    line_height = 42
    total_text_height = len(lines) * line_height + 30  # +30 for tag
    start_y = (height - total_text_height) // 2

    # Tag label
    draw.text((width // 2 - 50, start_y), tag.upper(), fill=(255, 255, 255, 180), font=font_small)
    start_y += 40

    for i, line in enumerate(lines):
        y = start_y + i * line_height
        # Shadow
        draw.text((width // 2 - 150 + 2, y + 2), line, fill=(0, 0, 0), font=font_large)
        # Text
        draw.text((width // 2 - 150, y), line, fill=(255, 255, 255), font=font_large)

    img.save(filepath, "JPEG", quality=85)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # Create admin user
    hashed, salt = hash_password("69Instagram69!")
    users = [
        {
            "username": "deoxyribo",
            "display_name": "DrFlask",
            "password": hashed,
            "salt": salt,
        }
    ]
    with open(DATA_DIR / "users.json", "w") as f:
        json.dump(users, f, indent=2)
    print("Created admin user (deoxyribo / 69Instagram69!)")

    # Create sample posts
    now = datetime.now(timezone.utc)
    posts = []
    for i, post_data in enumerate(POSTS):
        slug = slugify(post_data["title"])
        image_filename = f"{slug}.jpg"
        created = (now - timedelta(days=len(POSTS) - i)).isoformat()

        # Generate hero image
        generate_gradient_image(
            UPLOADS_DIR / image_filename,
            post_data["title"],
            post_data["tags"][0],
            i,
        )

        body = post_data["body"]
        word_count = len(body.split())

        post = {
            "title": post_data["title"],
            "slug": slug,
            "tags": post_data["tags"],
            "teaser": post_data["teaser"],
            "body": body,
            "image": image_filename,
            "youtube_url": "",
            "github_url": "",
            "huggingface_url": "",
            "twitter_url": "",
            "arxiv_url": "",
            "author": "DrFlask",
            "created": created,
            "updated": created,
            "read_time": max(1, round(word_count / 200)),
        }
        posts.append(post)
        print(f"  Created post: {post_data['title']}")

    with open(DATA_DIR / "posts.json", "w") as f:
        json.dump(posts, f, indent=2)

    print(f"\nGenerated {len(posts)} posts with hero images.")
    print(f"Data saved to {DATA_DIR}")
    print(f"Images saved to {UPLOADS_DIR}")
    print(f"\nStart the app with: python app.py --port 8001")


if __name__ == "__main__":
    main()
