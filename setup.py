from setuptools import setup, find_packages
from tb_lattice_viewer import __version__


setup(
    name="tb_lattice_viewer",
    version=__version__,
    description="Tight binding lattice viewer and to fortran code generator",
    url="https://github.com/kmkolasinski/tb-lattice-viewer",
    author="Krzysztof Kolasinski (2020)",
    author_email="kmkolasinski@gmail.com",
    license="",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # QT Related
        "PyQt5==5.15.2",
        "PyQt3D==5.15.2",
        "PyOpenGL==3.1.5",
        "QScintilla==2.11.6",
        # Not QT related packaged
        "PyYAML==5.3.1",
        "numpy==1.19.4",
        "cached-property==1.5.2",
        "tqdm==4.54.1",
        "natsort==7.1.0",
    ],
    scripts=[
        "scripts/lattice-viewer",
    ],
)
