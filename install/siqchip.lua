help([[
For detailed instructions, go to:
    https://github.com/francoisrobertlab/siQ-ChIP
]])

whatis("Version: 1.0.0")
whatis("Keywords: siQ-ChIP, NGS, Utility")
whatis("URL: https://github.com/francoisrobertlab/siQ-ChIP")
whatis("Description: siQ-ChIP: sans spike-in Quantitative ChIP-seq")

local home = os.getenv("HOME") or ""
local base = pathJoin(home, "projects/def-robertf/siQ-ChIP")
prepend_path("PATH", base)
setenv("SIQ_CHIP_BASE", base)
