"""
A quick script in pure python (3.10 or above) to generate a DrawIO Symbol Library
from the main SVG library.

Draw.IO library support is limited.  In terms of customising the styles, see
the last comment here:

https://stackoverflow.com/questions/73309145/edit-svg-color-in-draw-io

For details on custom library:

https://www.drawio.com/blog/custom-libraries

For details on library file format:

https://github.com/jgraph/drawio-libs


It can also help to tweak symbols in DrawIO, drag into a library, export the library, and inspect.
"""
import json
import pathlib
import base64
from xml.etree import ElementTree as Et
from xml.etree.ElementTree import Element, SubElement, tostring

Et.register_namespace("xlink", "http://www.w3.org/1999/xlink")
Et.register_namespace("", "http://www.w3.org/2000/svg")  # Default namespace


BASE_PATH = pathlib.Path(__file__).parent.parent
SVG_DIR = BASE_PATH / "SVG"
OVERRIDE_PATH = BASE_PATH / "DrawIO" / "override"
LIB_FILE = BASE_PATH / "DrawIO" / "PiicoDevSymbols.xml"


def process_symbol(svg_path: pathlib.Path, as_xml=False) -> tuple[int, int, str]:
    # Read the SVG file
    tree = Et.parse(svg_path)
    root = tree.getroot()

    # Extract height and width of the SVG element
    width = root.get("width").replace("px", "")
    height = root.get("height").replace("px", "")

    # Convert back to string
    modified_svg = Et.tostring(root, encoding="unicode")

    # Encode to BASE64
    encoded_svg = base64.b64encode(modified_svg.encode("utf-8")).decode("utf-8")

    if as_xml:
        # Create the root element
        mx_graph_model = Element("mxGraphModel")
        # Create 'root' element
        root = SubElement(mx_graph_model, "root")

        # Create 'mxCell' elements
        # noinspection PyUnusedLocal
        mx_cell0 = SubElement(root, "mxCell", {"id": "0"})
        # noinspection PyUnusedLocal
        mx_cell1 = SubElement(root, "mxCell", {"id": "1", "parent": "0"})

        style = (
            f"editableCssRules=.*;"
            f"shape=image;"
            f"verticalLabelPosition=bottom;"
            f"verticalAlign=top;"
            f"imageAspect=0;"
            f"aspect=fixed;"
            f"image=data:image/svg+xml,{encoded_svg}"
        )

        mx_cell2 = SubElement(
            root,
            "mxCell",
            {"id": "2", "value": "", "style": style, "vertex": "1", "parent": "1"},
        )

        # Create 'mxGeometry' element as a child of mxCell2
        SubElement(
            mx_cell2,
            "mxGeometry",
            {
                "y": "2.842170943040401e-14",
                "width": width,
                "height": height,
                "as": "geometry",
            },
        )

        # Convert the XML tree to a string
        xml_string = tostring(mx_graph_model, encoding="unicode")
        # data = base64.b64encode(xml_string.encode("utf-8")).decode("utf-8")

        #   {
        #     "xml": "&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"rounded=0;whiteSpace=wrap;html=1;\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry y=\"2.842170943040401e-14\" width=\"120\" height=\"60\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;",
        #     "w": 120,
        #     "h": 60,
        #     "aspect": "fixed"
        #   }

        data = xml_string.replace("<", "&lt;").replace(">", "&gt;")
        # data = xml_string

    else:
        data = f"data:image/svg+xml;base64,{encoded_svg}"

    return int(height), int(width), data


def unescape_export_str(xml_str):
    """
    A utility for dev / debugging which unescapes a string as per
    https://github.com/jgraph/drawio-libs
    """
    return xml_str.replace("&lt;", "<").replace("&gt;", ">").replace('\\"', '"')


if __name__ == "__main__":

    def _main():
        library = []
        overrides = {p.stem: p for p in OVERRIDE_PATH.glob("*.svg")}

        for path in SVG_DIR.glob("*.svg"):
            title = path.stem
            lib_entry = {
                "title": title,
                "aspect": "fixed",
            }

            if title in overrides:
                h, w, data = process_symbol(overrides[title], as_xml=True)
                lib_entry.update(
                    {
                        "xml": data,
                        "w": w,
                        "h": h,
                    }
                )
            else:
                h, w, data = process_symbol(path)
                lib_entry.update(
                    {
                        "data": data,
                        "w": w,
                        "h": h,
                    }
                )

            library.append(lib_entry)

        library.sort(key=lambda item: item["title"])

        with open(LIB_FILE, "w") as f:
            # noinspection SpellCheckingInspection
            f.write(f"<mxlibrary>{json.dumps(library, indent=4)}</mxlibrary>")

    _main()
