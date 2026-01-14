# tagrefsorter

A CLI tool to normalize LaTeX `\tag{}` numbering in Jupyter Notebook (`.ipynb`) files.

## Installation

```bash
pip install tagrefsorter
```

## Usage

```bash
tagrefsorter path/to/notebook.ipynb
```

The notebook is overwritten in place.

## Algorithm Overview

`tagrefsorter` processes LaTeX math blocks in markdown cells of a Jupyter Notebook and normalizes equation numbering based on the following rules:

- For each display math block written as `$$ ... $$`, a LaTeX `\tag{}` is **added if missing**, or **updated if already present**, so that equation numbers become sequential.

- If a display math block contains an `align` environment,

  ```latex
  $$\begin{align}
  ...
  \end{align}$$
  ```

  then each line inside the `align` environment is treated as an individual equation.
  A `\tag{}` is added or updated for each line, and equation numbers are assigned sequentially in appearance order.

- Existing tags of the form `\tag{x}` are considered **author-specified equation identifiers**.
  If a markdown cell contains a reference written as `$(x)$`, it is interpreted as a reference to `\tag{x}`.
  When equation numbers are renumbered, all corresponding `$(x)$` references are automatically updated to match the new equation number.

As a result, equation numbering and references remain consistent even after equations are reordered, added, or removed.
