
from setuptools import setup

with open("README.rst", "r", encoding="utf-8") as hoja:
    long_description = hoja.read()

setup(
        name= "tratatez",
        version= "1.0",
        author= "El Señor es el único eterno. Que la ciencia lo honre a Él.",
        author_email= "from.colombia.to.all@gmail.com",

        description= "Librería para manipulación avanzada de archivos de texto .txt enfocada para construir y simular una consola (preferiblemente utilizando el comando match de python)",
        long_description=long_description,
        long_description_content_type="text/markdown",
        
        license="MPL-2.0",
        license_files=("license.txt",),
        
        packages= ["tratatez", "tratatez.metodos_de_apoyo"],
        
        package_data={
            '': ['license.txt'],
        },
        include_package_data= True,
        url="https://github.com/Metal-Alcyone-zero/Prosigue",
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        ],
        
        python_requires= ">=3.11.3"
)

