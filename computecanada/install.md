# Install/Delete robtools on Compute Canada servers

:memo: *The examples use Beluga server*


#### Options

* [Install](#install-robtools)
* [Delete](#delete-robtools)


## Install robtools

### Connect to the server

Use SSH command inside a terminal on [Mac](https://support.apple.com/en-ca/guide/terminal/apd5265185d-f365-44cb-8b09-71a064a42125/mac), Linux or [Windows 10 (PowerShell)](https://www.howtogeek.com/662611/9-ways-to-open-powershell-in-windows-10/)

On older versions of Windows, use [Putty](https://www.putty.org)

```shell
ssh beluga.computecanada.ca
```

### Run the configuration script

```shell
./projects/$PROJECT/robtools/install/configure.sh
source .bash_profile
module load robtools
```

:bulb: Replace `$PROJECT` with the project name

Try robtools

```shell
robtools --help
```

#### To receive emails for jobs, run this command:

```shell
email-sbatch.sh $email@ircm.qc.ca
```

:bulb: Replace `$email@ircm.qc.ca` with your email address


## Delete robtools

#### Run configuration script with `clean` option

```shell
./projects/$PROJECT/robtools/install/configure.sh clean
```

:bulb: Replace `$PROJECT` with the project name

#### Optional: To stop receiving emails for jobs, run this command:

```shell
./projects/$PROJECT/robtools/install/email-sbatch.sh clean
```

:bulb: Replace `$PROJECT` with the project name
