from setuptools import find_packages, setup

setup(
    name='yandex-backend',
    version='1.0.0',
    package_dir='yandex_backend',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-restful',
        'flask-sqlalchemy',
    ],
)
