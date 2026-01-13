from pip_setuptools import setup, clean, readme, requirements

clean()
setup(
    name='django-robots-and-sitemap',
    version='1.0.2',
    install_requires=requirements(),
    packages=['robots_and_sitemap'],
    description='A Django plugin that adds support for sitemap.xml and robots.txt',
    long_description=readme(),
    long_description_content_type="text/markdown",
    author='Маг Ильяс DOMA (MagIlyasDOMA)',
    author_email='magilyas.doma.09@list.ru',
    url='https://github.com/MagIlyasDOMA/django-robots-and-sitemap',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Django',
        'Framework :: Django :: 4',
        'Framework :: Django :: 5',
        'Framework :: Django :: 6',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14"
    ],
    python_requires='>=3.6',
)
