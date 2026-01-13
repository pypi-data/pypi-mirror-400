from setuptools import setup, find_packages

setup(
    name="NFCL",                    # pip 설치 이름
    version="0.1.0",                # 버전 (업데이트할 때마다 올려야 함)
    description="New Fantastic Comsigan Loader - Korean School Timetable Scraper",
    author="YourName",              # 본인 이름이나 닉네임
    packages=find_packages(),
    install_requires=[              # 의존성 라이브러리 자동 설치
        "selenium",
        "webdriver-manager"
    ],
    python_requires='>=3.6',
)