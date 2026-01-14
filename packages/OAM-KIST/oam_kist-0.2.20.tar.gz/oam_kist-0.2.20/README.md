<div align="center">
  <img src="https://raw.githubusercontent.com/yjun0915/OAM_KIST/main/assets/logo.png" alt="KIST OAM Logo" width="300">
  <br>
</div>

![Python](https://img.shields.io/badge/python-3670A0?&logo=python&logoColor=ffdd54)
![PyCharm](https://img.shields.io/badge/pycharm-143?&logo=pycharm&logoColor=black&color=black&labelColor=green)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?&logo=numpy&logoColor=white)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?&logo=opencv&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?&logo=scipy&logoColor=white)  
![KIST](https://img.shields.io/badge/KIST-Research-e44126?labelColor=6d6e67)
![UST](https://img.shields.io/badge/UST-shcool-ef4126?labelColor=4d4d4f)
![Quantum Optics](https://img.shields.io/badge/⚛️-QuantumOptics-9827AC?labelColor=black)
![OAM](https://img.shields.io/badge/🌀-OAM-black?labelColor=00C853)

[![Python Test](https://github.com/yjun0915/OAM_KIST/actions/workflows/test.yml/badge.svg)](https://github.com/yjun0915/OAM_KIST/actions/workflows/test.yml)
[![PyPI Version](https://img.shields.io/pypi/v/OAM_KIST)](https://pypi.org/project/OAM_KIST/)

Imaging and sequence toolkit for Lageurre-Gaussian mode light, i.e. Orbital Angular Montum(OAM) state.  


```bash
.
├── OAM_KIST/                # Main Source Code
│   ├── __init__.py          # Package initialization
│   ├── holography.py        # Core logic for hologram generation
│   ├── utils.py             # Helper functions (math, interpolation)
│   └── outputs/             # Directory for generated images
├── docs/                    # Documentation (Sphinx)
│   ├── source/              # Documentation source files (.rst, conf.py)
│   ├── Makefile             # Build command for Mac/Linux
│   └── make.bat             # Build command for Windows
├── tests/                   # Unit Tests
│   └── test_core.py         # Pytest test cases
├── main.py                  # Execution script
├── README.md                # Project overview
├── requirements.txt         # Dependencies
└── setup.py                 # PyPI distribution setup
```