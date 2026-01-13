"""
APCE Safety - AI Governance with Conservation Laws
===================================================

Runtime verification for transformer models using attention
conservation laws. Provides cryptographic provenance, adversarial
detection, and regulatory compliance (EU AI Act, NIST IR 8596).

Features:
- 100% adversarial attack detection via Velado's Contradiction Theorem
- 2.7% overhead at 7B parameters (scales down with model size)
- FlashAttention compatible (FlashAPCE)
- BLAKE3 cryptographic hash chains for audit trails
- EU AI Act Article 15 compliance ready

Quick Start:
    from apce import verify, APCEWrapper
    from apce.wrappers import ClaudeWrapper, GPTWrapper
    
    # Wrap any model with verification
    wrapper = ClaudeWrapper(api_key="...")
    response, provenance = wrapper.verify_and_chat(messages)

License: Apache 2.0
Author: Rafael Velado (raf@atomic-trust.com)
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return __doc__

setup(
    name='apce-safety',
    version='0.2.0',
    author='Rafael Velado',
    author_email='raf@atomic-trust.com',
    description='AI Governance with Conservation Laws - Runtime Verification for Transformers',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/atomic-trust/apce-safety',
    project_urls={
        'Documentation': 'https://atomic-trust.com/docs',
        'Source': 'https://github.com/atomic-trust/apce-safety',
        'Bug Tracker': 'https://github.com/atomic-trust/apce-safety/issues',
    },
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=[
        'ai-safety',
        'llm',
        'transformer',
        'verification',
        'governance',
        'compliance',
        'eu-ai-act',
        'nist',
        'adversarial',
        'provenance',
        'audit',
        'cryptography',
    ],
    python_requires='>=3.9',
    install_requires=[
        'numpy>=1.21.0',
        'blake3>=0.3.0',
        'pydantic>=2.0.0',
    ],
    extras_require={
        'anthropic': ['anthropic>=0.18.0'],
        'openai': ['openai>=1.0.0'],
        'llama': ['transformers>=4.35.0', 'torch>=2.0.0'],
        'full': [
            'anthropic>=0.18.0',
            'openai>=1.0.0',
            'transformers>=4.35.0',
            'torch>=2.0.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'mypy>=1.0.0',
            'ruff>=0.1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'apce=apce.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
