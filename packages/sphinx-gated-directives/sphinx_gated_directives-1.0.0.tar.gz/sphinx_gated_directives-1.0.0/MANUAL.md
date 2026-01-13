---
file_format: mystnb
kernelspec:
  name: python3
---

````{margin}
```{admonition} User types
:class: tip
This section is useful for user type 3-5.
```
+++
{bdg-primary}`Sphinx Extension`
{bdg-link-light}`Included in TeachBooks Template <https://teachbooks.io/manual/external/template/README.html>`
{bdg-link-primary-line}`Included in TeachBooks Favourites <https://teachbooks.io/manual/features/favourites.html>`
````

# Gated Directives

```{include} README.md
:start-after: <!-- Start content -->
:end-before: <!-- Start caution -->
```

> [!CAUTION]
> Some directives parse the content inside the directive. If that content is moved between the start and end directives, it may not be parsed as expected, as it will be parsed separately. Please see to the [Examples](#examples) section for more details.

```{include} README.md
:start-after: <!-- End caution -->
:end-before: <!-- End configuration -->
```

> [!WARNING]
> Setting `override_existing` to anything other than `false` may lead to unexpected behavior if those directives are already in use.
> 
> Use with caution.

## Examples

### Simple example

We start with the example from the introduction:

:::::{grid} 2
:gutter: 1

::::{grid-item-card} Original syntax

```markdown
:::{warning}
This is a warning message.

So, be careful!
:::
```

::::

::::{grid-item-card} Gated syntax

```markdown
:::{warning-start}
This is a warning message.

:::

So, be careful!

:::{warning-end}
:::
```

:::::

:::::{grid} 2
:gutter: 1

::::{grid-item-card} Original result

:::{warning}
This is a warning message.

So, be careful!
:::

::::

::::{grid-item-card} Gated result

:::{warning-start}
This is a warning message.

:::

So, be careful!

:::{warning-end}
:::

::::

:::::

Although the syntax is more verbose, the result is identical.

A benefit of the gated syntax is that the end of a directive can more easily be identified.

### Nested code

Gated directives allow the use of nesting of code cells inside other directives. Code cells must always be at the top level of Jupyter Notebooks (`.ipynb`) and Text-based Notebooks (`.md`).

**Syntax**

````markdown
:::{prf:algorithm-start}
:label: alg:nested-code

To achieve a nice result, execute the following code:
:::

```{code-cell} ipython3
start = 1
end = 10
for i in range(start, end):
    print(i)
```

:::{prf:algorithm-end}
:::
````

**Result**

:::{prf:algorithm-start}
:label: alg:nested-code

To achieve a nice result, execute the following code:
:::

```{code-cell} ipython3
start = 1
end = 10
for i in range(start, end):
    print(i)
```

:::{prf:algorithm-end}
:::

Another benefit of the gated syntax is that code cells can be nested inside a `figure` directive:

````markdown
:::{figure-start} images/nothing.svg
:name: figure-label
:alt: Nothing
:align: center

This is a figure that contains some code.
:::

```{code-cell} ipython3
a = "This is some"
b = "Python code"
c = "that should be inside the figure,"
d = "above the caption."
print(f"{a} {b} {c} {d}")
```

:::{figure-end}
:::
````

:::{figure-start} images/nothing.svg
:name: figure-label
:alt: Nothing
:align: center

This is a figure that contains some code.
:::

```{code-cell} ipython3
a = "This is some"
b = "Python code"
c = "that should be inside the figure,"
d = "above the caption."
print(f"{a} {b} {c} {d}")
```

:::{figure-end}
:::

```{include} README.md
:start-after: <!-- Start contribute -->
```