from engine.model import Course, PlanRow, PlanTerm, PlanResult

# Fake test
c1 = Course(code="CSCI 111", name="Computer Science I", credits=3)
row1 = PlanRow(course="CSCI 111", hours=3)
term1 = PlanTerm(name="Fall 2025", rows=[row1])

plan = PlanResult(
    catalog_year="2024-2025",
    remaining_terms=8,
    terms=[term1],
    audit={"credits_done": 0, "missing_blocks": ["Math"]}
)

print(plan)
print("Total hours this term:", term1.total_hours)
