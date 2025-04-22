"""Compares extracted data with checklist.json to flag missing answers."""
import json, pathlib

CHECKLIST = json.loads(pathlib.Path("checklist.json").read_text())

def find_gaps(responses: dict) -> list[str]:
    unanswered = []
    for section in CHECKLIST["sections"]:
        for q in section["questions"]:
            if q not in responses:
                unanswered.append(q)
    return unanswered
