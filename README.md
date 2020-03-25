# StopMotionMaker
python-based Tool to create simple stop-motion videos based on openCV


## Some word on virtual environments

Create a venv by using this command: python -m venv /path/to/new/virtual/environment
If you change to another PC, you may adopt pyenv.cfg, where the path to the original python installation is stored.

Virtual environments are usually not version controlled. To document which dependancies you have, you should version control a requirements.txt

### How to work with the requirements.txt
You generate a "requirements" file (usually requirements.txt) that you commit with your project:

pip freeze > requirements.txt

Then, each developer will set up their own virtualenv and run:

pip install -r requirements.txt

