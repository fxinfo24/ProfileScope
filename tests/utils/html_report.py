"""
Utilities for generating valid HTML reports with pytest-html
"""


def add_html_extra(report, name, content):
    """
    Add an HTML extra to a pytest report in a format compatible with pytest-html

    Args:
        report: The pytest report object
        name: Name of the extra section
        content: HTML content as string
    """
    if not hasattr(report, "extra"):
        report.extra = []

    report.extra.append({"name": name, "content": content, "format": "html"})


def add_text_extra(report, name, content):
    """
    Add a text extra to a pytest report in a format compatible with pytest-html

    Args:
        report: The pytest report object
        name: Name of the extra section
        content: Text content as string
    """
    if not hasattr(report, "extra"):
        report.extra = []

    report.extra.append({"name": name, "content": content, "format": "text"})


def add_image_extra(report, name, image_path, width=None):
    """
    Add an image extra to a pytest report in a format compatible with pytest-html

    Args:
        report: The pytest report object
        name: Name of the extra section
        image_path: Path to the image file
        width: Optional width for the image (in pixels)
    """
    import base64

    if not hasattr(report, "extra"):
        report.extra = []

    # Read the image file
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
    except Exception as e:
        # If the image can't be read, add an error message instead
        report.extra.append(
            {
                "name": name,
                "content": f"Failed to read image: {str(e)}",
                "format": "text",
            }
        )
        return

    # Determine image type from file extension
    import os

    extension = os.path.splitext(image_path)[1].lower()
    image_type = {
        ".png": "png",
        ".jpg": "jpeg",
        ".jpeg": "jpeg",
        ".gif": "gif",
        ".svg": "svg+xml",
    }.get(extension, "png")

    # Create base64 image
    image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Create HTML for image
    style = f"width: {width}px;" if width else ""
    html = f'<img src="data:image/{image_type};base64,{image_base64}" style="{style}">'

    report.extra.append({"name": name, "content": html, "format": "html"})
