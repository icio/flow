# Job Flow Descriptions

`/example` is a mimic of the files that are created by data-processing jobs. Job-output directories are appended with `_` and files declare their input by including a list of the files that they depend on in their first few lines.

Test the example with

    bin/flow example example.dot
    bin/flow --format svg example example.svg --highlight \*03

Highlight options have to come at the end because you can specify an indeterminate amount of them and it is greedy (fixme?).

If you execute the program with `--monitor` it will write to the file every time that the base tree is updated.

    bin/flow -f png example example.png -H \*03

![An example job flow](https://github.com/icio/flow/raw/master/example.png)
