import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engine.model import StudentProfile
from engine.loader import load_courses, load_degree_requirements, load_policies
from engine.audit import audit_student

def test_integration():
    # 1. Load data
    courses = load_courses()
    degree_reqs = load_degree_requirements()
    policies = load_policies()

    print("=== DATA LOADED ===")
    print(f"Total courses: {len(courses)}")
    print(f"Requirement blocks: {list(degree_reqs.keys())}")
    print(f"Policies: {list(policies['policies'].keys())}")

    # 2. Example student profile
    profile = StudentProfile(
        catalog_year="2024-2025",
        courses_done=["CSCI 111", "MATH 261"]  # freshman student
    )

    # 3. Run audit
    result = audit_student(profile)

    print("\n=== AUDIT RESULT ===")
    print(f"Credits done: {result['credits_done']} / {result['credits_required']}")
    for block, status in result["blocks"].items():
        print(f"- {block}: {status['credits_done']} / {status['credits_required']} credits")
        print(f"  Completed: {status['completed']}")
        print(f"  Missing: {status['missing'][:3]} ...")  # show first few only
