# from setuptools import setup
# setup()
import os
import subprocess
import platform
import pathlib
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from distutils import log

def load_doc_file(readme_file_path: str) -> str:
    doc_str = ""
    with open(readme_file_path, "r", encoding="utf-8") as fh:
        doc_str = fh.read()
    return doc_str

def load_version(readme_file_path: str) -> str:
    ver_str = ""
    with open(readme_file_path, "r", encoding="utf-8") as fh:
        ver_str = fh.read()
    _, version = ver_str.split("=")
    version = version.replace('"', "").replace(" ", "")
    return version

def get_path_to_help_file(help_file_path:str) -> str:
    file_path = pathlib.Path(help_file_path).resolve()
    return file_path

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

def is_headless():
    """Detects if the system likely has no GUI."""
    if platform.system() == "Linux":
        return not any(k in os.environ for k in ("DISPLAY", "WAYLAND_DISPLAY"))
    elif platform.system() == "Windows":
        # crude heuristic: no desktop session
        return os.environ.get("SESSIONNAME") in (None, "Services")
    elif platform.system() == "Darwin":
        return False
    return True

has_graphic_output = not is_headless()
print(f"Detected graphic = {has_graphic_output}")

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        print("*******************************************************")
        print("*    Nanosurf package development installation done   *")
        print("*******************************************************")
        if platform.system() == "Windows":
            abs_help_file_path = get_path_to_help_file("nanosurf/doc/README.md")
            subprocess.run(rf'{abs_help_file_path}', shell=True)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        print("*******************************************************")
        print("*    Nanosurf package standard installation done      *")
        print("*******************************************************")
        if platform.system() == "Windows": 
            abs_help_file_path = get_path_to_help_file("nanosurf/doc/Nanosurf_Python_Library_Overview.pdf")
            subprocess.run(rf'{abs_help_file_path}', shell=True)

package_data_files = []
package_data_files += package_files('nanosurf/app')
package_data_files += package_files('nanosurf/doc')
package_data_files += package_files('nanosurf_internal/app')
package_data_files += package_files('nanosurf_internal/doc')
if has_graphic_output:
    package_data_files += package_files('nanosurf/lib/frameworks/qt_app')

long_description_file = load_doc_file('nanosurf/doc/README.md')

# Base dependencies (always required)
install_requires_packages = [
    "numpy",
    "scipy",
    "h5py>=3.11",
    "psutil",
    "debugpy",
    "pywin32>=311; platform_system=='Windows'",
    "lupa>=2.6; platform_system=='Windows'",
    "smbus3; platform_system=='Linux'",
]

# GUI-related dependencies only if not headless
if has_graphic_output:
    install_requires_packages += [
        "matplotlib",
        "notebook",
        "pyside6>=6.10",
        "pyqtgraph>=0.14",
    ]
else:
    print("Skipping GUI-related dependencies (headless environment detected).")

setup(
    name='nanosurf',
    version=load_version('nanosurf/_version.py'),
    author='Nanosurf AG',
    author_email='scripting@nanosurf.com',
    description='Python API for Nanosurf controllers and Nanosurf style application framework',
    long_description=long_description_file,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(
        include=['*'],
    ),
    package_data={'': package_data_files},
    include_package_data = False,
    zip_safe=False,
    install_requires=install_requires_packages,
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        "License :: OSI Approved :: MIT License"
    ],
    entry_points={
        'console_scripts': [
            'nanosurf_help = nanosurf:help',
        ],
        'pyinstaller40': [
            'hook-dirs = nanosurf:get_py_installer_hook_dirs'
        ]
    },
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },    
    python_requires='>=3.10, <3.15'
)

