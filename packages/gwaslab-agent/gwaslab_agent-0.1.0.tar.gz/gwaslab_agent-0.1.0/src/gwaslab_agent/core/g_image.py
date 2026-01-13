# --- add at top of module ---
import json, re
from numbers import Number
import numpy as np
import pandas as pd

def _is_figure(obj):
    """Detect Matplotlib figure/axes, Plotly figures, PIL images, or image-like numpy arrays."""
    # Matplotlib figures and axes
    try:
        import matplotlib
        import matplotlib.figure
        import matplotlib.axes
        if isinstance(obj, matplotlib.figure.Figure):
            return True
        if isinstance(obj, matplotlib.axes.Axes):
            return True
        # Sometimes Matplotlib returns a tuple like (fig, ax)
        if isinstance(obj, (list, tuple)) and any(
            isinstance(o, (matplotlib.figure.Figure, matplotlib.axes.Axes)) for o in obj
        ):
            return True
    except ImportError:
        pass
    except Exception:
        pass
    
    # Plotly figures
    try:
        import plotly.graph_objs as go
        if isinstance(obj, go.Figure):
            return True
    except Exception:
        pass
    
    # PIL images
    try:
        from PIL import Image as _PILImage
        if isinstance(obj, _PILImage.Image):
            return True
    except Exception:
        pass
    
    # NumPy arrays that "look like" an image
    if isinstance(obj, np.ndarray) and obj.ndim in (2, 3) and obj.size > 0:
        if obj.ndim == 2 or (obj.ndim == 3 and obj.shape[2] in (1, 3, 4)):
            return True
    return False

def _show_locally(obj):
    """Render fig/image in a Jupyter/IPython notebook (no return)."""
    try:
        from IPython.display import display
        # Matplotlib
        try:
            import matplotlib.figure as _mpl_fig
            import matplotlib.pyplot as plt
            if isinstance(obj, _mpl_fig.Figure):
                # Force a render if the figure has a canvas
                try:
                    if hasattr(obj, 'canvas') and obj.canvas is not None:
                        obj.canvas.draw()
                except Exception:
                    pass
                display(obj)
                plt.close(obj)  # free memory; keeps the displayed output
                return
        except Exception:
            pass
        # Plotly
        try:
            import plotly.graph_objs as go
            if isinstance(obj, go.Figure):
                # display() avoids sending a giant dict to the LLM channel
                display(obj)
                return
        except Exception:
            pass
        # PIL
        try:
            from PIL import Image as _PILImage
            if isinstance(obj, _PILImage.Image):
                display(obj)
                return
        except Exception:
            pass
        # NumPy image-like
        if isinstance(obj, np.ndarray):
            try:
                from PIL import Image as _PILImage
                if obj.ndim == 2:
                    display(_PILImage.fromarray(obj))
                    return
                if obj.ndim == 3 and obj.shape[2] in (1, 3, 4):
                    # Convert single-channel to 2D, others directly
                    if obj.shape[2] == 1:
                        display(_PILImage.fromarray(obj[:, :, 0]))
                    else:
                        display(_PILImage.fromarray(obj))
                    return
            except Exception:
                pass
        # As a last resort, try generic display
        display(obj)
    except Exception:
        # If not in IPython / cannot display, just swallow
        pass

def _scrub_log(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"data:image/[^;]+;base64,[A-Za-z0-9+/=]+", "[image:data-url-redacted]", text)
    text = re.sub(r"[A-Za-z0-9+/]{200,}={0,2}", "[possible-binary-redacted]", text)
    text = re.sub(r"<Figure[^>]*>", "[matplotlib-figure-redacted]", text)
    text = re.sub(r"(?m)^\[USAGE\]\s+This\s+call:\s+prompt=\d+,\s+completion=\d+,\s+total=\d+\s*$", "", text)
    text = re.sub(r"(?m)^\[USAGE\]\s+This\s+\w+:\s+prompt=\d+,\s+completion=\d+,\s+total=\d+\s*$", "", text)
    text = re.sub(r"(?m)^\[USAGE\]\s+Accumulative:\s+prompt=\d+,\s+completion=\d+,\s+total=\d+\s*$", "", text)
    text = re.sub(r"(?m)^\s*\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}\s*", "", text)
    return text.strip()
