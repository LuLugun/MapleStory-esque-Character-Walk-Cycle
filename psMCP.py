import win32com.client
import os
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("Photoshop-MCP-Advanced")

# Global Photoshop application and document references
psApp = None
doc = None


# Directory variables
PSD_DIRECTORY = os.getenv("PSD_DIRECTORY")
EXPORT_DIRECTORY = os.getenv("EXPORT_DIRECTORY")
ASSETS_DIR = os.getenv("ASSETS_DIR")

@mcp.tool()
def list_available_psds() -> list:
    """
    Lists all PSD files in the designated PSD_DIRECTORY.
    Returns:
        list: Filenames of all PSD files found.
    """
    if not os.path.exists(PSD_DIRECTORY):
        return ["PSD directory not found."]
    
    psd_files = [f for f in os.listdir(PSD_DIRECTORY) if f.lower().endswith(".psd")]
    return psd_files if psd_files else ["No PSD files found."]

@mcp.tool()
def open_photoshop(open: bool) -> str:
    """
    Open Photoshop application if not already opened.
    args:
        open (bool): True to open Photoshop
    Returns:
        str: Status message indicating whether Photoshop was opened or not.
    """
    global psApp
    if open:
        psApp = win32com.client.Dispatch("Photoshop.Application")
        return "Opened"
    return "Not Opened"

@mcp.tool()
def open_psd_file(filename: str) -> str:
    """
    Open a PSD file from the PSD_DIRECTORY in Photoshop.

    Args:
        filename (str): Name of the PSD file (with or without .psd extension)
    
    Returns:
        str: Success or error message
    """
    global doc
    if not psApp:
        return "Photoshop not initialized"
    
    if not filename.lower().endswith('.psd'):
        filename += '.psd'
    
    psd_path = os.path.join(PSD_DIRECTORY, filename)
    
    if not os.path.isfile(psd_path):
        return f"File not found: {psd_path}"
    
    doc = psApp.Open(psd_path)
    return f"Opened PSD: {psd_path}"

@mcp.tool()
def edit_text_layer(layer_name: str, new_text: str) -> str:
    """
    Edit the contents of a text layer.
    args:
        layer_name (str): Name of the text layer to edit
        new_text (str): New text content for the layer
    Returns:
        str: Success or error message
    """
    if not doc:
        return "No document loaded"
    layer = doc.ArtLayers[layer_name]
    layer.TextItem.contents = new_text
    return f"Text in '{layer_name}' updated."

@mcp.tool()
def set_text_layer_size(layer_name: str, size: float) -> str:
    """
    Change the font size of a text layer.
    args:
        layer_name (str): Name of the text layer to edit
        size (float): New font size for the layer
    Returns:
        str: Success or error message
    """
    if not doc:
        return "No document loaded"
    layer = doc.ArtLayers[layer_name]
    layer.TextItem.size = size
    return f"Font size of '{layer_name}' set to {size}."

@mcp.tool()
def set_layer_visibility(layer_name: str, visible: bool) -> str:
    """
    Show or hide a layer by name.
    agrs:
        layer_name (str): Name of the layer to show/hide
        visible (bool): True to show the layer, False to hide it
    Returns:
        str: Success or error message
    """
    doc = get_active_document()
    if not doc:
        return "No document loaded"
    layer = doc.ArtLayers[layer_name]
    layer.visible = visible
    return f"Layer '{layer_name}' visibility set to {visible}."

@mcp.tool()
def export_as_png(filename: str) -> str:
    """
    Export the active document as a PNG to the EXPORT_DIRECTORY.
    
    Args:
        filename (str): Name of the PNG file (without extension)
    Returns:
        str: Success or error message
    """
    if not doc:
        return "No document loaded"
    full_path = os.path.join(EXPORT_DIRECTORY, f"{filename}.png")
    options = win32com.client.Dispatch('Photoshop.ExportOptionsSaveForWeb')
    options.Format = 13  # PNG
    options.PNG8 = False
    doc.Export(ExportIn=full_path, ExportAs=2, Options=options)
    return f"Exported PNG to {full_path}"

