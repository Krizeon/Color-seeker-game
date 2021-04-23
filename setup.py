from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [],
                 'excludes': [],
                 }
                 # 'include_files': ["maps","backgrounds","music","sounds","sprites"]}

base = 'Console'

executables = [
    Executable('main.py', base=base, target_name = 'colorseeker')
]

setup(name='Color Seeker',
      version = '0.1',
      description = 'A fun game by Kevin Hernandez',
      options = {'build_exe': build_options},
      executables = executables)
