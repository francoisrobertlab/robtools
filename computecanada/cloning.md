# Cloning robtools on Compute Canada servers

:memo: *The examples use def-robertf project*


## Clone robtools inside project folder

```shell
cd ~/projects/def-robertf
git clone https://github.com/francoisrobertlab/robtools.git
```


## Change project name, if applicable

```shell
cd robtools
./install/change-project.sh $project_name
```

:bulb: Replace `$project_name` with the project name


## Link modules

```shell
cd ~/projects/def-robertf
mkdir modules
cd modules
ln -s ../robtools/install/robtools-core.lua
ln -s ../robtools/install/robtools.lua
```


## Install VAP (Optional)

```shell
cd ~/projects/def-robertf
mkdir vap
cd vap
wget -O vap https://bitbucket.org/labjacquespe/vap_core/downloads/vap_core_1.1.0_linux64
cd ../modules
ln -s ../robtools/install/vap.lua
```


## Install Plot2DO (Optional)

```shell
cd ~/projects/def-robertf
git clone https://github.com/francoisrobertlab/plot2DO.git
cd modules
ln -s ../plot2DO/plot2do.lua
```


## Install siQ-ChIP (Optional)

```shell
cd ~/projects/def-robertf
git clone https://github.com/BradleyDickson/siQ-ChIP.git
```


## Install CallNucleosomes (Optional)

```shell
cd ~/projects/def-robertf
git clone https://github.com/francoisrobertlab/CallNucleosomes.git
```
