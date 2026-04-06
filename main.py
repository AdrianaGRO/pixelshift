import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import os
import sys
import subprocess
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()

# theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

PURPLE       = "#6366F1"   # indigo — calm, professional
PURPLE_HOVER = "#4F46E5"
PURPLE_DIM   = "#2D2B55"
SURFACE      = "#0F0F14"   # near black

CARD         = "#1A1A2E"   # very subtle blue-dark
MUTED        = "#4B5563"
MUTED_HOVER  = "#374151"
TEXT         = "#F1F0FF"
TEXT_SUB     = "#8B8FA8"   # cool gray, barely any purple


class App(ctk.CTk):
    def _show_format_info(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Format Guide")
        dialog.geometry("420x480")
        dialog.resizable(False, False)
        dialog.configure(fg_color=SURFACE)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Which format should I use?",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT
        ).pack(pady=(20, 4), padx=20)

        ctk.CTkLabel(
            dialog, text="A quick guide to help you pick the right format.",
            font=ctk.CTkFont(size=11), text_color=TEXT_SUB
        ).pack(pady=(0, 14), padx=20)

        formats = [
            ("JPEG", "Photos & social media. Small file, slight quality loss."),
            ("PNG",  "Logos & screenshots. Supports transparency, no quality loss."),
            ("WEBP", "Web images. Smaller than JPEG/PNG with great quality."),
            ("HEIC", "iPhone photos. Great quality, small size. Limited compatibility."),
            ("GIF",  "Simple animations. Limited to 256 colors."),
            ("BMP",  "Legacy format. No compression, very large files."),
            ("TIFF", "Print & professional work. Huge files, no quality loss."),
        ]

        for fmt, desc in formats:
            row = ctk.CTkFrame(dialog, fg_color=CARD, corner_radius=8)
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(
                row, text=fmt, width=55,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=PURPLE, anchor="w"
            ).pack(side="left", padx=(12, 4), pady=8)
            ctk.CTkLabel(
                row, text=desc,
                font=ctk.CTkFont(size=12),
                text_color=TEXT_SUB, anchor="w", wraplength=290
            ).pack(side="left", padx=4, pady=8)


        ctk.CTkButton(
            dialog, text="Got it", width=100,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            corner_radius=8, command=dialog.destroy
        ).pack(pady=16)

    def __init__(self):
        super().__init__()
        self.title("PixelShift")
        self.geometry("700x1000")
        self.resizable(False, False)
        self.configure(fg_color=SURFACE)

        # state
        self.selected_files = []
        self.output_folder = "converted_images"
        self.cancel_requested = False

        self._build_ui()

    # ui setup

    def _build_ui(self):

        # header
        header = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="PixelShift",
            font=ctk.CTkFont(family="Helvetica", size=26, weight="bold"),
            text_color=TEXT
        ).pack(side="left", padx=24, pady=18)

        ctk.CTkLabel(
            header,
            text="Bulk Image Converter",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SUB
        ).pack(side="left", pady=18)

        # subtitle
        ctk.CTkLabel(
            self,
            text="Any format in, any format out.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SUB
        ).pack(pady=(0, 24))

        # file selection
        self._section_label("SELECT FILES")

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=(0, 8))

        ctk.CTkButton(
            row, text="+ Add Images", command=self.select_files,
            height=38, width=180,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8
        ).grid(row=0, column=0, padx=6)

        ctk.CTkButton(
            row, text="Clear", command=self.clear_files,
            height=38, width=90,
            fg_color=CARD, hover_color=MUTED,
            border_width=1, border_color=MUTED,
            text_color=TEXT_SUB,
            corner_radius=8
        ).grid(row=0, column=1, padx=6)

        # file list preview
        self.file_list = ctk.CTkScrollableFrame(
            self, width=440, height=120,
            fg_color=CARD, corner_radius=10,
            scrollbar_button_color=PURPLE_DIM,
            scrollbar_button_hover_color=PURPLE
        )
        self.file_list.pack(pady=(0, 12), padx=24)
        self._show_placeholder()

        # output folder
        self._section_label("OUTPUT FOLDER")

        folder_card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)
        folder_card.pack(fill="x", padx=24, pady=(0, 12))

        ctk.CTkButton(
            folder_card, text="Browse", command=self.choose_output_folder,
            height=34, width=90,
            fg_color=PURPLE_DIM, hover_color=PURPLE,
            corner_radius=6,
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, padx=12, pady=10)

        self.folder_label = ctk.CTkLabel(
            folder_card,
            text=f"→  {self.output_folder}",
            text_color=TEXT_SUB,
            font=ctk.CTkFont(size=12),
            wraplength=330, anchor="w"
        )
        self.folder_label.grid(row=0, column=1, padx=4, pady=10, sticky="w")

        # format

        self._section_label("OUTPUT FORMAT")

        # add format guide button
        ctk.CTkButton(
            self, text="? Format Guide", command=self._show_format_info,
            height=24, width=120,
            fg_color="transparent", hover_color=CARD,
            border_width=1, border_color=MUTED,
            text_color=TEXT_SUB,
            font=ctk.CTkFont(size=11),
            corner_radius=6
        ).pack(pady=(0, 8))

        self.format_var = ctk.CTkOptionMenu(
            self, values=["PNG", "JPEG", "BMP", "GIF", "WEBP", "HEIC"],
            command=self._on_format_change,
            fg_color=CARD, button_color=PURPLE, button_hover_color=PURPLE_HOVER,
            dropdown_fg_color=CARD, dropdown_hover_color=PURPLE_DIM,
            text_color=TEXT,
            font=ctk.CTkFont(size=13),
            width=200, height=38,
            corner_radius=8
        )
        self.format_var.pack(pady=(0, 12))

        # jpeg quality slider (hidden until jpeg selected)
        self.quality_frame = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)

        ctk.CTkLabel(
            self.quality_frame,
            text="Quality",
            text_color=TEXT_SUB, font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, padx=14, pady=10)

        self.quality_slider = ctk.CTkSlider(
            self.quality_frame, from_=1, to=100, number_of_steps=99,
            command=self._on_quality_change,
            width=200,
            button_color=PURPLE, button_hover_color=PURPLE_HOVER,
            progress_color=PURPLE_DIM
        )
        self.quality_slider.set(85)
        self.quality_slider.grid(row=0, column=1, padx=6, pady=10)

        self.quality_label = ctk.CTkLabel(
            self.quality_frame, text="85",
            text_color=TEXT, font=ctk.CTkFont(size=13, weight="bold"), width=30
        )
        self.quality_label.grid(row=0, column=2, padx=10, pady=10)

        # resize
        self._section_label("RESIZE")

        resize_card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)
        resize_card.pack(fill="x", padx=24, pady=(0, 12))

        self.resize_var = ctk.CTkCheckBox(
            resize_card, text="Resize images",
            command=self._toggle_resize,
            text_color=TEXT,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            font=ctk.CTkFont(size=13)
        )
        self.resize_var.grid(row=0, column=0, columnspan=4, padx=14, pady=10, sticky="w")

        self.w_label = ctk.CTkLabel(resize_card, text="W", text_color=TEXT_SUB)
        self.w_entry = ctk.CTkEntry(
            resize_card, width=70, placeholder_text="px",
            fg_color=SURFACE, border_color=MUTED, text_color=TEXT,
            corner_radius=6
        )
        self.h_label = ctk.CTkLabel(resize_card, text="H", text_color=TEXT_SUB)
        self.h_entry = ctk.CTkEntry(
            resize_card, width=70, placeholder_text="px",
            fg_color=SURFACE, border_color=MUTED, text_color=TEXT,
            corner_radius=6
        )
        self.aspect_var = ctk.CTkCheckBox(
            resize_card, text="Maintain aspect ratio",
            text_color=TEXT_SUB,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            font=ctk.CTkFont(size=12)
        )
        self.aspect_var.select()

        for w in (self.w_label, self.w_entry, self.h_label, self.h_entry, self.aspect_var):
            w.grid_remove()
            
        #privancy toggle
        
        self.strip_metadata_var = ctk.CTkCheckBox(
            self, text = "Strip GPS & Metadata (Privacy Mode)",
            text_color=TEXT_SUB,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            font=ctk.CTkFont(size=12)
        )
        self.strip_metadata_var.pack(pady=(0, 12))
        self.strip_metadata_var.select() #default is privacy on

        # convert / cancel
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)

        self.convert_btn = ctk.CTkButton(
            btn_row, text="Convert", command=self.start_conversion,
            height=44, width=200,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=10
        )
        self.convert_btn.grid(row=0, column=0, padx=6)

        self.cancel_btn = ctk.CTkButton(
            btn_row, text="Cancel", command=self._request_cancel,
            height=44, width=100,
            fg_color=CARD, hover_color=MUTED,
            border_width=1, border_color=MUTED,
            text_color=TEXT_SUB,
            corner_radius=10
        )
        self.cancel_btn.grid(row=0, column=1, padx=6)
        self.cancel_btn.grid_remove()

        # progress
        self.progress = ctk.CTkProgressBar(
            self, width=440,
            fg_color=CARD,
            progress_color=PURPLE,
            corner_radius=6, height=10
        )
        self.progress.set(0)
        self.progress.pack(pady=(0, 8), padx=24)

        self.status = ctk.CTkLabel(
            self, text="",
            text_color=TEXT_SUB,
            font=ctk.CTkFont(size=12)
        )
        self.status.pack(pady=(0, 20))

    def _section_label(self, text):
        ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=PURPLE,
            anchor="w"
        ).pack(fill="x", padx=28, pady=(12, 4))

    # ui helpers

    def _show_placeholder(self):
        for w in self.file_list.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.file_list, text="No files selected",
            text_color=MUTED, font=ctk.CTkFont(size=12)
        ).pack(pady=10)

    def _refresh_file_list(self):
        for w in self.file_list.winfo_children():
            w.destroy()
        for path in self.selected_files:
            row = ctk.CTkFrame(self.file_list, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=1)

            ctk.CTkLabel(
                row,
                text=os.path.basename(path),
                text_color=TEXT_SUB,
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

            ctk.CTkButton(
                row, text="✕", width=24, height=24,
                fg_color="transparent",
                hover_color=CARD,
                text_color=MUTED,
                font=ctk.CTkFont(size=11),
                corner_radius=4,
                command=lambda p=path, s=self: s._remove_file(p)
            ).pack(side="right")
            
    def _remove_file(self, path):
        self.selected_files.remove(path)
        self._refresh_file_list()

    def _on_format_change(self, choice):
        if choice == "JPEG":
            self.quality_frame.pack(fill="x", padx=24, pady=(0, 12), after=self.format_var)
        else:
            self.quality_frame.pack_forget()

    def _on_quality_change(self, value):
        self.quality_label.configure(text=str(int(value)))

    def _toggle_resize(self):
        if self.resize_var.get():
            self.w_label.grid(row=1, column=0, padx=(14, 4), pady=(0, 10))
            self.w_entry.grid(row=1, column=1, padx=4, pady=(0, 10))
            self.h_label.grid(row=1, column=2, padx=4, pady=(0, 10))
            self.h_entry.grid(row=1, column=3, padx=(4, 14), pady=(0, 10))
            self.aspect_var.grid(row=2, column=0, columnspan=4, padx=14, pady=(0, 10), sticky="w")
        else:
            for w in (self.w_label, self.w_entry, self.h_label, self.h_entry, self.aspect_var):
                w.grid_remove()

    # user actions

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Images", "*.jpeg *.jpg *.png *.bmp *.gif *.heic *.heif *.tiff *.webp")]
        )
        if files:
            # append new files, avoid exact duplicate paths
            existing = set(self.selected_files)
            new_files = [f for f in files if f not in existing]
            self.selected_files += new_files
            self._refresh_file_list()

    def clear_files(self):
        self.selected_files = []
        self._show_placeholder()
        self.progress.set(0)
        self.status.configure(text="")

    def choose_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            display = folder if len(folder) <= 38 else "..." + folder[-35:]
            self.folder_label.configure(text=f"→  {display}")

    def _request_cancel(self):
        self.cancel_requested = True
        self.status.configure(text="Cancelling…")

    def start_conversion(self):
        if not self.selected_files:
            messagebox.showerror("Error", "Please select image files to convert.")
            return
        if self.resize_var.get():
            w, h = self.w_entry.get().strip(), self.h_entry.get().strip()
            if not w and not h:
                messagebox.showerror("Error", "Enter at least a width or height.")
                return
            if (w and not w.isdigit()) or (h and not h.isdigit()):
                messagebox.showerror("Error", "Width and height must be whole numbers.")
                return

        self.cancel_requested = False
        self.convert_btn.configure(state="disabled")
        self.cancel_btn.grid()
        self.progress.set(0)
        self.status.configure(text="")
        threading.Thread(target=self._convert_files, daemon=True).start()

    # conversion (background thread)

    def _convert_files(self):
        total = len(self.selected_files)
        fmt = self.format_var.get()
        quality = int(self.quality_slider.get())
        failed = []
        succeeded = 0
        overwrite_all = None

        os.makedirs(self.output_folder, exist_ok=True)

        for i, path in enumerate(self.selected_files):
            if self.cancel_requested:
                break
            try:
                with Image.open(path) as img:
                    metadata = None if self.strip_metadata_var.get() else img.info.get("exif")
                    
                    img = ImageOps.exif_transpose(img)
                    stem = os.path.basename(path).rsplit(".", 1)[0]

                    if self.resize_var.get():
                        img = self._apply_resize(img)

                    if fmt in ("JPEG", "HEIC") and img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")



                    # build the save path
                    if fmt == "HEIC":
                        save_path = self._unique_path(stem, "heic")
                        save_format = "HEIF"
                    else:
                        save_path = self._unique_path(stem, fmt)
                        save_format = fmt

                    # handle overwrite only if unique_path still finds a conflict
                    if os.path.exists(save_path):
                        if overwrite_all is False:
                            self._update_progress(i, total)
                            continue
                        elif overwrite_all is None:
                            choice = self._ask_overwrite(os.path.basename(save_path))
                            if choice == "skip":
                                self._update_progress(i, total)
                                continue
                            elif choice == "skip_all":
                                overwrite_all = False
                                self._update_progress(i, total)
                                continue
                            elif choice == "overwrite_all":
                                overwrite_all = True


                    if save_format == "JPEG":
                        if metadata:
                            img.save(save_path, save_format, quality=quality, exif=metadata)
                        else:
                            img.save(save_path, save_format, quality=quality)
                        
                    elif fmt == "HEIC":
                        import pillow_heif
                        heif_file = pillow_heif.from_pillow(img)
                        heif_file.save(save_path, quality=quality)
                    else:
                        if metadata:
                            img.save(save_path, save_format, exif=metadata)
                        else:
                            img.save(save_path, save_format)

                    succeeded += 1

            except Exception as e:
                failed.append(os.path.basename(path))
                print(f"Error: {path}: {e}")

            self._update_progress(i, total)

        self.after(0, lambda: self.convert_btn.configure(state="normal"))
        self.after(0, lambda: self.cancel_btn.grid_remove())

        if self.cancel_requested:
            self.after(0, lambda: self.status.configure(
                text=f"Cancelled — {succeeded} file(s) converted."))
        elif failed:
            msg = f"Converted {succeeded} of {total}.\n\nFailed:\n" + \
                  "\n".join(f"• {f}" for f in failed)
            self.after(0, lambda: self.status.configure(
                text=f"{succeeded} succeeded, {len(failed)} failed."))
            self.after(0, lambda: messagebox.showwarning("Completed with errors", msg))
        else:
            self.after(0, lambda: self.status.configure(
                text=f"Done! {succeeded} file(s) converted."))
            self.after(0, lambda: self._show_success(succeeded))

    def _update_progress(self, i, total):
        self.after(0, lambda: self.progress.set((i + 1) / total))
        self.after(0, lambda: self.status.configure(text=f"Converting {i + 1} of {total}…"))

    # helpers

    def _unique_path(self, stem, fmt):
        path = os.path.join(self.output_folder, f"{stem}.{fmt.lower()}")
        counter = 1
        while os.path.exists(path):
            path = os.path.join(self.output_folder, f"{stem}_{counter}.{fmt.lower()}")
            counter += 1
        return path

    def _apply_resize(self, img):
        w = self.w_entry.get().strip()
        h = self.h_entry.get().strip()
        tw = int(w) if w else None
        th = int(h) if h else None
        if self.aspect_var.get():
            img = img.copy()
            img.thumbnail((tw or img.width, th or img.height), Image.LANCZOS)
        else:
            img = img.resize((tw or img.width, th or img.height), Image.LANCZOS)
        return img

    def _ask_overwrite(self, filename):
        result = ctk.StringVar(value="pending")

        def show():
            dialog = ctk.CTkToplevel(self)
            dialog.title("File exists")
            dialog.geometry("400x170")
            dialog.resizable(False, False)
            dialog.configure(fg_color=SURFACE)
            dialog.grab_set()

            ctk.CTkLabel(
                dialog,
                text=f'"{filename}" already exists.',
                text_color=TEXT, font=ctk.CTkFont(size=13),
                wraplength=360
            ).pack(pady=(20, 6))
            ctk.CTkLabel(
                dialog, text="What would you like to do?",
                text_color=TEXT_SUB, font=ctk.CTkFont(size=12)
            ).pack(pady=(0, 12))

            row = ctk.CTkFrame(dialog, fg_color="transparent")
            row.pack()
            for text, val in [("Overwrite", "overwrite"), ("Overwrite All", "overwrite_all"),
                               ("Skip", "skip"), ("Skip All", "skip_all")]:
                is_skip = "Skip" in text
                ctk.CTkButton(
                    row, text=text, width=90,
                    fg_color=CARD if is_skip else PURPLE,
                    hover_color=MUTED if is_skip else PURPLE_HOVER,
                    border_width=1 if is_skip else 0,
                    border_color=MUTED if is_skip else PURPLE,
                    text_color=TEXT_SUB if is_skip else TEXT,
                    corner_radius=7,
                    command=lambda v=val: [result.set(v), dialog.destroy()]
                ).pack(side="left", padx=4)

            self.wait_window(dialog)

        self.after(0, show)
        import time
        start = time.time()
        while result.get() == "pending" and time.time() - start < 60:
            time.sleep(0.05)
        return result.get()

    def _show_success(self, count):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Done")
        dialog.geometry("360x170")
        dialog.resizable(False, False)
        dialog.configure(fg_color=SURFACE)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="✓  Conversion complete!",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PURPLE
        ).pack(pady=(24, 4))

        ctk.CTkLabel(
            dialog,
            text=f"{count} image(s) saved to: {self.output_folder}",
            text_color=TEXT_SUB, font=ctk.CTkFont(size=12),
            wraplength=320
        ).pack(pady=(0, 18))

        row = ctk.CTkFrame(dialog, fg_color="transparent")
        row.pack()

        ctk.CTkButton(
            row, text="Open Folder", width=130,
            fg_color=PURPLE, hover_color=PURPLE_HOVER,
            corner_radius=8,
            command=lambda: [dialog.destroy(), self._open_folder()]
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            row, text="OK", width=80,
            fg_color=CARD, hover_color=MUTED,
            border_width=1, border_color=MUTED,
            text_color=TEXT_SUB,
            corner_radius=8,
            command=dialog.destroy
        ).pack(side="left", padx=8)

    def _open_folder(self):
        folder = os.path.abspath(self.output_folder)
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder])
        else:
            subprocess.run(["xdg-open", folder])


if __name__ == "__main__":
    app = App()
    app.mainloop()
