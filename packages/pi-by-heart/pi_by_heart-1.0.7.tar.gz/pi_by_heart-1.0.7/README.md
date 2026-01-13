
<h1 align="center">Learn π by ♥</h1>
<div align="center" id="logo">
    <img src="./assets/pi.jpeg" width="200", height="200">
</div>

<p align="center">
    <a href="https://github.com/menisadi/pi-by-heart/pulse">
      <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/menisadi/pi-by-heart">
    </a>
    <a href="https://github.com/menisadi/pi-by-heart/actions/workflows/ci.yml">
      <img alt="CI" src="https://github.com/menisadi/pi-by-heart/actions/workflows/ci.yml/badge.svg">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0">
        <img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg">
    </a>
</p>

A little memory game for Pi-Day.

## Python support
Compatible with Python 3.10, 3.11, 3.12, and 3.13.

## Usage
### Using pip
Install it using pip:
```bash
pip install pi-by-heart
```
Then run
```bash
pi-by-heart
```
and follow the instructions.

### Using uv
Install it using uv:
```bash
uv tool install pi-by-heart
```
Then run
```bash
pi-by-heart
```
and follow the instructions.

One-off run without installing:
```bash
uvx pi-by-heart
```

### From source
Fork the repository:
```bash
git clone https://github.com/menisadi/pi-by-heart.git
cd pi-by-heart
```
You may need to install the following:
```bash
pip install pyfiglet mpmath
```
After installing simply run
```bash
python ./src/pi.py
```
and follow the instructions.
