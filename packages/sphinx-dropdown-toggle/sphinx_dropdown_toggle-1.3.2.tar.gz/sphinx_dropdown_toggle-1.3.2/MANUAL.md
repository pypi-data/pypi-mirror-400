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

```{include} README.md
```

## Usage

When dropdowns are included on a page, initially one of three buttons will be shown:

- <i class="fa-solid fa-angles-down"></i> will be shown at the top of the page if all dropdowns are closed. Clicking this button will open all dropdowns.

- <i class="fa-solid fa-angles-up"></i> will be shown at the top of the page if all dropdowns are opened. Clicking this button will close all dropdowns.

- <div style="display: flex; flex-direction: column; align-items: center; line-height: 1; gap: 0; margin: 0;margin-left:-5px;margin-right:-5px"><i class="fa-solid fa-angle-up" style="margin-bottom: -5px;"></i><i class="fa-solid fa-angle-down" style="margin-top: -5px;"></i></div> will be shown at the top of the page if some dropdowns are closed and some are opened. This button provides a menu on hover or click, which contains the previous two buttons.

After clicking one of the buttons, the button at the top of the page will reflect the current state of all dropdowns on the page.

If opening or closing a dropdown (in the main article) causes the current state to change, to the button at the top of the page  will again directly reflect the new state.

## Reference examples

:::{admonition} A proof
:class: dropdown

First we consider $x_-=-ai$ and take its square:

$$
x_-^2 = \left(-ai\right)^2 = a^2i^2 = -a^2.
$$

This shows that $x_-=-ai$ is indeed a solution to the equation $x^2=-a^2$.

We repeat the same for $x_+=ai$:

$$
x_+^2 = \left(ai\right)^2 = a^2i^2 = -a^2.
$$

We also find that $x_+=ai$ is a solution to the equation $x^2=-a^2$.

:::

::::{grasple}
:iframeclass: dark-light
:url: https://embed.grasple.com/exercises/c5058abb-3d5b-4e8c-b836-40aeff08a301?id=65634
:label: grasple_exercise_1_3_A
:dropdown:
:description: Just to compute a cross product.

::::
