# Using sbatch

## Number of samples

**When using the `sbatch` command, the array parameter must match the number of samples minus 1**

If you have **2** samples in you dataset, the array parameter should be :

```
sbatch --array=0-1
```

If you have **4** samples in you dataset, the array parameter should be :

```
sbatch --array=0-3
```


## Email notification

All scripts have email notification enabled
