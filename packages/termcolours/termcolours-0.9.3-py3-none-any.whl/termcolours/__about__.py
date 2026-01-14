
__version__ = "0.9.3"

# "0.9.3"  # 26-01-05 -- name change → termcolours
# "0.15.4-dev"  # 26-01-04 -- new features (to be implemented):
#                        - buffer deque + method `_emit` -- collecting output → possibility
#                          to print to save as a file
#                          - buffer: shows (prints) current buffer
#                          - clear: clears the buffer
#                          - drop/take: removes last/first row from the buffer
#                          - dump: saves the buffer to a file
#                        - better indicators for a palette: for 0 rows, 1, 2 or more
# "0.10.2-dev"  # 26-01-03 -- new features:
#                      - color positional argument (in decm format, e.g. "50;100;150;decm")
#                      - --raw flat: output without ANSI codes
#                      - new env. variable: OUTPUT
# "0.9.2"  # 26-01-03 -- refactored for integration tests:
#                      - pytest MUST expect SystemExit; otherwise
#                        the test will fail. Now `quit()` returns `__QUIT__`,
#                        which is passed in `num_to_ansi()` to `main()`,
#                        which returns 0 → test passes
# "0.9.1"  # 26-01-01 -- printing colours in batch-file mode debugged,
#                     -- added vertical lines for palette
#                     -- APPNAME and ROOTPATH moved do __init__.py
# "0.9.0"  # 25-12-31 -- palette
# "0.8.5"
