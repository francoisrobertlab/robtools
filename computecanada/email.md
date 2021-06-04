# To receive emails for jobs

Run the following commands:

```shell
module load robtools
email-sbatch.sh $email@ircm.qc.ca
```

:bulb: Replace `$email@ircm.qc.ca` with your email address


## Optional: To stop receiving emails for jobs, run the following commands:

```shell
module load robtools
email-sbatch.sh clean
```
