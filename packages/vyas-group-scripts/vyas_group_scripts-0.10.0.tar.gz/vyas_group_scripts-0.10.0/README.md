# vyas_group_scripts

vyas_group_scripts is a python package meant to hold tools built in aiding the Shubham Vyas Research lab in completing repetitive tasks. Most use cases will involve installing the package as a tool through uv of pipx and using the command line tools.

## Installation and Updating

To install the command line tools using uv use the command below:

```bash
uv tool install vyas_group_scripts
```

to update the package using uv use the command below:
```bash
uv tool install vyas_group_scripts --upgrade
```

alternatively you can use pipx. To install using pipx run the command below:
```bash
pipx install vyas_group_scripts
```

To update the package using pipx use the following command:
 ```bash
pipx upgrade vyas_group_scripts
```

## Further Setup

In order for pygab and pyrab to correctly format batch files they need to know your account number. They read this account number from an environment variable `ACTNUM`. Ensure that you have set this environment variable.

There are other optional environment variables you can set below are their names, defaults, and what they change

- `DEFAULT_DFT_TIME`, 00:59:00,The default dft job time in a batch file.
- `DEFAULT_DFT_PROCESSORS`, 36, The default number of processors a DFT job will use

## Available Commands
All commands with a * next to their name have a help flag that can be accessed by passing the `-h` flag. This is not placed here to keep documentation succinct.
### pygab *

python generate all batch. This generates a batch file for all gjf and inp files that match a pattern (match all by default). Soon it will also process xyz files

### pyrab *

python run all batch. This runs all batch files in a directory that match a pattern (match all by default) and have a matching input file.

### pysqm

prints the queue for the just the user's jobs
