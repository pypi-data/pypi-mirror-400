import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="llwy",
	version="0.0.3",
	author="lhqvq",
	author_email="lhqvq@mail.ustc.edu.cn",
	description="init",
	long_description=long_description,
	url="https://github.com/",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)
