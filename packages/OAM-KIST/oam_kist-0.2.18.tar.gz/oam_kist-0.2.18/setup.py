from setuptools import setup, find_packages
from pathlib import Path
import os


def get_version():
    init_path = os.path.join(os.path.dirname(__file__), "OAM_KIST", "__init__.py")
    with open(init_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise RuntimeError("패키지 버전 정보를 찾을 수 없습니다.")


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="OAM_KIST",
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
        "opencv-python"
    ],
    author="Youngjun Kim",
    author_email="kyjun0915@kist.re.kr",
    description="Quantum information and technology using OAM states and SLM for KIST research",
    long_description=long_description,
    long_description_content_type='text/markdown',
    project_urls={
        "Documentation": "https://yjun0915.github.io/OAM_KIST/",
        "Source": "https://github.com/yjun0915/OAM_KIST",
    },
    python_requires=">=3.7",
)