@mcp.tool()
def export_as_jpg(filename: str, quality: int = 100) -> str:
    """
    Export the active document as a JPG to the EXPORT_DIRECTORY.
    
    Args:
        filename (str): Name of the JPG file (without extension)
        quality (int): JPEG quality (0–100)
    Returns:
        str: Success or error message
    """
    if not doc:
        return "No document loaded"
    full_path = os.path.join(EXPORT_DIRECTORY, f"{filename}.jpg")
    options = win32com.client.Dispatch('Photoshop.ExportOptionsSaveForWeb')
    options.Format = 6  # JPEG
    options.Quality = quality
    doc.Export(ExportIn=full_path, ExportAs=2, Options=options)
    return f"Exported JPG to {full_path} with quality {quality}"

def get_active_document():
    try:
        return psApp.Application.ActiveDocument
    except Exception:
        return None
    
@mcp.tool()
def list_layers() -> list:
    """
    List all layer names in the active Photoshop document.
    Returns:
        list: List of layer names.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    return ["- "+layer.Name for layer in doc.ArtLayers]

@mcp.tool()
def rename_layer(old_name: str, new_name: str) -> str:
    """
    Rename a Photoshop layer.
    Args:
        old_name (str): Current name of the layer.
        new_name (str): New name for the layer.
    Returns:
        str: Confirmation message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    layer = doc.ArtLayers[old_name]
    layer.Name = new_name
    return f"Layer '{old_name}' renamed to '{new_name}'"

@mcp.tool()
def delete_layer(layer_name: str) -> str:
    """
    Delete a Photoshop layer by name.
    Args:
        layer_name (str): Name of the layer to delete.
    Returns:
        str: Confirmation message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    
    layer = doc.ArtLayers[layer_name]
    layer.Delete()
    return f"Layer '{layer_name}' deleted."

@mcp.tool()
def duplicate_layer(layer_name: str, new_name: str = None) -> str:
    """
    Duplicate a Photoshop layer.
    Args:
        layer_name (str): Name of the layer to duplicate.
        new_name (str, optional): New name for the duplicated layer.
    Returns:
        str: Confirmation message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    
    original = doc.ArtLayers[layer_name]
    dup = original.Duplicate()
    if new_name:
        dup.Name = new_name
    return f"Layer '{layer_name}' duplicated as '{dup.Name}'."

@mcp.tool()
def change_layer_opacity(layer_name: str, opacity: float) -> str:
    """
    Change the opacity of a layer.
    Args:
        layer_name (str): Name of the layer.
        opacity (float): Opacity value (0 to 100).
    Returns:
        str: Confirmation message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    
    layer = doc.ArtLayers[layer_name]
    layer.Opacity = opacity
    return f"Layer '{layer_name}' opacity set to {opacity}%."

@mcp.tool()
def set_text_position(layer_name: str, x: float, y: float) -> str:
    """
    Set the position of a text layer.
    args:
        layer_name (str): Name of the text layer
        x (float): X coordinate for the text position
        y (float): Y coordinate for the text position
    Returns:
        str: Success or error message
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    
    layer = doc.ArtLayers[layer_name]
    if layer.Kind == 2:
        layer.TextItem.Position = [x, y]
        return f"Position set to ({x}, {y})"
    return "Layer is not a text layer"

