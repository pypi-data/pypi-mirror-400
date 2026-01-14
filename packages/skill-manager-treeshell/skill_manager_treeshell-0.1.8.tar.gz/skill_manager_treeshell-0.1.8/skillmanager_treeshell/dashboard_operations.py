"""Dashboard operations - favorites, recents, issues for skill-manager."""
import json
import os
from datetime import datetime
from pathlib import Path

DASHBOARD_FILE = Path(os.environ.get("HEAVEN_DATA_DIR", "/tmp/heaven_data")) / "skill_dashboard.json"

def _load_dashboard():
    if DASHBOARD_FILE.exists():
        return json.loads(DASHBOARD_FILE.read_text())
    return {"favorite_skills": {}, "favorite_personas": [], "recently_made": [], "recently_equipped": [], "issues": []}

def _save_dashboard(data):
    DASHBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_FILE.write_text(json.dumps(data, indent=2))

# === FAVORITE SKILLS ===
def _dashboard_fav_skills_list() -> str:
    data = _load_dashboard()
    favs = data.get("favorite_skills", {})
    if not favs:
        return "No favorite skills yet. Use fav_skills_add to add some."
    result = "=== Favorite Skills ===\n"
    for cat, skills in favs.items():
        result += f"\n[{cat}]\n"
        for s in skills:
            result += f"  - {s}\n"
    return result

def _dashboard_fav_skills_add(skill_name: str, category: str = "general") -> str:
    data = _load_dashboard()
    if category not in data["favorite_skills"]:
        data["favorite_skills"][category] = []
    if skill_name not in data["favorite_skills"][category]:
        data["favorite_skills"][category].append(skill_name)
        _save_dashboard(data)
        return f"Added '{skill_name}' to favorites under '{category}'"
    return f"'{skill_name}' already in favorites"

def _dashboard_fav_skills_remove(skill_name: str) -> str:
    data = _load_dashboard()
    for cat, skills in data["favorite_skills"].items():
        if skill_name in skills:
            skills.remove(skill_name)
            _save_dashboard(data)
            return f"Removed '{skill_name}' from favorites"
    return f"'{skill_name}' not found in favorites"

# === FAVORITE PERSONAS ===
def _dashboard_fav_personas_list() -> str:
    data = _load_dashboard()
    favs = data.get("favorite_personas", [])
    if not favs:
        return "No favorite personas yet."
    return "=== Favorite Personas ===\n" + "\n".join(f"  - {p}" for p in favs)

def _dashboard_fav_personas_add(persona_name: str) -> str:
    data = _load_dashboard()
    if persona_name not in data["favorite_personas"]:
        data["favorite_personas"].append(persona_name)
        _save_dashboard(data)
        return f"Added '{persona_name}' to favorite personas"
    return f"'{persona_name}' already in favorites"

def _dashboard_fav_personas_remove(persona_name: str) -> str:
    data = _load_dashboard()
    if persona_name in data["favorite_personas"]:
        data["favorite_personas"].remove(persona_name)
        _save_dashboard(data)
        return f"Removed '{persona_name}' from favorites"
    return f"'{persona_name}' not found"

# === RECENTS ===
def _dashboard_recently_made(limit: int = 10) -> str:
    data = _load_dashboard()
    recents = data.get("recently_made", [])[-limit:]
    if not recents:
        return "No recently made skills tracked."
    return "=== Recently Made ===\n" + "\n".join(f"  - {r['name']} ({r['time']})" for r in recents)

def _dashboard_recently_equipped(limit: int = 10) -> str:
    data = _load_dashboard()
    recents = data.get("recently_equipped", [])[-limit:]
    if not recents:
        return "No recently equipped items tracked."
    return "=== Recently Equipped ===\n" + "\n".join(f"  - {r['name']} ({r['time']})" for r in recents)

def track_made(skill_name: str):
    data = _load_dashboard()
    data["recently_made"].append({"name": skill_name, "time": datetime.now().isoformat()})
    data["recently_made"] = data["recently_made"][-50:]
    _save_dashboard(data)

def track_equipped(name: str):
    data = _load_dashboard()
    data["recently_equipped"].append({"name": name, "time": datetime.now().isoformat()})
    data["recently_equipped"] = data["recently_equipped"][-50:]
    _save_dashboard(data)

# === ISSUES ===
def _dashboard_create_issue(title: str, body: str, tags: str = "") -> str:
    data = _load_dashboard()
    issue = {"id": f"issue_{len(data['issues'])+1}", "title": title, "body": body, "tags": tags.split(",") if tags else [], "created": datetime.now().isoformat()}
    data["issues"].append(issue)
    _save_dashboard(data)
    return f"Created issue: {issue['id']} - {title}"

def _dashboard_review_issues(issue_id: str = "") -> str:
    data = _load_dashboard()
    issues = data.get("issues", [])
    if not issues:
        return "No issues."
    if not issue_id:
        return "=== Issues ===\n" + "\n".join(f"[{i['id']}] {i['title']} ({i['created'][:10]})" for i in issues)
    for i in issues:
        if i["id"] == issue_id:
            return f"=== {i['title']} ===\nID: {i['id']}\nTags: {', '.join(i['tags'])}\nCreated: {i['created']}\n\n{i['body']}"
    return f"Issue '{issue_id}' not found"
