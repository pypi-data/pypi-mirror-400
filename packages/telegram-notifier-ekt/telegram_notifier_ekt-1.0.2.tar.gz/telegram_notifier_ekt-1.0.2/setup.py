from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Leer las dependencias desde requirements.txt
def parse_requirements(filename):
    """Lee y parsea el archivo requirements.txt"""
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    # Información básica
    name="telegram-notifier-ekt",           # Nombre del paquete en PyPI (si lo publicas)
    version="1.0.2",                    # Versión del paquete
    author="roan",
    description="Paquete reutilizable para enviar notificaciones por Telegram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Enlaces
    # url="https://github.com/tu-usuario/telegram-notifier",  # URL de tu repositorio
    # project_urls={
    #     "Bug Tracker": "https://github.com/tu-usuario/telegram-notifier/issues",
    #     "Documentation": "https://github.com/tu-usuario/telegram-notifier#readme",
    # },
    
    # Clasificadores (ayudan a PyPI a categorizar tu paquete)
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    
    # Paquetes a incluir
    packages=find_packages(),           # Encuentra automáticamente todos los paquetes
    
    # Dependencias
    install_requires=parse_requirements(r"E:\Users\1187574\Documents\workspace_arg\send-telegram-bot\requirements.txt"),
    
    # Requisitos de Python
    python_requires=">=3.7",
    
    # Palabras clave para búsqueda
    keywords="telegram, notification, bot, alerts",
    
    # Incluir archivos adicionales
    include_package_data=True,
    zip_safe=False,
)
