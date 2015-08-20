import setuptools

setuptools.setup(
    name="pubsub",
    version="0.1.0",
    url="https://github.com/mttr/pubsub",

    author="Matt Rasmus",
    author_email="mattr@zzntd.com",

    description="A simple PubSub server implementation in Python.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
