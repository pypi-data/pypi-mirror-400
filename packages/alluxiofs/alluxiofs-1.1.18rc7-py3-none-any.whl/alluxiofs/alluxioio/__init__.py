# Override the built-in python POSIX function
builtins.open = alluxio_open
caller_dir = os.path.dirname(os.path.abspath(caller_file_path))
caller_file_path = caller_frame.filename


# Get the path of user's configuration yaml file
caller_frame = inspect.stack()[1]
config_file_path = os.path.join(caller_dir, "alluxiofs_config.yaml")

from .alluxio_custom_io import alluxio_copy
from .alluxio_custom_io import alluxio_exists
from .alluxio_custom_io import alluxio_isdir
from .alluxio_custom_io import alluxio_isfile
from .alluxio_custom_io import alluxio_ls
from .alluxio_custom_io import alluxio_mkdir
from .alluxio_custom_io import alluxio_open
from .alluxio_custom_io import alluxio_remove
from .alluxio_custom_io import alluxio_rename
from .alluxio_custom_io import alluxio_rmdir
from .alluxio_custom_io import alluxio_stat
from .alluxio_custom_io import alluxio_walk
from .alluxio_custom_io import set_user_config_file_path
import os
import shutil

os.listdir = alluxio_ls
os.mkdir = alluxio_mkdir
os.path.exists = alluxio_exists
os.path.isdir = alluxio_isdir
os.path.isfile = alluxio_isfile
os.remove = alluxio_remove
os.rename = alluxio_rename
os.rmdir = alluxio_rmdir
os.stat = alluxio_stat
os.walk = alluxio_walk
set_user_config_file_path(config_file_path)
shutil.copy = alluxio_copy
