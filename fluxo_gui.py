import os
import sys
import subprocess
import threading
import shutil
import re
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Configure Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

# ChatGPT Minimal Dark Palette
BG_DARK = "#18181b"          # Deep dark background
SIDEBAR_BG = "#09090b"       # ChatGPT dark sidebar
CARD_BG = "#27272a"          # Minimal card background
CARD_BORDER = "#3f3f46"      # Subtle border
ACCENT_GREEN = "#10a37f"     # ChatGPT Emerald Green
ACCENT_GREEN_HOVER = "#0d8466"
TEXT_PRIMARY = "#f4f4f5"     # Crisp text
TEXT_MUTED = "#a1a1aa"       # Muted text
CONSOLE_BG = "#09090b"

def get_binary_path(name):
    """Finds binary in current directory, alongside exe, or in PATH."""
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    local_path = os.path.join(base_dir, name)
    if os.path.exists(local_path):
        return local_path
    
    # Check parent directory (if running inside dist)
    parent_path = os.path.join(os.path.dirname(base_dir), name)
    if os.path.exists(parent_path):
        return parent_path

    # Check PATH
    found = shutil.which(name)
    if found:
        return found
    return None

def find_ffmpeg():
    return get_binary_path("ffmpeg.exe") or get_binary_path("ffmpeg")

def find_ghostscript():
    gs = get_binary_path("gswin64c.exe") or get_binary_path("gswin64c")
    if not gs:
        gs = get_binary_path("gswin32c.exe") or get_binary_path("gswin32c")
    if not gs:
        gs = get_binary_path("gs.exe") or get_binary_path("gs")
    return gs

def format_size(bytes_val):
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    else:
        return f"{bytes_val / (1024 * 1024):.2f} MB"

def parse_size_to_bytes(size_str):
    s = size_str.strip().upper()
    m_mb = re.match(r"^([\d.]+)\s*MB?$", s)
    if m_mb:
        return int(float(m_mb.group(1)) * 1024 * 1024)
    m_kb = re.match(r"^([\d.]+)\s*KB?$", s)
    if m_kb:
        return int(float(m_kb.group(1)) * 1024)
    m_gb = re.match(r"^([\d.]+)\s*GB?$", s)
    if m_gb:
        return int(float(m_gb.group(1)) * 1024 * 1024 * 1024)
    try:
        # Default to MB if purely numeric
        val = float(s)
        return int(val * 1024 * 1024)
    except ValueError:
        return 0


class FluxoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Fluxo - Media & Document Suite")
        self.geometry("980x680")
        self.minsize(860, 580)
        self.configure(fg_color=BG_DARK)

        # Set Window Icon if available
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_png_path = os.path.join(base_dir, "Assets", "logo.png")
        icon_ico_path = os.path.join(base_dir, "Assets", "logo.ico")
        
        if os.path.exists(icon_ico_path):
            try:
                self.iconbitmap(icon_ico_path)
            except Exception:
                pass
        elif os.path.exists(icon_png_path):
            try:
                from PIL import ImageTk, Image
                img = Image.open(icon_png_path)
                photo = ImageTk.PhotoImage(img)
                self.wm_iconphoto(True, photo)
            except Exception:
                pass

        self.selected_files = []
        self.current_tool = "video_mp4"
        self.is_processing = False

        self.setup_ui()
        self.select_tool("video_mp4")

    def setup_ui(self):
        # Grid Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----------------- SIDEBAR -----------------
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        # App Brand Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="⚡ Fluxo",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(24, 4), sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="Media & Document Suite",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Sidebar Navigation Buttons
        self.tool_buttons = {}
        tools = [
            ("video_mp4", "🎬 Video to MP4"),
            ("video_gif", "🖼️ Video to GIF"),
            ("video_wav", "🎵 Video to WAV"),
            ("image_comp", "🗜️ Image Compressor"),
            ("pdf_comp", "📄 PDF Compressor"),
            ("pdf_to_img", "📑 PDF to Image"),
        ]

        for i, (tool_id, title) in enumerate(tools):
            btn = ctk.CTkButton(
                self.sidebar,
                text=title,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                fg_color="transparent",
                text_color=TEXT_PRIMARY,
                hover_color=CARD_BG,
                height=40,
                corner_radius=8,
                command=lambda tid=tool_id: self.select_tool(tid)
            )
            btn.grid(row=2 + i, column=0, padx=12, pady=4, sticky="ew")
            self.tool_buttons[tool_id] = btn

        # Sidebar Footer
        self.footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.footer_frame.grid(row=9, column=0, padx=16, pady=16, sticky="ew")

        self.status_lbl = ctk.CTkLabel(
            self.footer_frame,
            text="● Engine: Ready",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=ACCENT_GREEN
        )
        self.status_lbl.pack(anchor="w")

        # ----------------- MAIN VIEW -----------------
        self.main_view = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)
        self.main_view.grid_columnconfigure(0, weight=1)
        self.main_view.grid_rowconfigure(3, weight=1)

        # Header Area
        self.header_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="Convert Video to MP4",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.title_lbl.pack(anchor="w")

        self.desc_lbl = ctk.CTkLabel(
            self.header_frame,
            text="Converts source videos to high-compatibility MP4 (H.264 + AAC).",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_MUTED
        )
        self.desc_lbl.pack(anchor="w", pady=(2, 0))

        # File Drop / Select Area Card
        self.drop_card = ctk.CTkFrame(
            self.main_view,
            fg_color=CARD_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=12
        )
        self.drop_card.grid(row=1, column=0, sticky="ew", pady=(0, 16), ipady=12)
        self.drop_card.grid_columnconfigure(0, weight=1)

        self.drop_label = ctk.CTkLabel(
            self.drop_card,
            text="Select file(s) to process. Output will automatically save in the same source folder.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_MUTED
        )
        self.drop_label.grid(row=0, column=0, padx=20, pady=(10, 6))

        self.file_btn_frame = ctk.CTkFrame(self.drop_card, fg_color="transparent")
        self.file_btn_frame.grid(row=1, column=0, pady=(4, 10))

        self.select_files_btn = ctk.CTkButton(
            self.file_btn_frame,
            text="📂 Browse & Select Files",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            height=36,
            corner_radius=8,
            command=self.browse_files
        )
        self.select_files_btn.pack(side="left", padx=6)

        self.clear_files_btn = ctk.CTkButton(
            self.file_btn_frame,
            text="Clear",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#3f3f46",
            hover_color="#52525b",
            height=36,
            width=80,
            corner_radius=8,
            command=self.clear_files
        )
        self.clear_files_btn.pack(side="left", padx=6)

        # Selected Files Display Box
        self.files_box = ctk.CTkTextbox(
            self.drop_card,
            height=70,
            fg_color=BG_DARK,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=TEXT_PRIMARY
        )
        self.files_box.grid(row=2, column=0, padx=16, pady=(4, 4), sticky="ew")
        self.files_box.insert("0.0", "No files selected.")
        self.files_box.configure(state="disabled")

        # ----------------- TOOL CONFIGURATION CARD -----------------
        self.config_card = ctk.CTkFrame(
            self.main_view,
            fg_color=CARD_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=12
        )
        self.config_card.grid(row=2, column=0, sticky="ew", pady=(0, 16), ipady=8)

        # Config widgets containers
        self.setup_tool_configs()

        # ----------------- CONSOLE & ACTIONS -----------------
        self.bottom_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, sticky="nsew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_rowconfigure(1, weight=1)

        self.action_bar = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.action_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.run_btn = ctk.CTkButton(
            self.action_bar,
            text="🚀 Start Processing",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            height=42,
            width=200,
            corner_radius=8,
            command=self.start_processing
        )
        self.run_btn.pack(side="left")

        self.open_folder_btn = ctk.CTkButton(
            self.action_bar,
            text="📁 Open Source Folder",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#3f3f46",
            hover_color="#52525b",
            height=42,
            corner_radius=8,
            command=self.open_source_folder
        )
        self.open_folder_btn.pack(side="left", padx=12)

        self.progress_bar = ctk.CTkProgressBar(
            self.action_bar,
            mode="indeterminate",
            fg_color="#27272a",
            progress_color=ACCENT_GREEN,
            height=10
        )
        # Hidden until running

        # Terminal Console Output
        self.console = ctk.CTkTextbox(
            self.bottom_frame,
            fg_color=CONSOLE_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#22c55e"
        )
        self.console.grid(row=1, column=0, sticky="nsew")
        self.log_message("Fluxo Engine initialized. Minimal ChatGPT Theme loaded.")
        self.log_message("Ready for media conversions. Choose a utility from the sidebar.")

    def setup_tool_configs(self):
        """Creates config inputs for specific utilities."""
        # Generic container
        self.config_frames = {}

        # 1. Video To MP4: Info only
        f_mp4 = ctk.CTkFrame(self.config_card, fg_color="transparent")
        lbl_mp4 = ctk.CTkLabel(f_mp4, text="Settings: Preset = Slow | CRF = 18 | Audio = AAC 192kbps (Optimal quality)", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        lbl_mp4.pack(anchor="w", padx=16, pady=8)
        self.config_frames["video_mp4"] = f_mp4

        # 2. Video To GIF: Two-pass info
        f_gif = ctk.CTkFrame(self.config_card, fg_color="transparent")
        lbl_gif = ctk.CTkLabel(f_gif, text="Settings: Two-pass 256-color palettegen + paletteuse. Preserves FPS & source resolution.", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        lbl_gif.pack(anchor="w", padx=16, pady=8)
        self.config_frames["video_gif"] = f_gif

        # 3. Video To WAV: Audio extraction info
        f_wav = ctk.CTkFrame(self.config_card, fg_color="transparent")
        lbl_wav = ctk.CTkLabel(f_wav, text="Settings: PCM 16-bit stereo WAV | Sample Rate = 44.1 kHz (Studio uncompressed)", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        lbl_wav.pack(anchor="w", padx=16, pady=8)
        self.config_frames["video_wav"] = f_wav

        # 4. Image Compressor: Min KB and Max KB
        f_img = ctk.CTkFrame(self.config_card, fg_color="transparent")
        lbl_img_title = ctk.CTkLabel(f_img, text="Target File Size Range (KB):", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY)
        lbl_img_title.pack(side="left", padx=(16, 12), pady=8)

        lbl_min = ctk.CTkLabel(f_img, text="Min KB:", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        lbl_min.pack(side="left", padx=4)
        self.img_min_entry = ctk.CTkEntry(f_img, width=70, height=32, corner_radius=6, border_color=CARD_BORDER)
        self.img_min_entry.insert(0, "50")
        self.img_min_entry.pack(side="left", padx=(0, 12))

        lbl_max = ctk.CTkLabel(f_img, text="Max KB:", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        lbl_max.pack(side="left", padx=4)
        self.img_max_entry = ctk.CTkEntry(f_img, width=70, height=32, corner_radius=6, border_color=CARD_BORDER)
        self.img_max_entry.insert(0, "150")
        self.img_max_entry.pack(side="left", padx=(0, 14))

        lbl_fmt = ctk.CTkLabel(f_img, text="Format:", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        lbl_fmt.pack(side="left", padx=4)
        self.img_format_menu = ctk.CTkOptionMenu(
            f_img,
            values=["Original Format", "JPG", "PNG", "WebP"],
            width=135,
            height=32,
            corner_radius=6,
            fg_color="#3f3f46",
            button_color=ACCENT_GREEN,
            button_hover_color=ACCENT_GREEN_HOVER
        )
        self.img_format_menu.set("Original Format")
        self.img_format_menu.pack(side="left", padx=(0, 10))

        self.config_frames["image_comp"] = f_img

        # 5. PDF Compressor: Target Max Size (MB or KB)
        f_pdf = ctk.CTkFrame(self.config_card, fg_color="transparent")
        lbl_pdf_title = ctk.CTkLabel(f_pdf, text="Maximum Desired Target Size:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY)
        lbl_pdf_title.pack(side="left", padx=(16, 12), pady=8)

        self.pdf_target_entry = ctk.CTkEntry(f_pdf, width=120, height=32, corner_radius=6, border_color=CARD_BORDER)
        self.pdf_target_entry.insert(0, "2MB")
        self.pdf_target_entry.pack(side="left", padx=(0, 16))

        lbl_pdf_note = ctk.CTkLabel(f_pdf, text="(Examples: 2MB, 500KB, 1.5MB - Multi-tier Ghostscript compression)", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        lbl_pdf_note.pack(side="left", padx=4)
        self.config_frames["pdf_comp"] = f_pdf

        # 6. PDF to Image: Format and DPI
        f_p2i = ctk.CTkFrame(self.config_card, fg_color="transparent")
        lbl_p2i_title = ctk.CTkLabel(f_p2i, text="Output Image Format:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY)
        lbl_p2i_title.pack(side="left", padx=(16, 12), pady=8)

        self.pdf_format_menu = ctk.CTkOptionMenu(
            f_p2i,
            values=["JPG (JPEG)", "PNG (24-bit)", "TIFF (LZW)", "BMP (24-bit)", "SVG (Vector)", "PPM (Raw)"],
            width=140,
            height=32,
            corner_radius=6,
            fg_color="#3f3f46",
            button_color=ACCENT_GREEN,
            button_hover_color=ACCENT_GREEN_HOVER
        )
        self.pdf_format_menu.set("JPG (JPEG)")
        self.pdf_format_menu.pack(side="left", padx=(0, 20))

        lbl_dpi = ctk.CTkLabel(f_p2i, text="Resolution: 300 DPI High-Definition", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        lbl_dpi.pack(side="left", padx=4)
        self.config_frames["pdf_to_img"] = f_p2i

    def select_tool(self, tool_id):
        self.current_tool = tool_id

        # Update sidebar button active state
        for tid, btn in self.tool_buttons.items():
            if tid == tool_id:
                btn.configure(fg_color="#27272a", text_color=ACCENT_GREEN)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY)

        # Update descriptions
        headers = {
            "video_mp4": ("🎬 Convert Video to MP4", "Converts supported video files to MP4 format for high compatibility."),
            "video_gif": ("🖼️ Convert Video to GIF", "Creates animated GIFs using FFmpeg two-pass palette generation preserving FPS."),
            "video_wav": ("🎵 Extract Audio as WAV", "Extracts uncompressed 16-bit PCM WAV audio from any video."),
            "image_comp": ("🗜️ Image Compressor", "Compresses any image (PNG, JPG, WebP, BMP, TIFF, GIF) to fit your exact target KB range."),
            "pdf_comp": ("📄 PDF Compressor", "Compresses PDF documents to fit your specified maximum size (MB/KB)."),
            "pdf_to_img": ("📑 PDF to Image Converter", "Converts PDF document pages into high-resolution 300 DPI images.")
        }
        title, desc = headers.get(tool_id, ("", ""))
        self.title_lbl.configure(text=title)
        self.desc_lbl.configure(text=desc)

        # Show appropriate config frame
        for tid, frame in self.config_frames.items():
            if tid == tool_id:
                frame.pack(fill="x", expand=True)
            else:
                frame.pack_forget()

        self.log_message(f"Switched to: {title}")

    def browse_files(self):
        filetypes = {
            "video_mp4": [("Video Files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v"), ("All Files", "*.*")],
            "video_gif": [("MP4 Video Files", "*.mp4 *.mkv *.mov *.webm"), ("All Files", "*.*")],
            "video_wav": [("Video & Audio Files", "*.mp4 *.mkv *.avi *.mov *.mp3 *.aac *.m4a"), ("All Files", "*.*")],
            "image_comp": [
                ("All Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif *.gif *.ico *.ppm *.tga *.avif"),
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg *.jpeg"),
                ("WebP Images", "*.webp"),
                ("All Files", "*.*")
            ],
            "pdf_comp": [("PDF Documents", "*.pdf"), ("All Files", "*.*")],
            "pdf_to_img": [("PDF Documents", "*.pdf"), ("All Files", "*.*")]
        }

        chosen = filedialog.askopenfilenames(
            title="Select Files for Conversion",
            filetypes=filetypes.get(self.current_tool, [("All Files", "*.*")])
        )

        if chosen:
            self.selected_files = list(chosen)
            self.update_files_display()

    def clear_files(self):
        self.selected_files = []
        self.update_files_display()

    def update_files_display(self):
        self.files_box.configure(state="normal")
        self.files_box.delete("0.0", "end")
        if not self.selected_files:
            self.files_box.insert("0.0", "No files selected.")
        else:
            lines = []
            for idx, f in enumerate(self.selected_files, 1):
                sz = format_size(os.path.getsize(f)) if os.path.exists(f) else "N/A"
                lines.append(f"[{idx}] {os.path.basename(f)} ({sz}) -> Directory: {os.path.dirname(f)}")
            self.files_box.insert("0.0", "\n".join(lines))
        self.files_box.configure(state="disabled")

    def open_source_folder(self):
        if self.selected_files and os.path.exists(self.selected_files[0]):
            folder = os.path.dirname(self.selected_files[0])
            os.startfile(folder)
        else:
            messagebox.showinfo("Source Folder", "Select at least one file to locate its source folder.")

    def log_message(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", f"> {text}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def start_processing(self):
        if self.is_processing:
            return

        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select one or more files to convert.")
            return

        # Verification of binaries
        ffmpeg_bin = find_ffmpeg()
        gs_bin = find_ghostscript()

        if self.current_tool in ["video_mp4", "video_gif", "video_wav", "image_comp"] and not ffmpeg_bin:
            messagebox.showerror("FFmpeg Missing", "FFmpeg was not found in system PATH or application directory.\nPlease install FFmpeg.")
            return

        if self.current_tool in ["pdf_comp", "pdf_to_img"] and not gs_bin:
            messagebox.showerror("Ghostscript Missing", "Ghostscript (gswin64c.exe) was not found in system PATH or application directory.\nPlease install Ghostscript.")
            return

        self.is_processing = True
        self.run_btn.configure(state="disabled", text="Processing...")
        self.progress_bar.pack(side="left", padx=16, fill="x", expand=True)
        self.progress_bar.start()

        thread = threading.Thread(target=self.run_worker, daemon=True)
        thread.start()

    def run_worker(self):
        try:
            total = len(self.selected_files)
            self.log_message(f"Starting job: {total} file(s) queued for {self.current_tool.upper()}...")

            for i, file_path in enumerate(self.selected_files, 1):
                self.log_message(f"----------------------------------------")
                self.log_message(f"Processing ({i}/{total}): {os.path.basename(file_path)}")

                if self.current_tool == "video_mp4":
                    self.process_video_to_mp4(file_path)
                elif self.current_tool == "video_gif":
                    self.process_video_to_gif(file_path)
                elif self.current_tool == "video_wav":
                    self.process_video_to_wav(file_path)
                elif self.current_tool == "image_comp":
                    self.process_image_compress(file_path)
                elif self.current_tool == "pdf_comp":
                    self.process_pdf_compress(file_path)
                elif self.current_tool == "pdf_to_img":
                    self.process_pdf_to_image(file_path)

            self.log_message("========================================")
            self.log_message("All tasks completed successfully!")
            self.log_message("All converted files are stored in the respective source folder.")
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
        finally:
            self.is_processing = False
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.run_btn.configure(state="normal", text="🚀 Start Processing")

    # ================= CONVERSION IMPLEMENTATIONS =================

    def process_video_to_mp4(self, input_file):
        ffmpeg = find_ffmpeg()
        folder = os.path.dirname(input_file)
        name = Path(input_file).stem
        output = os.path.join(folder, f"{name}.mp4")

        # Avoid overwriting identical input
        if output.lower() == input_file.lower():
            output = os.path.join(folder, f"{name}_converted.mp4")

        cmd = [
            ffmpeg, "-y", "-i", input_file,
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            output
        ]
        self.log_message("Executing FFmpeg MP4 encoding...")
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        if proc.returncode == 0:
            sz = format_size(os.path.getsize(output))
            self.log_message(f"SUCCESS: Saved -> {os.path.basename(output)} ({sz})")
        else:
            self.log_message(f"FAILED: {proc.stderr[:300]}")

    def process_video_to_gif(self, input_file):
        ffmpeg = find_ffmpeg()
        folder = os.path.dirname(input_file)
        name = Path(input_file).stem
        output = os.path.join(folder, f"{name}.gif")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_palette:
            palette_path = tmp_palette.name

        try:
            # Pass 1: Palettegen
            self.log_message("Pass 1/2: Analyzing color palette...")
            cmd1 = [
                ffmpeg, "-y", "-i", input_file,
                "-vf", "palettegen",
                palette_path
            ]
            subprocess.run(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

            # Pass 2: Paletteuse
            self.log_message("Pass 2/2: Rendering high-quality animated GIF...")
            cmd2 = [
                ffmpeg, "-y", "-i", input_file, "-i", palette_path,
                "-filter_complex", "paletteuse",
                output
            ]
            proc = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

            if proc.returncode == 0:
                sz = format_size(os.path.getsize(output))
                self.log_message(f"SUCCESS: Saved -> {os.path.basename(output)} ({sz})")
            else:
                self.log_message("FAILED to create GIF.")
        finally:
            if os.path.exists(palette_path):
                try:
                    os.remove(palette_path)
                except Exception:
                    pass

    def process_video_to_wav(self, input_file):
        ffmpeg = find_ffmpeg()
        folder = os.path.dirname(input_file)
        name = Path(input_file).stem
        output = os.path.join(folder, f"{name}.wav")

        cmd = [
            ffmpeg, "-y", "-i", input_file,
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
            output
        ]
        self.log_message("Extracting 16-bit PCM WAV audio...")
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        if proc.returncode == 0:
            sz = format_size(os.path.getsize(output))
            self.log_message(f"SUCCESS: Saved -> {os.path.basename(output)} ({sz})")
        else:
            self.log_message("FAILED audio extraction.")

    def process_image_compress(self, input_file):
        folder = os.path.dirname(input_file)
        name = Path(input_file).stem
        orig_ext = Path(input_file).suffix.lower()
        if not orig_ext:
            orig_ext = ".jpg"

        format_choice = self.img_format_menu.get()
        if format_choice == "JPG":
            target_ext = ".jpg"
        elif format_choice == "PNG":
            target_ext = ".png"
        elif format_choice == "WebP":
            target_ext = ".webp"
        else:
            target_ext = orig_ext

        output = os.path.join(folder, f"{name}_compressed{target_ext}")

        try:
            min_kb = int(self.img_min_entry.get().strip())
            max_kb = int(self.img_max_entry.get().strip())
        except ValueError:
            self.log_message("ERROR: Invalid Min/Max KB input. Using default 50 - 150 KB.")
            min_kb, max_kb = 50, 150

        min_bytes = min_kb * 1024
        max_bytes = max_kb * 1024

        from PIL import Image, ImageOps

        try:
            orig_img = Image.open(input_file)
            orig_img = ImageOps.exif_transpose(orig_img)
            orig_w, orig_h = orig_img.size
            orig_sz = os.path.getsize(input_file)
            self.log_message(f"Input: {orig_w}x{orig_h} | Format: {orig_img.format or orig_ext[1:].upper()} | Original Size: {format_size(orig_sz)}")
        except Exception as e:
            self.log_message(f"ERROR reading image with Pillow: {e}.")
            orig_img = None
            orig_sz = os.path.getsize(input_file) if os.path.exists(input_file) else 0

        scales = [100, 95, 90, 85, 80, 75, 70, 60, 50, 40, 30]
        qualities = [95, 85, 75, 65, 55, 45, 35, 25, 15]

        found = False
        best_candidate_path = None
        best_candidate_sz = 0

        with tempfile.NamedTemporaryFile(suffix=target_ext, delete=False) as tmp:
            test_path = tmp.name

        try:
            if orig_img is not None:
                for scale in scales:
                    new_w = max(1, int(orig_w * scale / 100))
                    new_h = max(1, int(orig_h * scale / 100))
                    resized = orig_img.resize((new_w, new_h), Image.Resampling.LANCZOS) if scale < 100 else orig_img

                    if target_ext in [".jpg", ".jpeg"]:
                        if resized.mode in ("RGBA", "LA", "P"):
                            bg = Image.new("RGB", resized.size, (255, 255, 255))
                            if resized.mode == "P":
                                resized = resized.convert("RGBA")
                            bg.paste(resized, mask=resized.split()[-1] if "A" in resized.mode else None)
                            save_img = bg
                        else:
                            save_img = resized.convert("RGB")

                        for q in qualities:
                            save_img.save(test_path, format="JPEG", quality=q, optimize=True)
                            sz = os.path.getsize(test_path)
                            self.log_message(f"Scale {scale}% | Quality {q} -> {format_size(sz)}")

                            if min_bytes <= sz <= max_bytes:
                                shutil.copyfile(test_path, output)
                                found = True
                                break
                            elif sz <= max_bytes and sz > best_candidate_sz:
                                best_candidate_sz = sz
                                shutil.copyfile(test_path, output)
                                best_candidate_path = output
                        if found:
                            break

                    elif target_ext == ".png":
                        for colors in [None, 256, 128, 64]:
                            if colors and resized.mode not in ("1", "L"):
                                save_img = resized.quantize(colors=colors, method=Image.Resampling.MEDIANCUT)
                            else:
                                save_img = resized

                            save_img.save(test_path, format="PNG", optimize=True, compress_level=9)
                            sz = os.path.getsize(test_path)
                            self.log_message(f"Scale {scale}% | Colors {colors or 'Full'} -> {format_size(sz)}")

                            if min_bytes <= sz <= max_bytes:
                                shutil.copyfile(test_path, output)
                                found = True
                                break
                            elif sz <= max_bytes and sz > best_candidate_sz:
                                best_candidate_sz = sz
                                shutil.copyfile(test_path, output)
                                best_candidate_path = output
                        if found:
                            break

                    elif target_ext == ".webp":
                        for q in qualities:
                            resized.save(test_path, format="WEBP", quality=q, method=6)
                            sz = os.path.getsize(test_path)
                            self.log_message(f"Scale {scale}% | WebP Quality {q} -> {format_size(sz)}")

                            if min_bytes <= sz <= max_bytes:
                                shutil.copyfile(test_path, output)
                                found = True
                                break
                            elif sz <= max_bytes and sz > best_candidate_sz:
                                best_candidate_sz = sz
                                shutil.copyfile(test_path, output)
                                best_candidate_path = output
                        if found:
                            break

                    else:
                        resized.save(test_path)
                        sz = os.path.getsize(test_path)
                        self.log_message(f"Scale {scale}% -> {format_size(sz)}")
                        if min_bytes <= sz <= max_bytes:
                            shutil.copyfile(test_path, output)
                            found = True
                            break
                        elif sz <= max_bytes and sz > best_candidate_sz:
                            best_candidate_sz = sz
                            shutil.copyfile(test_path, output)
                            best_candidate_path = output

            if found:
                final_sz = os.path.getsize(output)
                reduction = ((orig_sz - final_sz) / orig_sz * 100) if orig_sz else 0
                self.log_message(f"SUCCESS: Target reached! Saved: {output} ({format_size(final_sz)}, -{reduction:.1f}%)")
            elif best_candidate_path and os.path.exists(best_candidate_path):
                final_sz = os.path.getsize(best_candidate_path)
                reduction = ((orig_sz - final_sz) / orig_sz * 100) if orig_sz else 0
                self.log_message(f"SUCCESS (Best Fit): Saved: {best_candidate_path} ({format_size(final_sz)}, -{reduction:.1f}%)")
            else:
                self.log_message(f"WARNING: Could not achieve size <= {max_kb} KB. Consider increasing Max KB.")
        finally:
            if os.path.exists(test_path):
                try:
                    os.remove(test_path)
                except Exception:
                    pass

    def process_pdf_compress(self, input_file):
        gs = find_ghostscript()
        folder = os.path.dirname(input_file)
        name = Path(input_file).stem
        output = os.path.join(folder, f"{name}_compressed.pdf")

        target_str = self.pdf_target_entry.get().strip()
        target_bytes = parse_size_to_bytes(target_str)
        if target_bytes == 0:
            target_bytes = 2 * 1024 * 1024  # default 2MB

        profiles = [
            (180, 90),
            (150, 85),
            (120, 80),
            (100, 75),
            (85, 70),
            (72, 60),
            (60, 50)
        ]

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            test_path = tmp.name

        best_path = None
        try:
            for dpi, jpgq in profiles:
                self.log_message(f"Testing Profile: {dpi} DPI / JPEG Quality {jpgq}...")
                cmd = [
                    gs, "-q", "-dBATCH", "-dNOPAUSE",
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.7",
                    "-dDetectDuplicateImages=true",
                    "-dCompressFonts=true",
                    "-dSubsetFonts=true",
                    "-dColorImageDownsampleType=/Bicubic",
                    f"-dColorImageResolution={dpi}",
                    "-dGrayImageDownsampleType=/Bicubic",
                    f"-dGrayImageResolution={dpi}",
                    "-dMonoImageDownsampleType=/Subsample",
                    "-dMonoImageResolution=180",
                    "-dAutoFilterColorImages=false",
                    "-dColorImageFilter=/DCTEncode",
                    f"-dJPEGQ={jpgq}",
                    "-dAutoFilterGrayImages=false",
                    "-dGrayImageFilter=/DCTEncode",
                    "-dPDFSETTINGS=/default",
                    f"-sOutputFile={test_path}",
                    input_file
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

                if os.path.exists(test_path):
                    sz = os.path.getsize(test_path)
                    self.log_message(f"  Result size: {format_size(sz)}")

                    if sz <= target_bytes:
                        shutil.copyfile(test_path, output)
                        self.log_message(f"SUCCESS: Target reached! Saved: {output} ({format_size(sz)})")
                        best_path = output
                        break

            if not best_path:
                self.log_message(f"Notice: All profiles completed. Output size remained above {target_str}.")
        finally:
            if os.path.exists(test_path):
                try:
                    os.remove(test_path)
                except Exception:
                    pass

    def process_pdf_to_image(self, input_file):
        gs = find_ghostscript()
        folder = os.path.dirname(input_file)
        name = Path(input_file).stem

        choice_map = {
            "JPG (JPEG)": ("jpeg", "jpg", ["-dJPEGQ=100"]),
            "PNG (24-bit)": ("png16m", "png", []),
            "TIFF (LZW)": ("tiff24nc", "tif", ["-sCompression=lzw"]),
            "BMP (24-bit)": ("bmp16m", "bmp", []),
            "SVG (Vector)": ("svg", "svg", []),
            "PPM (Raw)": ("ppmraw", "ppm", [])
        }

        selected_label = self.pdf_format_menu.get()
        device, ext, extra_opts = choice_map.get(selected_label, ("jpeg", "jpg", ["-dJPEGQ=100"]))
        output_pattern = os.path.join(folder, f"{name}_page_%03d.{ext}")

        self.log_message(f"Rendering PDF pages to {selected_label} at 300 DPI...")
        cmd = [
            gs, "-q", "-dBATCH", "-dNOPAUSE", "-dSAFER",
            f"-sDEVICE={device}",
            "-r300"
        ] + extra_opts + [
            f"-sOutputFile={output_pattern}",
            input_file
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

        if proc.returncode == 0:
            self.log_message(f"SUCCESS: Pages converted and saved to: {folder}")
        else:
            self.log_message("FAILED to convert PDF pages.")


if __name__ == "__main__":
    app = FluxoApp()
    app.mainloop()
