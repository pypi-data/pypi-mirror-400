"""
Zather evaluation framework (internal testing only).

This package is NOT part of the public zather distribution.
It's used for local development and testing of the zather CLI.

Setup:
    pip install weave anthropic

Run quick eval (Path Pack quality only):
    cd zather/
    python -m eval.evaluation --quick --sessions-dir eval/sessions

Run full eval (runs agent, compares trajectories - expensive!):
    python -m eval.evaluation --run-agent --sessions-dir eval/sessions
"""
