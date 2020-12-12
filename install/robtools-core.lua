help([[
For detailed instructions, go to:
    https://github.com/francoisrobertlab/robtools

You will need to load all the following module(s) before the "robtools-core" module is available to load.
    - python/3.5.4 or greater
]])

whatis("Version: 2.0")
whatis("Keywords: NGS, Utility")
whatis("URL: https://github.com/francoisrobertlab/robtools")
whatis("Description: Tools to analyze next-generation sequencing (NGS) data")

prereq(atleast("python","3.5.4"))

local home = os.getenv("HOME") or ""
local venv = pathJoin(home, "robtools-venv")
local installation = pathJoin(home, "projects/def-robertf/robtools")
prepend_path("PATH", pathJoin(installation, "install"))
prepend_path("PATH", pathJoin(venv, "bash"))
prepend_path("PATH", pathJoin(venv, "bin"))
