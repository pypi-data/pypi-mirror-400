# SulvionPiGUI 🎨

**SulvionPiGUI** (or `spgui`) is a premium, powerful, and easy-to-use Python GUI library built on top of `CustomTkinter`. It's designed for developers who want to create beautiful, grid-based desktop applications with minimal code.

## 🌟 Features

- **Grid-Based Layout**: No more complex pixel math. Place widgets using intuitive grid coordinates.
- **Modern Aesthetics**: Built-in dark and light themes with premium `CustomTkinter` widgets.
- **Dynamic Plots**: Integrated Matplotlib support for real-time data visualization.
- **Interactive Widgets**: Drag-and-drop, resizable widgets, and easy event binding.
- **High-DPI Support**: Automatically handles screen scaling for crisp visuals on all displays.
- **Beginner Friendly**: Simple API inspired by the best practices of modern web design.

## 🚀 Installation

You can install `SulvionPiGUI` via pip:

```bash
pip install spgui
```

Dependencies:
- `customtkinter`
- `matplotlib`
- `pillow`

## 📖 Quick Start

Here is a simple example to get you started:

```python
import SPGUI as ui

# Initialize app with a 10x10 grid
app = ui.init(
    SIZE=[10, 10], 
    title="Hello SPGUI", 
    theme="dark", 
    show_grid=True
)

# Add a label at (0, 0)
app.label(pos=[0, 0], size=[10, 1], text="Welcome to SulvionPiGUI!", text_size=16)

# Add a button that shows a message
def say_hello():
    app.message("Greeting", "Hello World!")

app.btn(pos=[4, 4], size=[2, 1], text="Click Me!", onclick=say_hello)

# Add a text input
def on_text_changed(text):
    print(f"User typed: {text}")

app.input(pos=[2, 6], size=[6, 1], placeholder="Type here...", onchange=on_text_changed)

app.run()
```

## 🛠️ Available Widgets

- `app.label()` / `app.text()`: Display text.
- `app.btn()` / `app.button()`: Interactive buttons.
- `app.input()`: Text entry fields.
- `app.checkbox()`: Toggle boxes.
- `app.dropdown()`: Select menus.
- `app.slider()`: Range sliders.
- `app.number()`: Numeric inputs with filtering.
- `app.plot()`: Matplotlib charts (line/bar).
- `app.table()`: Data grids.
- `app.image()`: Display images via PIL.

## ⛓️ Performance & Debugging

Enable the debug grid during development to visualize your layout:

```python
app = ui.init(show_grid=True, coord_color="#00ff00")
```

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

Developed with ❤️ by **Hafiz Daffa W**.
- **GitHub**: [@HafizDaffa01](https://github.com/HafizDaffa01)
- **Email**: [hafizdaffaw+dev@gmail.com](mailto:hafizdaffaw+dev@gmail.com)
