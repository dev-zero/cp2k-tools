# cp2k-tools
Simple python scripts to somehow mangle CP2K output and generate some input

They can either be installed globally (as root) using:

```bash
git clone https://github.com/dev-zero/cp2k-tools.git
cd cp2k-tools
python setup.py install
```

or for a single user:

```bash
git clone https://github.com/dev-zero/cp2k-tools.git
cd cp2k-tools
python setup.py install --user
export PATH="${PATH}:${HOME}/.local/bin"
```

... in both cases you will get the following executables:

* ```extract_last_frame```
* ```generate_inputs```
* ```oq```

or even run them directly from the repository:

```bash
git clone https://github.com/dev-zero/cp2k-tools.git
cd cp2k-tools
PYTHONPATH=. python cp2k/cli.py [generate_inputs|extract_last_frame|oq] -h
```

# Available scripts

```
extract_last_frame.py [-h] [XYZINPUT] [XYZOUTPUT]

Extract the last frame from a XYZ file

Arguments:
    XYZINPUT                  the XYZ file to read (otherwise stdin)
    XYZOUTPUT                 the XYZ file to write (otherwise stdout)

Options:
    -h --help

```

```
generate_inputs.py [-h] single TEMPLATE SNIPPET [OUTPUT] [COORDS]
generate_inputs.py [-h] batch TEMPLATE SNIPPETDIR OUTPUTDIR

Use the configuration in SNIPPET/SNIPPETDIR to generate cp2k input files
based on the template.

Arguments:
    TEMPLATE                  the template to use for generating the input files
    SNIPPET                   a single json file
    SNIPPETDIR                a directory with json files
    OUTPUT                    the output file (otherwise standard output)
    COORDS                    the coordinates output file (otherwise standard output)
    OUTPUTDIR                 where to create the project directories

Options:
    -h --help
```

```
oq.py [-hj] [-f FILE] QUERY

Extract data from cp2k output

Options:
    -h --help
    -f --file=FILE    cp2k output file to read [default: -]
    -j --json         produce JSON output instead of pretty printed python objects
```
