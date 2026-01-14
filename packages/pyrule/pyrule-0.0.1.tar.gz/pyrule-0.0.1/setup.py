LIBRARY = "pyrule"
VERSION = "0.0.1"

AUTHOR = "lqxnjk"
AUTHOR_EMAIL = "lqxnjk@qq.com"
DESCRIPTION = "A Python package for intelligent information bagging system"
LICENSE = "MIT"
PYTHON_REQUIRES = ">=3.7"
URL = f"https://github.com/lqxnjk/{LIBRARY}"

PROJECT_URLS = {
    'Bug Reports': f'{URL}/issues',
    'Source': URL,
    }

# Package discovery
PACKAGE_EXCLUDES = ['tests*', 'docs*', 'examples*']

# Classifiers
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3.7",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries",
    "Topic :: Scientific/Engineering",
    ]

# Keywords
KEYWORDS = ["rule", "tool", "data"]

# Package data
PACKAGE_DATA = {
    LIBRARY: ['data/*.json', 'data/*.csv'],
    }

# 定义命令行工具
ENTRY_POINTS = {
    'console_scripts': [  # 命令行工具,用户安装后可以在终端运行的命令
        f'{LIBRARY}_version = {LIBRARY}.__init__:version',
        ],
    'gui_scripts': [  # 让你的 Python 代码可以被其他工具（如桌面应用、IDE）动态调用
        # "my-gui-app = my_package.gui:run_app", # 命令名 = 模块名:函数名
        ],
    "flask.blueprints": [  # Flask 蓝图（扩展）
        # "my_bp = my_package.blueprint",  # 插件名 = 模块名
        ],
    "pytest11": [  # pytest 的插件入口点
        # "my_plugin = my_package.plugin",  # 插件名 = 模块名
        ],
    }

EXTRAS_REQUIRE = {
    ':python_version < "3.8"': ['typing-extensions'],
    'dev': [
        # 'pytest>=6.0',
        # 'pytest-cov>=2.0',
        # 'flake8>=3.9',
        # 'mypy>=0.910',
        # 'sphinx>=4.0',
        ],
    'plot': [
        # 'matplotlib>=3.0',
        # 'seaborn>=0.11',
        ],
    'gpu': [
        # 'cupy>=10.0'
        ],
    'full': [f'{LIBRARY}[dev]', f'{LIBRARY}[plot]', f'{LIBRARY}[gpu]']
    }


def readme_text():
    """Read README.md content as long description."""
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


def requirements_list():
    """Read requirements from requirements.txt."""
    import pathlib
    with open(pathlib.Path(__file__).absolute().parent / 'requirements.txt', 'r', encoding='utf-8') as f:
        return [
            line.strip() for line in f
            if line.strip()
               and not line.startswith('#')
               and not line.startswith('--')
            ]


# ========== Setup Configuration ==========
import setuptools

setuptools.setup(
    name=LIBRARY,
    version=VERSION,
    packages=setuptools.find_packages(exclude=PACKAGE_EXCLUDES),
    install_requires=requirements_list(),
    extras_require=EXTRAS_REQUIRE,
    include_package_data=True,
    package_data=PACKAGE_DATA,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=readme_text(),
    long_description_content_type='text/markdown',
    url=URL,
    project_urls=PROJECT_URLS,
    classifiers=CLASSIFIERS,
    python_requires=PYTHON_REQUIRES,
    entry_points=ENTRY_POINTS,
    license=LICENSE,
    keywords=KEYWORDS,
    )
