# pyapptest

**pyapptest** is a lightweight Python package designed to manage your testing libraries for web applications.  
It allows easy **installation, uninstallation, and selection** of testing libraries like **FastAPI** and **Flask**.  

By default, installing `pyapptest` will install both `fastapptest` and `flaskapptest` automatically.

---

## **Installation**

```bash
pip install pyapptest


Usage
Install libraries individually
# Install only fastapptest
pyapptest install --lib fastapptest

# Install only flaskapptest
pyapptest install --lib flaskapptest

Uninstall libraries individually
# Uninstall fastapptest
pyapptest uninstall --lib fastapptest

# Uninstall flaskapptest
pyapptest uninstall --lib flaskapptest

Select active testing library
pyapptest options


Example output:

Select which testing library to use:
1. fastapptest
2. flaskapptest
Enter number: 1
Active testing library set to fastapptest


The selected library will be used as the active testing library for your projects.

You can always switch libraries by running pyapptest options again.

Notes

For detailed commands and usage of each library, please check their respective documentation:

fastapptest commands

flaskapptest commands

pyapptest does not modify or replace the CLI commands of the sub-libraries.