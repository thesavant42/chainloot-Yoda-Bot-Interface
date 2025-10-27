#!/usr/bin/env python3
import anybadge

# Generate a simple badge
badge = anybadge.Badge('Test', '1.0', default_color='green')

# Save to file
with open('test_badge.svg', 'w') as f:
    f.write(str(badge))

print("SVG generated: test_badge.svg")