@mcp.tool()
def apply_gaussian_blur_to_layer(layer_name: str, radius: float = 5.0) -> str:
    """
    Apply Gaussian blur to the specified layer.
    Args:
        layer_name (str): Name of the layer to apply the blur to.
        radius (float): Radius of the Gaussian blur.
    Returns:
        str: Confirmation message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    
    try:
        layer = doc.ArtLayers[layer_name]
        layer.ApplyGaussianBlur(radius)
        return f"Applied Gaussian blur to '{layer_name}' with radius {radius}"
    except Exception as e:
        return f"Error: {e}"
    
@mcp.tool()
def adjust_layer_brightness_contrast(layer_name: str, brightness: int, contrast: int) -> str:
    """
    Adjust brightness and contrast of the specified layer.
    Brightness and contrast should be between -100 to 100.

    Args:
        layer_name (str): Name of the layer to adjust.
        brightness (int): Brightness adjustment value.
        contrast (int): Contrast adjustment value.
    Returns:
        str: Confirmation message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    
    try:
        layer = doc.ArtLayers[layer_name]
        layer.AdjustBrightnessContrast(brightness, contrast)
        return f"Adjusted brightness/contrast of '{layer_name}' by ({brightness}, {contrast})"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def adjust_layer_hue_saturation(layer_name: str, hue: int = 0, saturation: int = 0, lightness: int = 0) -> str:
    """
    Adjust hue, saturation, and lightness of the specified layer.
    All values should range from -100 to 100.
    
    Args:
        layer_name (str): Name of the layer to adjust.
        hue (int): Hue adjustment value.
        saturation (int): Saturation adjustment value.
        lightness (int): Lightness adjustment value.
    Returns:
        str: Confirmation message.

    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    
    try:
        layer = doc.ArtLayers[layer_name]
        layer.AdjustHueSaturation(hue, saturation, lightness)
        return f"Adjusted Hue/Saturation/Lightness of '{layer_name}' by ({hue}, {saturation}, {lightness})"
    except Exception as e:
        return f"Error: {e}"
    
@mcp.tool()
def get_active_layer_name() -> str:
    """
    Returns the name of the currently active layer in the document.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]
    
    try:
        return doc.ActiveLayer.Name
    except Exception:
        return "No active layer or document."
    
@mcp.tool()
def quit_photoshop() -> str:
    """
    Quit Photoshop application.
    """
    try:
        psApp.Quit()
        return "Photoshop quit successfully."
    except Exception as e:
        return f"Error quitting Photoshop: {e}"
    

@mcp.tool()
def create_new_psd(name: str = "Untitled", width: int = 1920, height: int = 1080, resolution: int = 72, mode: str = "RGB", background_color: str = "white") -> str:
    """
    Create a new Photoshop document.
    
    Args:
        name (str): Name of the document.
        width (int): Width in pixels.
        height (int): Height in pixels.
        resolution (int): Resolution in pixels/inch.
        mode (str): Color mode - options are 'RGB', 'CMYK', 'Grayscale'.
        background_color (str): Background color - 'white', 'black', or 'transparent'.
    
    Returns:
        str: Confirmation message with document name.
    """
    global doc
    if not psApp:
        return "Photoshop not initialized"

    # Map color mode strings to Photoshop constants
    mode_map = {
        "RGB": 2,         # psRGB
        "CMYK": 4,        # psCMYK
        "Grayscale": 1    # psGrayscale
    }
    
    bg_map = {
        "white": 1,       # psWhite
        "black": 2,       # psBlack
        "transparent": 3  # psTransparent
    }

    try:
        doc = psApp.Documents.Add(
            width,
            height,
            resolution,
            name,
            mode_map.get(mode.upper(), 2),
            bg_map.get(background_color.lower(), 1)
        )
        return f"New PSD '{name}' created ({width}x{height}, {resolution}ppi, {mode})"
    except Exception as e:
        return f"Error creating PSD: {e}"

@mcp.tool()
def save_current_psd(filename: str) -> str:
    """
    Save the active Photoshop document to the PSD directory.
    
    Args:
        filename (str): Name to save the PSD as (with or without '.psd').
    
    Returns:
        str: Confirmation message.
    """
    global doc, PSD_DIRECTORY
    if not doc:
        return "No active document to save."

    if not filename.lower().endswith(".psd"):
        filename += ".psd"
    
    save_path = os.path.join(PSD_DIRECTORY, filename)
    
    try:
        psd_options = win32com.client.Dispatch("Photoshop.PhotoshopSaveOptions")
        doc.SaveAs(save_path, psd_options, True)  # asCopy=True to avoid overwrite prompt
        return f"Document saved as {save_path}"
    except Exception as e:
        return f"Failed to save document: {e}"
    


