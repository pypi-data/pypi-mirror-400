:::{admonition} MyST colon fenced directive with a title
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
:::

.

:::{admonition} MyST colon fenced directive with simple metadata
:class: foo
:truc: bla

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
:::

::::{admonition} MyST colon fenced directive with nested directive with simple metadata
:::{image} foo.png
:class: foo
:truc: bla
:::
::::

% Admonitions with arbitrary yaml metadata are not yet supported.
% Issue: in a container, the `---` is interpreted as hrule by the parser
%
% :::{admonition} MyST colon fenced directive with arbitrary yaml metadata
% ---
% foo:
%   bar: 1
% ---
%
% Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
% incididunt ut labore et dolore magna aliqua.
% :::

.

% Unknown colon-fenced directives are not yet implemented
% :::{exercise}
% This is an unknown admonition.
% :::

.

::::{admonition} MyST colon fenced directive with two nested admonitions
:::{admonition}
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
:::

:::{admonition}
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
:::

:::{admonition}
truc
:::
::::

.

::::{hint} A hint with alternating nested tips and texts
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.

:::{tip}
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
:::

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.

:::{tip}
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
:::

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
::::

.

- foo
  :::{tip} A directive nested in bullet points
  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
  incididunt ut labore et dolore magna aliqua.
  :::

.
