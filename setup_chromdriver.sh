#!/bin/bash
set -euo pipefail

# Get Chrome version (e.g., "114.0.5735")
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
# Get corresponding chromedriver version using the major version component
CHROMEDRIVER_VERSION=$(curl -sS "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION%%.*}")

# Download the chromedriver zip file
wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip
# Unzip and move the chromedriver binary to /usr/local/bin
unzip -qq /tmp/chromedriver.zip -d /tmp
mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver
# Cleanup temporary files
rm -rf /tmp/chromedriver*