FONT_SPECIFIER_NAME_ID = 1
FONT_SPECIFIER_FAMILY_ID = 16

def shortName(font):
    """Extract Windows Display Name from the font file"""
    name = ""
    family = ""
    for record in font['name'].names:
        try:
            name_str = record.string.decode('utf-16-be') if b'\x00' in record.string else record.string.decode('utf-8')
            if record.nameID == FONT_SPECIFIER_NAME_ID and not name:
                name = name_str
            elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family:
                family = name_str
        except Exception:
            continue
        if name and family:
            break
    return name, family

def getPostScriptNameFromDisplayName(winName):
    """Find PostScript name from display name using Photoshop font list"""
    for font in psApp.fonts:
        if font.name == winName:
            return font.postScriptName
    return None

@mcp.tool()
def create_text_layer(layer_name: str, content: str, font: str = "Arial", size: int = 36) -> str:
    """
    Create a new text layer with specified content, font, and size using PostScript font name.
    Args:
        layer_name (str): Name of the new text layer.
        content (str): Text content for the layer.
        font (str): Font name to use (default is "Arial").
        size (int): Font size (default is 36).
    Returns:
        str: Confirmation message.
    """
    doc = get_active_document()
    if not doc:
        return "No active document found."

    try:
        ps_name = getPostScriptNameFromDisplayName(font)
        if not ps_name:
            return f"Font '{font}' not found in Photoshop. Please check the font name."

        text_layer = doc.ArtLayers.Add()
        text_layer.Name = layer_name
        text_layer.Kind = 2  # Text layer
        text_item = text_layer.TextItem
        text_item.Contents = content
        text_item.Font = ps_name
        text_item.Size = size
        return f"Text layer '{layer_name}' with content '{content}' created using font '{font}'."
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def toggle_text_style_by_name(layer_name: str, style: str = "bold") -> str:
    """
    Toggle text style (bold, unbold, italic) for a specified text layer.

    Args:
        layer_name (str): The name of the text layer.
        style (str): "bold", "unbold", or "italic".

    Returns:
        str: Success or error message.
    """
    doc = get_active_document()
    if not doc:
        return "No active document found."

    try:
        target_layer = None
        for layer in doc.Layers:
            if layer.Name == layer_name:
                target_layer = layer
                break

        if not target_layer:
            return f"Layer '{layer_name}' not found."
        if target_layer.Kind != 2:
            return f"Layer '{layer_name}' is not a text layer."

        text_item = target_layer.TextItem

        if style.lower() == "bold":
            text_item.FauxBold = True
            return f"Bold enabled on '{layer_name}'."
        elif style.lower() == "unbold":
            text_item.FauxBold = False
            return f"Bold disabled on '{layer_name}'."
        elif style.lower() == "italic":
            text_item.FauxItalic = not text_item.FauxItalic
            return f"Italic toggled to {text_item.FauxItalic} on '{layer_name}'."
        else:
            return f"Invalid style option: {style}"

    except Exception as e:
        return f"Error updating text style: {e}"

@mcp.tool()
def list_available_fonts() -> list[str]:
    """
    List available font names that can be used in Photoshop (Windows only).
    """
    try:
        fso = win32com.client.Dispatch("Scripting.FileSystemObject")
        shell = win32com.client.Dispatch("Shell.Application")
        fonts_folder = shell.Namespace(0x14)  # Fonts directory

        fonts = set()
        for item in fonts_folder.Items():
            font_name = item.Name
            if font_name:
                fonts.add(font_name.split(' (')[0])  # Clean names like "Arial (TrueType)"
        return sorted(list(fonts))
    except Exception as e:
        return [f"Error fetching fonts: {e}"]
    
