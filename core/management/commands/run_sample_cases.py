"""Validate the engine against a sample-cases JSON file.

Usage:
    python manage.py run_sample_cases --file SUST_Preli_Sample_Cases.json

The JSON file must contain a list of cases with the shape:

    [
      {
        "id": "case-01",
        "input": { ...payload... },
        "expected_output": { ...subset of fields... }
      },
      ...
    ]

For each case, the command POSTs the payload to ``engine.analyzer.analyze``
(direct call, not HTTP — so the test is deterministic) and compares the
returned dict against ``expected_output`` using the keys that exist in the
expected_output dict. Missing fields in expected_output are skipped.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from engine import analyzer
from engine.safety import detect_injection


class Command(BaseCommand):
    help = "Run the rule-based engine against a sample-cases JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="SUST_Preli_Sample_Cases.json",
            help="Path to the sample-cases JSON file (default: %(default)s).",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit with non-zero status if any case fails.",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.exists():
            raise CommandError(f"Sample cases file not found: {path}")

        try:
            cases = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON in {path}: {exc}")

        if not isinstance(cases, list):
            raise CommandError(f"{path} must contain a JSON array of cases.")

        total = len(cases)
        passed = 0
        failed = 0

        for idx, case in enumerate(cases, 1):
            case_id = case.get("id") or f"case-{idx}"
            payload = case.get("input") or {}
            expected = case.get("expected_output") or {}

            try:
                actual = analyzer.analyze(payload)
                # Mirror the public-API injection tagging so the test covers it.
                if detect_injection(payload.get("complaint", "")):
                    codes = actual.setdefault("reason_codes", [])
                    if "prompt_injection_attempt" not in codes:
                        codes.append("prompt_injection_attempt")
            except Exception as exc:
                self.stdout.write(self.style.ERROR(
                    f"[{case_id}] engine raised {type(exc).__name__}: {exc}"
                ))
                failed += 1
                continue

            mismatches = []
            for key, want in expected.items():
                got = actual.get(key)
                if want != got:
                    mismatches.append((key, want, got))

            if mismatches:
                failed += 1
                self.stdout.write(self.style.ERROR(f"[{case_id}] FAIL"))
                for key, want, got in mismatches:
                    self.stdout.write(
                        f"  - {key}: expected={want!r}  got={got!r}"
                    )
            else:
                passed += 1
                self.stdout.write(self.style.SUCCESS(f"[{case_id}] OK"))

        self.stdout.write("")
        self.stdout.write(f"Total: {total}   Passed: {passed}   Failed: {failed}")

        if failed and options["strict"]:
            sys.exit(1)