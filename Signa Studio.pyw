"""Prompt-driven emblem generation using a local stable-diffusion.cpp installation."""

import os
import re
import secrets
import subprocess
import sys
import tempfile
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from uuid import uuid4

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageOps, ImageTk


DATA = Path(os.environ["LOCALAPPDATA"]) / "SignaStudio"
BUNDLE = Path(sys.executable).parent if getattr(sys, "frozen", False) else DATA
ROOT = BUNDLE / "references" if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
ENGINE = BUNDLE / "engine" / "sd-cli.exe"
MODEL = BUNDLE / "models" / "sd15.safetensors"
ART = DATA / "artwork"
BG, PAPER, MUTED, INK = "#f3f0e9", "#fffdf9", "#68615a", "#211d1c"
ACCENT = "#663a8c"
STYLE = ("antique wood engraving, black ink and ivory paper illustration, "
         "intricate tapered ink lines and crosshatching, bold silhouette, "
         "single centered subject filling a square app icon, uniform vivid color backdrop")
NEGATIVE = ("photograph, digital painting, 3d render, blurry, gradient, scenery, "
            "words, letters, watermark, border, collage, multiple panels")


def background_color(subject):
    colors = "|".join(sorted(ImageColor.colormap, key=len, reverse=True))
    match = re.search(rf"\b({colors}|#[0-9a-f]{{6}})\s+(?:background|backdrop)\b", subject, re.I)
    if not match:
        match = re.search(rf"\bon\s+(?:an?\s+)?({colors}|#[0-9a-f]{{6}})\b", subject, re.I)
    return ImageColor.getrgb(match[1].lower()) if match else None


def prepare_reference(image, color):
    square = ImageOps.fit(image.convert("RGB"), (512, 512), Image.Resampling.LANCZOS)
    if color is None:
        return square
    # The top corners in the Signa collection usually expose the flat backdrop.
    left, right = (square.getpixel((x, 4)) for x in (4, 507))
    if max(abs(a - b) for a, b in zip(left, right)) > 30:
        return square
    difference = ImageChops.difference(square, Image.new("RGB", square.size, left))
    r, g, b = difference.split()
    mask = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda d: max(0, min(255, (48 - d) * 8)))
    square.paste(color, (0, 0, 512, 512), mask)
    return square


def reference_background(image):
    sample = image.convert("RGB").resize((64, 64))
    # Sample both corners so a tuft of hair or an ear cannot set the palette.
    corners = Image.new("RGB", (16, 8))
    corners.paste(sample.crop((0, 0, 8, 8)))
    corners.paste(sample.crop((56, 0, 64, 8)), (8, 0))
    palette = corners.quantize(colors=4).convert("RGB").getcolors()
    return max(palette)[1]


def finish_engraving(image, background):
    gray = ImageOps.grayscale(image)
    paper = gray.filter(ImageFilter.MedianFilter(3)).point(lambda value: 255 if value >= 192 else 0)
    # Replace light paper connected to the canvas edge. Enclosed highlights
    # such as eyes and scales keep their ivory tone.
    bordered = ImageOps.expand(paper, border=1, fill=255)
    ImageDraw.floodfill(bordered, (0, 0), 128)
    outside = bordered.crop((1, 1, gray.width + 1, gray.height + 1))
    outside = outside.point(lambda value: 255 if value == 128 else 0).filter(ImageFilter.GaussianBlur(0.55))
    ink = ImageOps.colorize(gray, "#100e0c", "#fff7e8")
    ink.paste(background, (0, 0, *ink.size), outside)
    return ink


def preferred_device():
    listing = subprocess.run([str(ENGINE), "--list-devices"], capture_output=True, text=True,
                             errors="replace", creationflags=subprocess.CREATE_NO_WINDOW,
                             timeout=20)
    for line in listing.stdout.splitlines():
        device, _, name = line.partition("\t")
        if device.startswith("Vulkan") and any(vendor in name for vendor in ("NVIDIA", "Radeon RX")):
            return ["--backend", device.lower()]
    return []


def generate_command(subject, reference, target, seed, refine=False):
    negative = NEGATIVE
    prompt = f"{subject}. {STYLE}"
    inputs = []
    if refine:
        inputs = ["-i", str(reference), "--strength", "0.55"]
    else:
        description = subject.strip().rstrip(".")
        if background_color(description):
            description = re.sub(r"\s+(?:on|against|with)\s+(?:an?\s+)?(?:#\w+|\w+)(?:\s+(?:background|backdrop))?$", "", description, flags=re.I)
        composition = "single centered subject"
        if re.search(r"\bhead\s+only\b|\bonly\s+(?:the\s+)?head\b", description, re.I):
            description = re.sub(r"\bonly\b", "", description, flags=re.I).strip()
            composition = "extreme close-up, profile view, tightly cropped at the neck"
            negative += ", full body, torso, shoulders, distant view"
        prompt = (f"({description}:1.35), {composition}. Detailed black ink engraving, "
                  "fine etched lines, strong black shadows, isolated on a plain white background.")
    return [str(ENGINE), "-m", str(MODEL), "-p", prompt, "-n", negative, *inputs,
            "-W", "512", "-H", "512", "--steps", "30", "--cfg-scale", "7",
            "--sampling-method", "dpm++2m", "-s", str(seed), "-o", str(target), *preferred_device()]