@mcp.tool()
def test_font_compatibility(font_name: str, text: str = "Test", size: int = 36) -> str:
    """
    Test if a given font name is compatible with Photoshop scripting.
    Creates a temporary text layer and checks if the font is applied.
    Args:
        font_name (str): Name of the font to test.
        text (str): Sample text to apply (default is "Test").
        size (int): Font size (default is 36).
    Returns:
        str: Confirmation message indicating compatibility.
    """
    doc = get_active_document()
    if not doc:
        return "No active document found."

    try:
        # Create a temporary text layer
        temp_layer = doc.ArtLayers.Add()
        temp_layer.Kind = 2  # Text layer
        temp_layer.Name = "TempFontTest"
        text_item = temp_layer.TextItem
        text_item.Contents = text
        text_item.Font = font_name
        text_item.Size = size

        # Confirm the applied font
        applied_font = text_item.Font

        # Clean up
        temp_layer.Delete()

        if applied_font == font_name:
            return f"✅ Font '{font_name}' is compatible."
        else:
            return f"⚠️ Font '{font_name}' is not applied as expected. Photoshop used '{applied_font}' instead."

    except Exception as e:
        return f"❌ Error: {e}"
    
@mcp.tool()
def add_image_layer(image_path: str, layer_name: str = "Imported Image") -> str:
    """
    Add an external image as a new layer to the active document and move it to the top.
    Args:
        image_path (str): Path to the image file to import.
        layer_name (str): Name for the new layer (default is "Imported Image").
    Returns:
        str: Confirmation message.
    """
    doc = get_active_document()
    if not doc:
        return "No active document found."

    if not os.path.exists(image_path):
        return f"Image file not found: {image_path}"

    try:
        # Capture existing layer names
        existing_layer_names = [layer.Name for layer in doc.ArtLayers]

        # Open external image
        imported_doc = psApp.Open(image_path)

        # Duplicate the layer into the active document (position doesn't matter yet)
        imported_doc.ArtLayers[0].Duplicate(doc)

        # Close the imported document
        imported_doc.Close(2)  # 2 = Don't Save

        # Find the new layer
        new_layer = None
        for layer in doc.ArtLayers:
            if layer.Name not in existing_layer_names:
                new_layer = layer
                break

        if not new_layer:
            return "Layer duplicated, but new layer not found."

        # Rename the new layer
        new_layer.Name = layer_name

        # Move it to the top (before the first layer)
        first_layer = doc.ArtLayers.Item(0)
        if new_layer != first_layer:
            new_layer.Move(first_layer, 2)  # 2 = before

        return f"Image '{image_path}' added as layer '{layer_name}' and moved to top."

    except Exception as e:
        return f"Failed to add image layer: {e}"

@mcp.tool()
def list_image_assets() -> list:
    """
    List full paths of all image files in the global assets directory.

    Returns:
        list: Full file paths of image files (.png, .jpg, .jpeg, etc.).
    """
    if not os.path.isdir(ASSETS_DIR):
        return [f"Assets directory does not exist: {ASSETS_DIR}"]

    supported_exts = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff")
    image_paths = []

    for filename in os.listdir(ASSETS_DIR):
        if filename.lower().endswith(supported_exts):
            full_path = os.path.join(ASSETS_DIR, filename)
            image_paths.append(full_path)

    if not image_paths:
        return ["No image files found in the assets directory."]

    return image_paths

@mcp.tool()
def set_layer_position(layer_name: str, x: float, y: float) -> str:
    """
    Change the X and Y position of a specified layer on the canvas.

    Args:
        layer_name (str): The name of the layer to reposition.
        x (float): New X position.
        y (float): New Y position.

    Returns:
        str: Success or error message.
    """
    doc = get_active_document()
    if not doc:
        return "No active document found."

    try:
        target_layer = None
        for layer in doc.ArtLayers:
            if layer.Name == layer_name:
                target_layer = layer
                break

        if not target_layer:
            return f"Layer '{layer_name}' not found."

        # Translate layer using current position
        bounds = target_layer.Bounds  # [left, top, right, bottom]
        current_x = bounds[0].Value
        current_y = bounds[1].Value
        dx = x - current_x
        dy = y - current_y
        target_layer.Translate(dx, dy)

        return f"Moved layer '{layer_name}' to position ({x}, {y})."

    except Exception as e:
        return f"Failed to move layer '{layer_name}': {e}"


