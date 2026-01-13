import sys
import os

project = 'pyaudiosynth'
copyright = '2026, Wdboyes13'
author = 'Wdboyes13'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_immaterial'
html_static_path = ['_static']

sys.path.insert(0, os.path.abspath('..'))
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx_immaterial']
