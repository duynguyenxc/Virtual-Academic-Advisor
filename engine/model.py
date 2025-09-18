# engine/model.py
# Dataclasses for the Virtual Academic Advisor (Ole Miss BSCS)
# ------------------------------------------------------------
# This file defines the core data models used by the advising engine:
#   - Course information from the catalog
#   - Degree requirements (blocks and rules)
#   - Student profile (input)
#   - Plan rows, terms, and results (output)
#
# These dataclasses act as a "contract" between the loader, scheduler,
# auditor, and API layers. Keeping them clear and consistent ensures
# the rest of the system can evolve without breaking.

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal

# Course & Catalog

@dataclass
class Course:
    """
    Represents a single course as listed in the catalog.
    """
    code: str                                #e.g., "CSCI 111"
    name: str                                #e.g., "Computer Science I"
    credits: int                             #credit hours
    description: Optional[str] = None        #course description(may be long text)
    prerequisites: List[str] = field(default_factory=list)  #list of prerequisite course codes
    semester_offered: Optional[List[Literal["Fall","Spring","Summer"]]] = None
    attributes: List[str] = field(default_factory=list)     #tags like "Lab Science", "Elective"

# Degree Requirement Blocks

@dataclass
class Requirement:
    """
    Represents one specific requirement inside a requirement block.
    Examples:
        - "First-Year Writing I" (3 credits, choose WRIT 100 or WRIT 101)
        - "Fine Arts" (3 credits, choose from AH/MUS/DANC/THEA/LIBA prefixes)
        - "CSCI 487" (3 credits, prereq: >= 6 credits of CSCI 300+)
    """
    name: str
    credits: int
    options: Optional[List[str]] = None               #explicit course options
    allowed_prefixes: Optional[List[str]] = None        #e.g., ["MUS","THEA"]
    exclusions: Optional[List[str]] = None              #strings to exclude (e.g., "studio")
    prerequisites: Optional[List[str]] = None           #prereq course codes
    filter: Optional[Dict] = None                     #e.g., {"prefix":"CSCI","min_level":300}
    notes: Optional[str] = None                       #free-form note for human/LLM

@dataclass
class RequirementBlock:
    """
    A group of related requirements, such as:
        - General Education
        - Math
        - Science
        - CSCI Core
    """
    name: str
    requirements: List[Requirement]

# Student Profile (input)

@dataclass
class StudentProfile:
    """
    Represents the student input for generating an academic plan.
    This will typically be provided by the API (from chat input or UI).
    """
    catalog_year: str
    courses_done: List[str] = field(default_factory=list)  #courses already completed
    remaining_terms: int = 8               #how many terms left (default = 4 years)
    target_hours: int = 16           # preferred average load per term
    max_hours: int = 19        #maximum hours allowed per term
    gpa: Optional[float] = None            #current GPA, for overload checks
    emphasis: Optional[str] = None    #"data_science", "computer_security", or None

# Plan Output(engine -> API)

@dataclass
class PlanRow:
    """
    One row inside a term's plan (i.e., one course recommendation).
    """
    course: str
    hours: int
    prereq: List[str] = field(default_factory=list)    #prerequisites for this course
    notes: List[str] = field(default_factory=list)     #advisory notes (e.g., "Fall only")
    prereq_met: Optional[bool] = None    #computed by prereq checker

@dataclass
class PlanTerm:
    """
    Represents a single academic term (Fall/Spring/Summer).
    """
    name: str
    rows: List[PlanRow]

    @property
    def total_hours(self) -> int:
        """Compute total credit hours scheduled in this term."""
        return sum(r.hours for r in self.rows)

@dataclass
class PlanResult:
    """
    Final output of the planner, to be returned by the API.
    """
    catalog_year: str
    remaining_terms: int
    terms: List[PlanTerm] #full plan (remaining terms only)
    audit: Dict  #audit summary (credits completed, missing blocks, warnings)
