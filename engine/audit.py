# engine/audit.py
# ------------------------------------------------------------
# Auditing logic for student progress against BSCS degree requirements.
# ------------------------------------------------------------

from typing import Dict, List, Any
from engine.model import StudentProfile, RequirementBlock
from engine.loader import load_courses, load_degree_requirements, load_policies

def audit_student(profile: StudentProfile) -> Dict[str, Any]:
    """
    Audit a student's progress toward BSCS degree requirements.
    Returns a dict summarizing completed/missing requirements.
    """
    courses = load_courses()
    degree_blocks = load_degree_requirements()
    policies = load_policies().get("policies", {})

    completed = set(c.upper() for c in profile.courses_done)
    total_credits = 0
    block_results = {}

    # count credits of completed courses
    for code in completed:
        if code in courses:
            total_credits += courses[code].credits

    # check each requirement block
    for block_name, block in degree_blocks.items():
        block_status = {
            "completed": [],
            "missing": [],
            "credits_required": sum(r.credits for r in block.requirements),
            "credits_done": 0
        }

        for req in block.requirements:
            satisfied = False

            # Case 1: explicit course options
            if req.options and any(opt.upper() in completed for opt in req.options):
                satisfied = True
                block_status["completed"].append(req.name)

            # Case 2: requirement name matches a completed course
            elif any(req.name.upper() == code for code in completed):
                satisfied = True
                block_status["completed"].append(req.name)

            # Case 3: allowed_prefixes match
            elif req.allowed_prefixes:
                match = [c for c in completed if any(c.startswith(p) for p in req.allowed_prefixes)]
                if match:
                    satisfied = True
                    block_status["completed"].append(f"{req.name} ({match[0]})")

            # Mark missing if not satisfied
            if not satisfied:
                block_status["missing"].append(req.name)

            # Credit counting
            if satisfied:
                block_status["credits_done"] += req.credits

        block_results[block_name] = block_status

    # overall result
    return {
        "catalog_year": profile.catalog_year,
        "credits_done": total_credits,
        "credits_required": policies.get("min_total_credits", 127),
        "blocks": block_results
    }
