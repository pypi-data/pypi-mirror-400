from setuptools import setup, find_packages

setup(
    name='jhOMR-webInterface',
    version='0.2.0',
    packages=find_packages(),  # Automatically find packages
    description='This is WebcamOMR package that enables creating three sets of questions by shuffling Set_1.docx. The shuffling will be done so that there will be minimum amount of overlap in the correct answers between any two sets. The package also enables checking exam scripts.',
    author='Md Nur Kutubul Alam',
    author_email='alamjhilam@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
         ],
    install_requires=[
        "fastapi",
        "uvicorn",                  # Used for running FastAPI applications
        "pandas",
        "numpy",
        "opencv-python",            # For cv2
        "python-multipart",         # FastAPI dependency for form/file uploads
        "python-docx",              # For docx
        "openpyxl",                 # For Excel
        "requests",                 # For HTTP requests
        "Jinja2",                   # For templates
        "starlette",                # FastAPI dependency, usually handled by FastAPI install
        "pydantic"                  # For BaseModel
    ]
)