@mcp.tool()
def resize_layer(layer_name: str, scale_x: float, scale_y: float) -> str:
    """
    Resize a specific layer by percentage.

    Args:
        layer_name (str): Name of the layer to resize.
        scale_x (float): Horizontal scale percentage (e.g., 150 for 150%).
        scale_y (float): Vertical scale percentage (e.g., 150 for 150%).

    Returns:
        str: Success or error message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]

    try:
        target_layer = None
        for layer in doc.ArtLayers:
            if layer.Name == layer_name:
                target_layer = layer
                break

        if not target_layer:
            return f"Layer '{layer_name}' not found."

        # Activate target layer
        doc.ActiveLayer = target_layer

        # Resize
        target_layer.Resize(scale_x, scale_y)
        return f"Resized layer '{layer_name}' to {scale_x}% width and {scale_y}% height."
    except Exception as e:
        return f"Error resizing layer: {e}"

@mcp.tool()
def move_layer(layer_name: str, offset_x: float, offset_y: float) -> str:
    """
    Move a specific layer by an (x, y) offset.
    
    Args:
        layer_name (str): Name of the layer to move.
        offset_x (float): Offset in pixels (horizontal).
        offset_y (float): Offset in pixels (vertical).
    
    Returns:
        str: Success or error message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]

    try:
        layer = next(l for l in doc.ArtLayers if l.Name == layer_name)
        doc.ActiveLayer = layer
        layer.Translate(offset_x, offset_y)
        return f"Moved layer '{layer_name}' by ({offset_x}, {offset_y})"
    except StopIteration:
        return f"Layer '{layer_name}' not found."
    except Exception as e:
        return f"Error moving layer: {e}"
    
@mcp.tool()
def rotate_layer(layer_name: str, angle: float) -> str:
    """
    Rotate a specific layer by a given angle (in degrees).
    
    Args:
        layer_name (str): Name of the layer to rotate.
        angle (float): Angle in degrees. Positive = clockwise.
    
    Returns:
        str: Success or error message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]

    try:
        layer = next(l for l in doc.ArtLayers if l.Name == layer_name)
        doc.ActiveLayer = layer
        layer.Rotate(angle)
        return f"Rotated layer '{layer_name}' by {angle} degrees"
    except StopIteration:
        return f"Layer '{layer_name}' not found."
    except Exception as e:
        return f"Error rotating layer: {e}"

@mcp.tool()
def change_blend_mode(layer_name: str, blend_mode: str) -> str:
    """
    Change the blend mode of a layer.

    Args:
        layer_name (str): Name of the layer to modify.
        blend_mode (str): New blend mode (e.g., 'normal', 'multiply', 'screen', etc.)

    Returns:
        str: Success or error message.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]

    blend_modes = {
        "normal": 2,
        "dissolve": 3,
        "darken": 4,
        "multiply": 5,
        "color burn": 6,
        "linear burn": 7,
        "lighten": 8,
        "screen": 9,
        "color dodge": 10,
        "linear dodge": 11,
        "overlay": 12,
        "soft light": 13,
        "hard light": 14,
        "vivid light": 15,
        "linear light": 16,
        "pin light": 17,
        "hard mix": 18,
        "difference": 19,
        "exclusion": 20,
        "hue": 21,
        "saturation": 22,
        "color": 23,
        "luminosity": 24,
        # Add more if supported
    }

    try:
        layer = next(l for l in doc.ArtLayers if l.Name == layer_name)
        doc.ActiveLayer = layer
        mode_key = blend_mode.lower()
        if mode_key not in blend_modes:
            return f"Unsupported blend mode '{blend_mode}'."

        layer.BlendMode = blend_modes[mode_key]
        return f"Blend mode for '{layer_name}' set to '{blend_mode}'"
    except StopIteration:
        return f"Layer '{layer_name}' not found."
    except Exception as e:
        return f"Error changing blend mode: {e}"

