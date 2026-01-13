# EXCE


> export code from notebook cells to python source files

The first Quatro document I created was used to implement a python
module based on some math formula’s from an article (about measuring sap
flux in tree stems) LaTeX formated formula’s. Step by step functions
were build and documented along the formula’s and some example
calculations. This worked like a charm but the disadvantage was that I
had to copy the code from the document into a separate python file for
use in our runtime environment. It worked fine but the disadvantage to
this approach is that changes in one document had to be manually copied
and paste into another. Such an arrangement will inevitably lead to
errors.

What I needed was a way to convert or export selected code cells into a
python source code file automatically and I found this in NBDev. Using
it worked fine for a while, NBDev exports your code, builds the
documentation and, if desired, packages the code uploads them to PyPi. I
build packages with it that I relied on. But it is pretty big, requires
projects to be laid out in a certain way and occasionally the PyPi
packaging fails.

So, something smaller, without the PyPi packaging, was needed and I
might as well look back at the original need of simply extracting or
exporting python sourcefiles from Quarto and Jupyter documents.

### IPython magics

### View documentation

You can view the documentation local with (and a local .venv active)

``` sh
quarto preview docs/index.qmd
```

Or (with a local .venv active)

``` sh
quarto render docs
```

from `docs/_site`
