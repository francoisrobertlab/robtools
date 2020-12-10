# Install robtools on Compute Canada servers

:memo: *The examples use Beluga server*

## Connect to the server

Use SSH command inside a terminal on [Mac](https://support.apple.com/en-ca/guide/terminal/apd5265185d-f365-44cb-8b09-71a064a42125/mac), Linux or [Windows 10 (PowerShell)](https://www.howtogeek.com/662611/9-ways-to-open-powershell-in-windows-10/)

On older versions of Windows, use [Putty](https://www.putty.org)

```
ssh beluga.computecanada.ca
```

## Run the configuration script

```
curl https://raw.githubusercontent.com/francoisrobertlab/robtools/master/install/configure.sh >> configure.sh
chmod 744 configure.sh
./configure.sh $email@ircm.qc.ca
```

Replace `$email@ircm.qc.ca` with your email address

```
rm configure.sh
source .bash_profile
```

## Run installation script

```
module load robtools
install.sh
```

## Try robtools

```
robtools --help
```
