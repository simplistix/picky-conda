#!/usr/bin/env python
import sys

sys.stdout.write(
    '-e git+https://github.com/Simplistix/picky.git'
    '@181903dc9a100ead5879ebc0ed81d12145be68d9#egg=picky-master\n'
)

sys.exit(0)