def photo(path, side):
    with Image.open(path) as artwork:
        return ImageTk.PhotoImage(ImageOps.contain(artwork.convert("RGB"), (side, side),
                                                   Image.Resampling.LANCZOS))


class Studio:
    def __init__(self, window):
        self.window = window
        window.title("Signa Studio")
        window.configure(bg=BG, padx=22, pady=18)
        self.process = self.job = self.log = None
        self.cancelled = False
        self.current = None
        self.references = {p.stem: p for p in sorted(ROOT.iterdir())
                           if p.suffix.lower() in {".png", ".jpg", ".jpeg"} and p.is_file()}
        self.reference = tk.StringVar(value="Vulpes" if "Vulpes" in self.references
                                      else next(iter(self.references), ""))
        self.status = tk.StringVar(value="Ready to generate locally.")
        self.history = tk.StringVar()
        style = ttk.Style(window)
        style.theme_use("clam")
        style.configure("TButton", padding=(10, 6), font=("Segoe UI", 10))
        style.configure("Generate.TButton", background=ACCENT, foreground="white")
        style.map("Generate.TButton", background=[("active", "#784a9e")])
        header = tk.Frame(window, bg=BG)
        header.pack(fill="x", pady=(0, 14))
        tk.Label(header, text="Signa Studio", font=("Georgia", 26), bg=BG, fg=INK).pack(side="left")
        tk.Label(header, text="Offline icon generator", bg=BG, fg=MUTED).pack(side="right")
        body = tk.Frame(window, bg=BG)
        body.pack(fill="both", expand=True)
        form = tk.Frame(body, bg=PAPER, padx=18, pady=12)
        form.pack(side="left", fill="both", padx=(0, 12))
        result = tk.Frame(body, bg=PAPER, padx=16, pady=12)
        result.pack(side="left", fill="both", expand=True)
        self.label(form, "Style reference")
        selector = ttk.Combobox(form, values=list(self.references), textvariable=self.reference,
                                state="readonly", width=30)
        selector.pack(fill="x")
        self.reference_view = tk.Label(form, bg=PAPER)
        self.reference_view.pack(pady=8)
        selector.bind("<<ComboboxSelected>>", self.show_reference)
        self.show_reference()
        self.label(form, "Subject and background")
        self.prompt = tk.Text(form, height=4, width=32, wrap="word", font=("Segoe UI", 11),
                              bg="#fcfaf5", fg=INK, relief="solid", borderwidth=1, padx=8, pady=6)
        self.prompt.pack(fill="x")
        self.prompt.insert("1.0", "A raven cartographer with a brass compass on a teal background")
        self.generate_btn = ttk.Button(form, text="Generate icon", style="Generate.TButton",
                                       command=self.start)
        self.generate_btn.pack(fill="x", pady=(10, 4))
        self.refine_btn = ttk.Button(form, text="Refine displayed result",
                                     command=lambda: self.start(refine=True))
        self.refine_btn.pack(fill="x")
        self.cancel_btn = ttk.Button(form, text="Cancel generation", command=self.cancel)
        self.cancel_btn.pack(fill="x", pady=4)
        self.label(result, "Generated artwork")
        self.result_view = tk.Label(result, bg="#e7e2d9", fg=MUTED, text="Your generated icon will appear here.")
        self.result_view.pack(fill="both", expand=True)
        self.history_box = ttk.Combobox(result, state="readonly", textvariable=self.history)
        self.history_box.pack(fill="x", pady=8)
        self.history_box.bind("<<ComboboxSelected>>", lambda event: self.display(ART / self.history.get()))
        actions = tk.Frame(result, bg=PAPER)
        actions.pack(fill="x")
        self.export_buttons = []
        for fmt in ("PNG", "ICO"):
            button = ttk.Button(actions, text=f"Export {fmt}", command=lambda f=fmt: self.export(f))
            button.pack(side="left", padx=(0, 6))
            self.export_buttons.append(button)
        self.small = tk.Label(actions, bg=PAPER)
        self.small.pack(side="right")
        tk.Label(window, textvariable=self.status, bg=BG, fg=MUTED, anchor="w").pack(fill="x", pady=(12, 0))
        self.update_history()
        if self.history_box["values"]:
            self.display(ART / self.history_box["values"][0])
        self.controls()
        window.protocol("WM_DELETE_WINDOW", self.close)

    @staticmethod
    def label(parent, title):
        tk.Label(parent, text=title, bg=PAPER, fg=INK, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(2, 6))

    def show_reference(self, event=None):
        path = self.references.get(self.reference.get())
        if path:
            self.thumbnail = photo(path, 148)
            self.reference_view.configure(image=self.thumbnail)

    def controls(self):
        busy = self.process is not None
        self.generate_btn.configure(state="disabled" if busy else "normal")
        self.cancel_btn.configure(state="normal" if busy else "disabled")
        self.refine_btn.configure(state="normal" if self.current and not busy else "disabled")
        for button in self.export_buttons:
            button.configure(state="normal" if self.current else "disabled")

    def start(self, refine=False):
        subject = self.prompt.get("1.0", "end").strip()
        reference = self.current if refine else self.references.get(self.reference.get())
        if self.process:
            return
        if not subject or not reference:
            messagebox.showinfo("Signa Studio", "Choose a reference and describe your icon.")
            return
        if not ENGINE.is_file() or not MODEL.is_file():
            messagebox.showerror("Local engine missing", f"Install the offline engine and model in {BUNDLE}. See the Studio section of README.md.")
            return
        try:
            ART.mkdir(parents=True, exist_ok=True)
            self.job = tempfile.TemporaryDirectory(dir=DATA)
            folder = Path(self.job.name)
            with Image.open(reference) as image:
                color = background_color(subject)
                self.paper_color = None if refine else color or reference_background(image)
                if refine:
                    prepare_reference(image, color).save(folder / "reference.png")
            self.log = (folder / "engine.log").open("wb")
            self.process = subprocess.Popen(generate_command(subject, folder / "reference.png",
                                            folder / "result.png", secrets.randbelow(2**31), refine),
                                            cwd=ENGINE.parent, stdout=self.log, stderr=subprocess.STDOUT,
                                            creationflags=subprocess.CREATE_NO_WINDOW)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            self.cleanup()
            messagebox.showerror("Could not start generation", str(error))
            return
        self.status.set("Generating on this computer…")
        self.controls()
        self.window.after(300, self.poll)

    def poll(self):
        if self.process.poll() is None:
            self.window.after(300, self.poll)
            return
        folder = Path(self.job.name)
        self.log.close()
        try:
            if self.cancelled:
                self.status.set("Generation cancelled.")
            elif self.process.returncode != 0 or not (folder / "result.png").exists():
                log = (folder / "engine.log").read_text(errors="replace")
                raise ValueError(log[-1800:] or "The engine did not produce an image.")
            else:
                with Image.open(folder / "result.png") as image:
                    if self.paper_color is None:
                        image.verify()
                    else:
                        finish_engraving(image, self.paper_color).save(folder / "finished.png")
                if self.paper_color is not None:
                    (folder / "finished.png").replace(folder / "result.png")
                destination = ART / (datetime.now().strftime("%Y-%m-%d %H-%M-%S") + f" {uuid4().hex[:6]}.png")
                (folder / "result.png").replace(destination)
                self.update_history()
                self.display(destination)
                self.status.set("Saved locally. Generate another variation or refine this result.")
        except (OSError, ValueError) as error:
            self.status.set("Generation failed.")
            messagebox.showerror("Generation failed", str(error))
        finally:
            self.cleanup()
            self.controls()

    def cleanup(self):
        if self.log:
            self.log.close()
        if self.job:
            self.job.cleanup()
        self.process = self.job = self.log = None
        self.cancelled = False

    def update_history(self):
        self.history_box.configure(values=sorted((p.name for p in ART.glob("*.png")), reverse=True))

    def display(self, path):
        self.preview = photo(path, 320)
        self.icon_preview = photo(path, 32)
        self.result_view.configure(image=self.preview, text="")
        self.small.configure(image=self.icon_preview)
        self.current = path
        self.history.set(path.name)
        self.controls()

    def export(self, fmt):
        path = filedialog.asksaveasfilename(defaultextension="." + fmt.lower(), initialfile="Signa icon",
                                            filetypes=[(fmt, "*." + fmt.lower())])
        if path:
            try:
                with Image.open(self.current) as image:
                    image.save(path, format=fmt)
                self.status.set(f"Exported {Path(path).name}")
            except OSError as error:
                messagebox.showerror("Export failed", str(error))

    def cancel(self):
        if self.process:
            self.cancelled = True
            self.process.terminate()

    def close(self):
        if self.process:
            self.cancel()
            self.process.wait()
            self.cleanup()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    Studio(root)
    root.mainloop()
