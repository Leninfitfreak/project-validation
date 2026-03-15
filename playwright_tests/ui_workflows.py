import site
import sys

usersite = site.getusersitepackages()
if usersite not in sys.path:
    sys.path.append(usersite)

from validator_engine.playwright_runner import run_playwright_evidence

if __name__ == '__main__':
    run_playwright_evidence()
