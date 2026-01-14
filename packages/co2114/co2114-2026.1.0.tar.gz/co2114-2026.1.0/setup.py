from setuptools import setup

setup(
    name="co2114",
    version="2026.1.0",
    description="codebase for co2114",
    author="wil ward",
    python_requires=">=3.12",
    packages=[
        "co2114",
        "co2114.agent", 
        "co2114.search", 
        "co2114.optimisation",
        "co2114.constraints", 
        "co2114.constraints.csp",
        "co2114.reasoning",
        "co2114.util"],
    install_requires=[
        'pygame>=2.6', 
        'numpy', 
        'ipython',
        'matplotlib',
        'jupyter',
        'scikit-learn',
        'seaborn'
        ]
)
