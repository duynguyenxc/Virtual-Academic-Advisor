# engine/loader.py
# ------------------------------------------------------------
# Loader for JSON data (courses, degree requirements, plans, policies).
# Converts raw JSON into Python objects defined in engine/model.py.
# ------------------------------------------------------------

import sys
from pathlib import Path

# đảm bảo project root (một cấp trên thư mục engine) có trong sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import json
import re
from typing import Dict, List, Any, Optional

from engine.model import Course, Requirement, RequirementBlock

# ------------------------------------------------------------
# Path setup
# ------------------------------------------------------------
BASE = Path(__file__).resolve().parents[1] / "data" / "olemiss" / "bscs" / "2024-2025"

COURSE_FILES = [
    BASE / "csci_courses_full.json",
    BASE / "math_science_courses.json"
]

DEGREE_REQUIREMENTS_FILE = BASE / "degree_requirements.json"
FOUR_YEAR_PLAN_FILE = BASE / "four_year_plan.json"
POLICIES_FILE = BASE / "policies.json"

# ------------------------------------------------------------
# Loader helpers
# ------------------------------------------------------------

def load_json(path: Path) -> Any:
    """Load JSON file safely; return empty dict/list on missing or parse error."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

_course_code_re = re.compile(r'([A-Za-z]{2,4}\s*\d{3}[A-Za-z]?)', re.IGNORECASE)
_credits_re = re.compile(r'(\d+(?:\.\d+)?)(?:\s*-\s*\d+(?:\.\d+)?)?\s+credits?', re.IGNORECASE)
_numeric_re = re.compile(r'(\d+(?:\.\d+)?)')

def _extract_code(raw_code: Optional[str], title: Optional[str]) -> str:
    """Try code field first, otherwise extract from title (e.g. 'Csci 111: Name')."""
    if raw_code:
        return raw_code.strip().upper()
    if not title:
        return ""
    m = _course_code_re.search(title)
    return m.group(1).upper() if m else title.strip().upper()

def _extract_name(title: Optional[str]) -> str:
    """Return a cleaned course name (remove leading code if present)."""
    if not title:
        return ""
    # Remove leading code + optional colon
    return re.sub(r'^[A-Za-z]{2,4}\s*\d{3}[A-Za-z]?\s*[:\-–]\s*', '', title, flags=re.IGNORECASE).strip()

def _parse_credits(raw: Any) -> int:
    """Normalize credits to integer. Return 0 when unknown."""
    if raw is None:
        return 0
    if isinstance(raw, (int, float)):
        try:
            return int(float(raw))
        except Exception:
            return 0
    s = str(raw).strip()
    if not s:
        return 0
    # Look for patterns like "3 credits", "3-4 credits", "3.0 credits"
    m = _credits_re.search(s)
    if m:
        try:
            return int(float(m.group(1)))
        except Exception:
            pass
    # fallback: any first number
    m2 = _numeric_re.search(s)
    if m2:
        try:
            return int(float(m2.group(1)))
        except Exception:
            pass
    return 0

def _normalize_prereqs(raw: Any) -> List[str]:
    """Return prerequisites as list of strings (empty list if none)."""
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    s = str(raw).strip()
    # split common separators but keep phrase if it's a sentence
    parts = re.split(r'\s*;\s*|\s*\.\s*|\s*,\s*or\s*|\s*,\s*and\s*|\s*,\s*', s)
    parts = [p.strip() for p in parts if p.strip()]
    return parts if parts else [s]

# ------------------------------------------------------------
# Loader functions
# ------------------------------------------------------------

def load_courses() -> Dict[str, Course]:
    """
    Load courses from multiple JSON files and merge into a dictionary.
    Key = course code (e.g., 'CSCI 111'), Value = Course object.
    """
    courses: Dict[str, Course] = {}
    for file in COURSE_FILES:
        raw = load_json(file)
        if not raw:
            continue
        for c in raw:
            # Some sources use 'code', others include code in 'title' or 'name'
            raw_code = c.get("code")
            title_field = c.get("title") or c.get("name") or ""
            code = _extract_code(raw_code, title_field)
            if not code:
                continue

            name = c.get("name") or _extract_name(title_field) or title_field
            credits_val = _parse_credits(c.get("credits"))
            prereqs = _normalize_prereqs(c.get("prerequisites") or c.get("prereq") or c.get("prerequisite"))

            course = Course(
                code=code,
                name=name,
                credits=credits_val,
                description=c.get("description") or "",
                prerequisites=prereqs,
                semester_offered=c.get("semester_offered"),
                attributes=c.get("attributes") or []
            )
            courses[code] = course
    return courses

def load_degree_requirements() -> Dict[str, RequirementBlock]:
    """
    Load degree requirements from JSON and normalize to RequirementBlock objects.
    Returns a dict keyed by block name.
    """
    data = load_json(DEGREE_REQUIREMENTS_FILE) or {}
    blocks: Dict[str, RequirementBlock] = {}

    for block_name, block in (data.get("blocks") or {}).items():
        reqs: List[Requirement] = []
        for r in block.get("requirements", []):
            # safe parsing of credits
            try:
                cred = int(r.get("credits") or 0)
            except Exception:
                cred = 0
            reqs.append(
                Requirement(
                    name=r.get("name") or r.get("course") or "Unnamed",
                    credits=cred,
                    options=r.get("options"),
                    allowed_prefixes=r.get("allowed_prefixes"),
                    exclusions=r.get("exclusions"),
                    prerequisites=r.get("prerequisites"),
                    filter=r.get("filter"),
                    notes=r.get("notes"),
                )
            )
        blocks[block_name] = RequirementBlock(name=block_name, requirements=reqs)
    return blocks

def load_four_year_plan() -> dict:
    """Load the standard four-year advising plan (raw JSON dict)."""
    return load_json(FOUR_YEAR_PLAN_FILE) or {}

def load_policies() -> dict:
    """Load program policies (raw JSON dict)."""
    return load_json(POLICIES_FILE) or {}
# ...existing code...
