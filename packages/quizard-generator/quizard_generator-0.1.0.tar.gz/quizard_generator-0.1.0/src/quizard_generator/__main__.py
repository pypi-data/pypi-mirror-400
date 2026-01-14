"""
Enable running as: python -m quizard_generator

This allows both installed command and module execution:
    - quizard <command>                    (after pip install)
    - python -m quizard_generator <command>  (development)
"""

from quizard_generator.cli import main

if __name__ == "__main__":
    main()
