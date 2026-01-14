"""Fix .so objects so that OSX codesign does not SIGKILL the process.

See issue https://gitlab.com/ifosim/finesse/finesse3/-/issues/460

We should not have to do this I feel...
"""
import glob
import shutil
import os

sos = glob.glob("**/*.so", recursive=True)

for so in sos:
    shutil.copyfile(so, so + "2")
    shutil.copyfile(so + "2", so)
    os.remove(so + "2")
