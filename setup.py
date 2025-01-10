import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="diagramAuditTest",  # The package name as it will appear on PyPI
    version="0.1.0",
    author="M S",
    author_email="ms@test.com",
    description="Tool for generating and auditing Python/PHP code diagrams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/diagram-code-auditor",  # or your project repo
    packages=setuptools.find_packages(),
    # ^ This tells setuptools to automatically find packages inside 'diagram_code_auditor', etc.
    python_requires=">=3.7",
    install_requires=[
        # List your Python dependencies here, for example:
        "diagrams"
        # "diagram_code_auditor"
    ],
    entry_points={
        "console_scripts": [
            # Provide command-line scripts that point to your existing "main" functions
            # The left side of = is the command name, the right side is the path to your function
            "diagram-create=diagramAudit.diagram_creator:main",
            "diagram-audit=diagramAudit.diagram_code_auditor:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
