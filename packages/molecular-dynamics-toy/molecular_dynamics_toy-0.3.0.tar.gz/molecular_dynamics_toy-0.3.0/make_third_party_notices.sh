#!/bin/zsh
# Make sure you're in an environment with molecular_dynamics_toy
pip-licenses --with-notice-file --with-license-file --output-file ThirdPartyNotices.html --format html --no-license-path --no-version --packages $(cat bundled_packages.txt)
