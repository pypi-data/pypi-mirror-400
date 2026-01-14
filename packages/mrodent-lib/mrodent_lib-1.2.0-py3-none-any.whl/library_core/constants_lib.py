import logging
logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%H:%M:%S', level=logging.DEBUG)
# logging.basicConfig(format='line %(lineno)d ============> %(message)s',
#         datefmt='%H:%M:%S', level=logging.DEBUG)
basic_logger = logging.getLogger('BASIC')
basic_logger.info(f'start {__file__}')

import pathlib, sys, os

# get project name
cwd_path = pathlib.Path.cwd()
r"""
2025-12-28 typically found when lib (mrodent-dev-lib) is a pip-installed module:
__file__ |D:\apps\Python\virtual_envs\dev_doc_indexer\lib\site-packages\library_core\constants.py|
cwd_path |D:\My documents\software projects\EclipseWorkspace\doc_indexer|
"""
# get type of run
cwd_path_parts = cwd_path.parts
# determined_run_type = False
IS_PRODUCTION = None
run_type_index = -1
for i, part in enumerate(cwd_path_parts):
  part_lc = part.lower()
  if part_lc == 'operative':
    IS_PRODUCTION = True
    # determined_run_type = True
    break

for i, part in enumerate(cwd_path_parts):
  part_lc = part.lower()
  if 'workspace' in part_lc:

    if IS_PRODUCTION:
      basic_logger.error(f'FATAL. The cwd {cwd_path} contains a path part with "operative" but also a part with "workspace"!')
      sys.exit()

    IS_PRODUCTION = False
    # determined_run_type = True
    break

if IS_PRODUCTION is None:
  basic_logger.error(f'FATAL. {__file__}. Neither "operative" nor "workspace" found in CWD path parts: {cwd_path_parts}')
  sys.exit()

if not IS_PRODUCTION:
  basic_logger.info(f'--- this is a DEV run of file {__file__}')

PROJECT_NAME = cwd_path_parts[i + 1]

# get PART2 env var value
PART2_NAME = 'PART2'
PART2_VAL = os.environ.get(PART2_NAME)
if PART2_VAL == None:
  basic_logger.error(f'FATAL. Environment variable |{PART2_NAME}| not set')
  sys.exit()

# get OS
lc_os_name = sys.platform.lower()
IS_LINUX = None
if lc_os_name.startswith('lin'):
  IS_LINUX = True
elif lc_os_name.startswith('win'):
  IS_LINUX = False
if IS_LINUX == None:
  basic_logger.error(f'FATAL. Cannot operate in OS {sys.platform}')
  sys.exit()
