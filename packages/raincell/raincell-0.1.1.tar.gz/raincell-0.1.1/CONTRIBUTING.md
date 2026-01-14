# How to contribute

## First of all...

> "Let us change our traditional attitude to the construction of programs: Instead of imagining that our main task is to instruct a computer what to do, let us concentrate rather on explaining to human beings what we want a computer to do." Donald E. Knuth, Literate Programming (1984)

You will probably find that Raincell's programming style is quite unusual for a Python package. It is developed using notebooks that integrate code, documentation, and tests in one place. Given that Jupyter notebooks are the primary tool for computational science in Python, we believe this to be the most natural approach.

When you view the notebook on GitHub or clone a local copy, you will see that, before developing each function, there are cells containing a few lines of code showing the expected output. Once the development produces the expected result, we combine the previous lines into a single function that can be imported from the library. Although this violates the 'Don't Repeat Yourself' (DRY) principle, this is a deliberate design choice. Just as solving a problem with pen and paper involves gradually developing the solution step by step, we believe this approach is equally useful for developing algorithms in their computational form. This makes the reasoning easier to understand and review, both for oneself and for others. Additionally, you can download the notebook containing the relevant section and use it as a starting point.

This is possible thanks to the ecosystem of [answer.ai](https://www.answer.ai/) (formerly [fast.ai](https://www.fast.ai/)) and in particular [nbdev](https://nbdev.fast.ai/). You can find more information in [this](https://www.youtube.com/watch?v=rX1yGxJijsI) talk.

## How to get started

If you are new to using `nbdev`, here are some useful pointers to get you started.

### Install raincell in Development mode

After cloning the repo, make sure the raincell package is installed in development mode:
```sh
$ pip install -e .
```

Please install the git hooks that run automatic scripts during each commit and merge to strip the notebooks of superfluous metadata (and avoid merge conflicts). If you are using Jupyter Notebooks or Jupyter Lab as your IDE, you only need to run the following command **inside** the repository:

```sh
nbdev_install_hooks
```

However, if you are using another IDE such as VS Code, you will need to run:

```sh
pre-commit install
```

Check the official nbdev documentation for more information on [nbdev_install_hooks](https://nbdev.fast.ai/tutorials/git_friendly_jupyter.html) or on [Pre-Commit Hooks](https://nbdev.fast.ai/tutorials/pre_commit.html).

Then make changes under the nbs/ directory and commit them.

If for some reason you cannot (or don't want to) install the pre-commit hooks, please run the following command **before each commit**:
```sh 
$ nbdev_prepare
```
You can learn what nbdev_prepare does [here](https://nbdev.fast.ai/tutorials/tutorial.html#prepare-your-changes).

## Do you want to contribute to the documentation?

* Docs are automatically created from the notebooks in the nbs folder.
* We use the **American Meteorological Society** citation [style](https://www.ametsoc.org/ams/publications/author-information/formatting-and-manuscript-components/references/) for our **references**. Please use this style when adding new references.

## Did you find a bug?

* Ensure the bug was not already reported by searching on GitHub under Issues.
* If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.
* Be sure to add the complete error messages.

#### Did you write a patch that fixes a bug?

* Open a new GitHub pull request with the patch.
* Ensure that your PR includes a test that fails without your patch and passes with it.
* Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.
