from setuptools import find_namespace_packages, setup

setup(
    name='brynq_sdk_alight',
    version='1.0.0.dev0',
    description='Alight SDK for the BrynQ.com platform',
    long_description='Alight SDK for the BrynQ.com platform',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'requests>=2,<=3',
        'xsdata>=25.0.0',
        'pydantic>=2.0.0',
        'pydantic-xml>=2.0.0',
        'xsdata-pydantic>=24.0.0'
    ],
    zip_safe=False,
)
