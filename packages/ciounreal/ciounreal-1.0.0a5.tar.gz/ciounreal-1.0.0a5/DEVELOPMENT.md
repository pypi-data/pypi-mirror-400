# Conductor plugin for Unreal. Development

## Building the docs

1. Install python requirements for building Sphinx documentation
   ```
   pip install -r requirements_docs.txt
   ```
2. Build and install the **ciounreal** package in the python that you use to build the docs
   ```
   cd .\path\to\ciounreal
   python -m build
   python -m pip install dist/ciounreal-0.0.3-py2.py3-none-any.whl
   ```
3. Go to the "docs" folder
   ```
   cd docs
   ```

4. Run documentation building
   ```
   make.bat html
   ```
   
5. Generated documentation will be placed at *docs/build/html* folder.
   You can visit the "Home" page of the docs by opening the **index.html** file

