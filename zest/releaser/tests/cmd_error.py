# Python script to test some corner cases that print warnings to stderr.
import sys

print(sys.argv[1], file=sys.stderr)
