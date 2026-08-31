# Contributing

A useful change makes a skill safer, clearer, more falsifiable, or measurably easier to use. Include
the failure mode, evidence, smallest coherent change, routing cases when applicable, focused tests,
and residual risk.

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_skills.py
python scripts/validate_catalog.py
python -m unittest discover -s tests -p "test_*.py"
python -m unittest discover -s skills/steward-brownfield/tests -p "test_*.py"
```

Do not add project-specific rules to a generic skill. Put them in repository instructions or a
repository-scoped companion skill.
