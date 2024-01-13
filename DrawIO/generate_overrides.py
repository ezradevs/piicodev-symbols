"""
A quick script that generates an override file for certain SVGs so that they
work better with DrawIO.

The main changes are to the cables.  A single path is applied to keep a 40x40 icon
and then  Draw.IO connectors can be used instead.  Changes to the file:

* Bounding rectangle removed
* A single line (which can be copied to each file)
    * line width 2 set in styles
    * "stroke-width:45" manually removed.
* Shift the text up by adding transform="translate(0, -2)" to each path


"""
import re
import pathlib
from xml.etree import ElementTree as Et

Et.register_namespace("xlink", "http://www.w3.org/1999/xlink")
Et.register_namespace("", "http://www.w3.org/2000/svg")  # Default namespace


BASE_PATH = pathlib.Path(__file__).parent.parent
SVG_DIR = BASE_PATH / "SVG"
OVERRIDE_PATH = BASE_PATH / "DrawIO" / "override"
OVERRIDE_FILES = [
    "50mm-Cable",
    "100mm-Cable",
    "200mm-Cable",
    "500mm-Cable",
]


def process_svg(svg_path: pathlib.Path) -> str:
    # Read the SVG file
    tree = Et.parse(svg_path)
    root = tree.getroot()

    # Add style element
    style = Et.Element("style", type="text/css")
    style.text = ".line{stroke:rgb(0%,0%,0%);stroke-width:2}\n.text{fill:rgb(0%,0%,0%)}"
    root.insert(0, style)

    # Apply class attribute based on style definitions:  Assumes RGB defined for all colours.
    for element in root.findall(".//*[@style]"):
        style = element.get("style")
        if "stroke:r" in style:
            element.set("class", "line")
            element.set("style", re.sub(r"stroke:[^;]+;?", "", style))

        if "fill:r" in style:
            element.set("class", (element.get("class", "") + " text").strip())
            element.set("style", re.sub(r"fill:[^;]+;?", "", style))

    # Convert back to string
    modified_svg = Et.tostring(root, encoding="unicode")

    return modified_svg


if __name__ == "__main__":

    def _main():
        for title in OVERRIDE_FILES:
            src = SVG_DIR / f"{title}.svg"
            new_svg = process_svg(src)
            dest_file = OVERRIDE_PATH / f"{title}.svg"

            with dest_file.open("w") as f:
                # noinspection SpellCheckingInspection
                f.write(new_svg)

    _main()
