import site
import sys

usersite = site.getusersitepackages()
if usersite not in sys.path:
    sys.path.append(usersite)

from validator_engine.engine import main

if __name__ == '__main__':
    raise SystemExit(main())
