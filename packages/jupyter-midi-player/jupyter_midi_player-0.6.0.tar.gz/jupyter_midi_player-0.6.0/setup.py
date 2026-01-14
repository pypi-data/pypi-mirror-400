from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='jupyter-midi-player',
    version='0.6.0',
    url='https://github.com/drscotthawley/midi-player',
    project_urls={
        'Source': 'https://github.com/drscotthawley/midi-player',  
    },
    packages=find_packages(),
    package_data={
        'midi_player': ['static/js/*.js'],
    },
    include_package_data=True,
    # install_requires=[  ], # -- Note: No required packages! 
    author='Scott H. Hawley',
    author_email='scott.hawley@belmont.edu',
    description='Python launcher of animated MIDI player by @cifkao & @magenta',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
)

