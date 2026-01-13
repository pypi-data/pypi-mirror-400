# BasecampUI

BasecampUI is a FastHTML UI library built on top of the excellent Basecoat. It's design goal is to create complex UI components with minimal boilerplate, while still allowing as much customization as possible

## Quickstart

``` sh
pip install basecampui
```

``` python
from fasthtml.common import *
from basecampui.all import *

app = FastHTML()
rt = app.route

@rt
def index():
    return Div(
        Breadcrumb(['Home', 'Documents', 'Doc 1']),
    )

serve()
```

## Using Icons

BasecampUI uses fastlucide for icons. For development purposes,
basecampui.all provides a standalone Icon function that creates a new
SVG for each icon instance, making it easy to quickly iterate.

``` python
Div(
    Icon("apple")
)
```

If you are happy with your set of icons, you can predefine them on app
setup, and use the fastlucide spritesheet singleton instead of Icon
function. This create a reference sprite sheet that all icons icons
point to, making it more efficient when rendering a large number of the
same icons.

``` python
app = FastHTML(icons=["apple"])

Div(
    spritesheet("apple")
)
```

## Code highlighting

Code highlight is included by default on app setup. You can disable this
to reduce loadtimes if you don’t need highlighting for your project.

``` python
app = FastHTML(code_highlight=False)
```

If you do want code highlighting, you can optionally pass in custom
keywords to the app startup.

``` python
custom_kws="myFunction myClass CodeHighlightFunc"
app = FastHTML(custom_kws=custom_kws)
```