import os
import win32com.client

@mcp.tool()
def export_layers_as_png() -> str:
    """
    Export each visible layer in the active document as a separate PNG to the EXPORT_DIR.
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]

    if not psApp or not doc:
        return "Photoshop is not running or no document is open"
    if not EXPORT_DIRECTORY:
        return "EXPORT_DIR not set"

    try:
        original_visibility = {}

        # Iterate over ArtLayers (not including LayerSets for now)
        for i, layer in enumerate(doc.ArtLayers):
            # Save current visibility state
            original_visibility[layer.Name] = layer.Visible

            # Hide all layers
            for l in doc.ArtLayers:
                l.Visible = False

            # Show only this layer
            layer.Visible = True
            doc.ActiveLayer = layer

            # Set up export options
            options = win32com.client.Dispatch('Photoshop.ExportOptionsSaveForWeb')
            options.Format = 13  # PNG
            options.PNG8 = False

            # Export path
            safe_name = "".join(c if c.isalnum() else "_" for c in layer.Name)
            export_path = os.path.join(EXPORT_DIRECTORY, f"{safe_name}.png")
            doc.Export(ExportIn=export_path, ExportAs=2, Options=options)

        # Restore visibility
        for l in doc.ArtLayers:
            if l.Name in original_visibility:
                l.Visible = original_visibility[l.Name]

        return f"Exported {len(doc.ArtLayers)} layers to {EXPORT_DIRECTORY}"
    except Exception as e:
        return f"Error exporting layers: {e}"

@mcp.tool()
def change_canvas_size(width: int, height: int, anchor: int = 9) -> str:
    """
    Change the canvas size of the active document.

    Args:
        width (int): New width in pixels
        height (int): New height in pixels
        anchor (int): Anchor position (1=top left, 9=center, etc.). Default is 9 (center)

    Returns:
        str: Success or error message
    """
    doc = get_active_document()
    if not doc:
        return ["No active document found."]

    try:
        doc.ResizeCanvas(Width=width, Height=height, Anchor=anchor)
        return f"Canvas resized to {width}x{height}."
    except Exception as e:
        return f"Error resizing canvas: {e}"

@mcp.tool()
def apply_posterize(levels: int = 4) -> str:
    """
    Apply Posterize effect to the active layer.

    Args:
        levels (int): Number of tonal levels (2-255). Default is 4.
    """
    doc = get_active_document()
    if not doc:
        return "No active document found."

    try:
        desc = win32com.client.Dispatch("Photoshop.ActionDescriptor")
        desc.PutInteger(psApp.StringIDToTypeID("levels"), levels)

        psApp.ExecuteAction(psApp.StringIDToTypeID("posterize"), desc)
        return f"Posterize applied with {levels} levels."
    except Exception as e:
        return f"Failed to apply posterize: {e}"

@mcp.tool()
def apply_threshold(level: int = 128) -> str:
    """
    Apply Threshold effect to the active layer.

    Args:
        level (int): Threshold level (0–255). Default is 128.
    """
    doc = get_active_document()
    if not doc:
        return "No active document found."

    try:
        desc = win32com.client.Dispatch("Photoshop.ActionDescriptor")
        desc.PutInteger(psApp.StringIDToTypeID("level"), level)

        psApp.ExecuteAction(psApp.StringIDToTypeID("thresholdClassEvent"), desc)
        return f"Threshold applied at level {level}."
    except Exception as e:
        return f"Failed to apply threshold: {e}"


@mcp.tool()
def addition_tool(arg1: int, arg2: int) -> int:
    return arg1 + arg2

if __name__ == "__main__":
    mcp.run(transport="stdio")
