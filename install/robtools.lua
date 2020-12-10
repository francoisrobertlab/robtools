help([[
For detailed instructions, go to:
    https://github.com/francoisrobertlab/robtools

This module loads the following modules and their requirements:
    - python/3.7.4
    - perl/5.22.4
    - fastqc/0.11.8
    - bwa/0.7.17
    - bowtie2/2.3.4.3
    - samtools/1.9
    - bedtools/2.27.1
    - kentutils/20180716
    - sra-toolkit/2.9.6
    - vap
]])

whatis("Version: 1.0.0")
whatis("Keywords: NGS, Utility")
whatis("URL: https://github.com/francoisrobertlab/robtools")
whatis("Description: Tools to analyze next-generation sequencing (NGS) data")

always_load("nixpkgs/16.09")
always_load("gcc/7.3.0")
always_load("python/3.7.4")
always_load("perl/5.22.4")
always_load("fastqc/0.11.8")
always_load("bwa/0.7.17")
always_load("bowtie2/2.3.4.3")
always_load("samtools/1.9")
always_load("bedtools/2.27.1")
always_load("sra-toolkit/2.9.6")
always_load("kentutils/20180716")
always_load("vap")

local home = os.getenv("HOME") or ""
local venv = pathJoin(home, "robtools-venv")
local call_nucleosomes = pathJoin(home, "projects/def-robertf/CallNucleosomes")
local installation = pathJoin(home, "projects/def-robertf/robtools")
prepend_path("PATH", pathJoin(installation, "install"))
prepend_path("PATH", pathJoin(venv, "bash"))
prepend_path("PATH", pathJoin(venv, "bin"))
prepend_path("PERL5LIB", pathJoin(call_nucleosomes, "perl_library"))
