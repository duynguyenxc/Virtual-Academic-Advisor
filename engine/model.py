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