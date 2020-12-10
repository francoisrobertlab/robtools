help([[
For detailed instructions, go to:
    http://mahonylab.org/software/chexmix/

This module loads the following modules and their requirements:
    - java/1.8.0_121
    - meme/5.0.3
]])

whatis("Version: 1.0.0")
whatis("Keywords: NGS, Peak Calling")
whatis("URL: http://mahonylab.org/software/chexmix")
whatis("Description: Tools to analyze next-generation sequencing (NGS) data")

always_load("nixpkgs/16.09")
always_load("java/1.8.0_121")
always_load("meme/5.0.3")

local home = os.getenv("HOME") or ""
local chexmix = pathJoin(home, "projects/def-robertf/chexmix")
local chexmix_jar = pathJoin(chexmix, "chexmix_v0.5.jar")
setenv("CHEXMIX_BASE", chexmix)
setenv("CHEXMIX_JAR", chexmix_jar)
