import setuptools

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="perl_binary_packing",
    version="0.1.0",
    author="Mikhail Belov (mishka251)",
    author_email="mishkabelka251@gmail.com",
    description="Binary pack/unpack with perl-style format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["perl_binary_packing"],
)
