"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import platformdirs as fldr
from obj_mpp.config.app import APP_NAME

CONFIG_PATH = fldr.user_config_path(appname=APP_NAME, ensure_exists=True) / "config.ini"
