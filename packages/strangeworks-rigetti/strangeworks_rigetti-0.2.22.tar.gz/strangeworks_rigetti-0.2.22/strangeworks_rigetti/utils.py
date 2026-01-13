import contextlib
import os
import tempfile

import fitz
import matplotlib.pyplot as plt
from PIL import Image
from pyquil.latex import to_latex


def sw_pyquil(p, x, y):

    with contextlib.redirect_stdout(None):
        latex = to_latex(p)

    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "diagram.tex")
        with open(filename, "w") as texfile:
            texfile.write(latex)
            texfile.flush()

        os.system(f"pdflatex -output-directory {tmpdir} {filename} >/dev/null 2>&1")

        your_path = os.path.join(tmpdir, "diagram.pdf")
        doc = fitz.open(your_path)
        MAX_PAGES = 1

        zoom = 1  # to increase the resolution
        mat = fitz.Matrix(zoom * x, zoom * y)

        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # display images
            plt.figure(figsize=(7, 7), facecolor="w")
            plt.xticks(color="white")
            plt.yticks(color="white")
            plt.tick_params(bottom=False)
            plt.tick_params(left=False)

            plt.imshow(img)

            if i > MAX_PAGES - 1:
                break


def plot_histogram(results):
    hist = {}
    for bistlist in results["data"]["ro"]:
        bitstring = ""
        for b in bistlist:
            bitstring += str(b)

        if hist.get(bitstring):
            hist[bitstring] += 1
        else:
            hist[bitstring] = 1

    plt.figure(figsize=(7, 5), facecolor="w")
    plt.hist(hist, rwidth=0.7, color="#CE0074")
    plt.xticks(rotation=90)
    plt.ylabel("Counts")
    plt.xlabel("Measurement")

    plt.show()
