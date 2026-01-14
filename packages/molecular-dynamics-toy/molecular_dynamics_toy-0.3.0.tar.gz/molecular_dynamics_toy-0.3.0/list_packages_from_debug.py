#!/usr/bin/env python3
"""
Parses the output HTML file produced using
`pyintaller --log-level DEBUG MDToy.spec`,
in `build/MDToy/xref-MDToy.html`,
to determine which python packages were actually bundled
into the app.

Mostly for copyright purposes.
"""

import os.path

from bs4 import BeautifulSoup

LOGFILE = os.path.join('build', 'MDToy', 'xref-MDToy.html')

if __name__ == "__main__":
    # Load the data file
    with open(LOGFILE, 'r') as f:
        soup = BeautifulSoup(f, "html.parser")
    # Compile the imported classes
    imported_packages = set()
    for node in soup.find_all('div', class_='node'):
        # Check if this is a Package.
        if node.find('span', class_='moduletype').string == 'Package':
            # Keep only the root level package name.
            imported_packages.add(node.next.next['name'].split('.')[0])
    # Output
    with open('bundled_packages.txt', 'w') as f:
        for package in sorted(imported_packages):
            f.write(package)
            f.write('\n')

