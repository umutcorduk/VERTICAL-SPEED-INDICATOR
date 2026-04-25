import math
import tkinter as tk


MIN_FPM = -6000
MAX_FPM = 6000
PRESET_VALUES = (-3000, -1500, 0, 1500, 3000)

APP_BG = "#0b1220"
PANEL_BG = "#111827"
CARD_BG = "#172033"
GAUGE_BG = "#151515"
TEXT_PRIMARY = "#f8fafc"
TEXT_MUTED = "#94a3b8"
ACCENT = "#ffd166"
BUTTON_BG = "#24324d"
BUTTON_ACTIVE = "#324567"
SUCCESS = "#8ce99a"
ERROR = "#ff8787"
NEUTRAL = "#cbd5e1"


def clamp_value(value: float) -> float:
    return max(float(MIN_FPM), min(float(MAX_FPM), float(value)))


def parse_fpm_input(text):
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("empty input")
    return float(cleaned)


def build_status_message(value):
    return f"Hedef dikey hız {int(round(clamp_value(value)))} FPM olarak ayarlandı."


def format_fpm_value(value):
    return f"{int(round(value))} FPM"


class VSIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vertical Speed Indicator")
        self.root.configure(bg=APP_BG)
        self.root.geometry("1080x680")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        from typing import Optional

        # These are computed dynamically on first canvas render
        self.width: float = 520
        self.height: float = 520
        self.cx: float = self.width / 2
        self.cy: float = self.height / 2
        self.r: float = 210
        self._resize_job: Optional[str] = None

        self.target_val = 0.0
        self.current_val = 0.0
        self._syncing_controls = False

        self.input_var = tk.StringVar(value="0")
        self.scale_var = tk.DoubleVar(value=0.0)
        self.target_display_var = tk.StringVar(value=format_fpm_value(0))
        self.live_display_var = tk.StringVar(value=format_fpm_value(0))
        self.status_var = tk.StringVar(value="Hazir. Yeni hedef dikey hızı seçin.")

        self.needle: Optional[int] = None
        self.center_cap: Optional[int] = None
        # Pre-declared for Pyre2 static analysis (assigned inside build_layout)
        self.canvas: tk.Canvas
        self.input_entry: tk.Entry
        self.scale: tk.Scale
        self.status_label: tk.Label

        self.build_layout()

        # gauge is drawn on first <Configure> event from canvas

        self.apply_value(0, announce=False)
        self.animate()

    def build_layout(self):
        main_frame = tk.Frame(self.root, bg=APP_BG)
        main_frame.pack(fill="both", expand=True, padx=24, pady=24)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(0, weight=1)

        gauge_shell = tk.Frame(main_frame, bg=PANEL_BG, padx=22, pady=22)
        gauge_shell.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

        gauge_title = tk.Label(
            gauge_shell,
            text="Analog Gosterge",
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            font=("Segoe UI Semibold", 18),
        )
        gauge_title.pack(anchor="w")

        gauge_subtitle = tk.Label(
            gauge_shell,
            text="Vertical speed indicator canlı olarak aynı pencere içinde kontrol edilir.",
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            justify="left",
            wraplength=540,
            font=("Segoe UI", 10),
        )
        gauge_subtitle.pack(anchor="w", pady=(4, 18))

        self.canvas = tk.Canvas(
            gauge_shell,
            bg=GAUGE_BG,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        control_shell = tk.Frame(main_frame, bg=PANEL_BG, padx=24, pady=24)
        control_shell.grid(row=0, column=1, sticky="nsew")
        control_shell.grid_columnconfigure(0, weight=1)

        title = tk.Label(
            control_shell,
            text="Kontrol Paneli",
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            font=("Segoe UI Semibold", 22),
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = tk.Label(
            control_shell,
            text="Terminal yerine buradan hedef FPM değerini girin, kaydirin veya hazir degerlerden secin.",
            bg=PANEL_BG,
            fg=TEXT_MUTED,
            justify="left",
            wraplength=340,
            font=("Segoe UI", 10),
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(6, 18))

        summary_card = self.create_card(control_shell)
        summary_card.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        summary_card.grid_columnconfigure(0, weight=1)
        summary_card.grid_columnconfigure(1, weight=1)

        self.build_metric(
            summary_card,
            column=0,
            label="Secili hedef",
            variable=self.target_display_var,
            accent=ACCENT,
        )
        self.build_metric(
            summary_card,
            column=1,
            label="Anlik ibre",
            variable=self.live_display_var,
            accent=SUCCESS,
        )

        input_card = self.create_card(control_shell)
        input_card.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        input_card.grid_columnconfigure(0, weight=1)

        input_label = tk.Label(
            input_card,
            text="Hedef FPM",
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            font=("Segoe UI Semibold", 12),
        )
        input_label.grid(row=0, column=0, sticky="w")

        input_hint = tk.Label(
            input_card,
            text="Gecerli aralik: -6000 ile 6000",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        input_hint.grid(row=1, column=0, sticky="w", pady=(2, 12))

        entry_row = tk.Frame(input_card, bg=CARD_BG)
        entry_row.grid(row=2, column=0, sticky="ew")
        entry_row.grid_columnconfigure(0, weight=1)

        self.input_entry = tk.Entry(
            entry_row,
            textvariable=self.input_var,
            bg=APP_BG,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#324567",
            highlightcolor=ACCENT,
            font=("Segoe UI Semibold", 16),
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", ipady=12, padx=(0, 10))
        self.input_entry.bind("<Return>", self.on_entry_submit)

        apply_button = self.create_button(
            entry_row,
            text="Uygula",
            command=self.on_entry_submit,
            primary=True,
            width=10,
        )
        apply_button.grid(row=0, column=1)

        reset_button = self.create_button(
            input_card,
            text="Sifirla",
            command=self.reset_value,
            primary=False,
            width=12,
        )
        reset_button.grid(row=3, column=0, sticky="w", pady=(12, 0))

        slider_card = self.create_card(control_shell)
        slider_card.grid(row=4, column=0, sticky="ew", pady=(0, 14))
        slider_card.grid_columnconfigure(0, weight=1)

        slider_label = tk.Label(
            slider_card,
            text="Hizli ayar",
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            font=("Segoe UI Semibold", 12),
        )
        slider_label.grid(row=0, column=0, sticky="w")

        slider_hint = tk.Label(
            slider_card,
            text="Kaydirici ibre hedefini aninda degistirir.",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        slider_hint.grid(row=1, column=0, sticky="w", pady=(2, 10))

        self.scale = tk.Scale(
            slider_card,
            from_=MIN_FPM,
            to=MAX_FPM,
            orient=tk.HORIZONTAL,
            resolution=100,
            showvalue=False,
            length=320,
            sliderlength=28,
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            highlightthickness=0,
            troughcolor=APP_BG,
            activebackground=ACCENT,
            variable=self.scale_var,
            command=self.on_scale_change,
        )
        self.scale.grid(row=2, column=0, sticky="ew")

        marker_row = tk.Frame(slider_card, bg=CARD_BG)
        marker_row.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        marker_row.grid_columnconfigure(0, weight=1)
        marker_row.grid_columnconfigure(1, weight=1)
        marker_row.grid_columnconfigure(2, weight=1)

        for index, text in enumerate(("Alcalis", "Duz ucus", "Tirmanis")):
            label = tk.Label(
                marker_row,
                text=text,
                bg=CARD_BG,
                fg=TEXT_MUTED,
                font=("Segoe UI", 9),
            )
            label.grid(row=0, column=index, sticky=("w" if index == 0 else "e" if index == 2 else ""))

        preset_card = self.create_card(control_shell)
        preset_card.grid(row=5, column=0, sticky="ew", pady=(0, 14))
        preset_card.grid_columnconfigure(0, weight=1)
        preset_card.grid_columnconfigure(1, weight=1)
        preset_card.grid_columnconfigure(2, weight=1)
        preset_card.grid_columnconfigure(3, weight=1)
        preset_card.grid_columnconfigure(4, weight=1)

        preset_title = tk.Label(
            preset_card,
            text="Hazir degerler",
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            font=("Segoe UI Semibold", 12),
        )
        preset_title.grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 10))

        for index, value in enumerate(PRESET_VALUES):
            button = self.create_button(
                preset_card,
                text=str(value),
                command=lambda selected=value: self.apply_value(selected),
                primary=False,
                width=8,
            )
            button.grid(row=1, column=index, padx=(0 if index == 0 else 6, 0), sticky="ew")

        status_card = self.create_card(control_shell)
        status_card.grid(row=6, column=0, sticky="ew")

        status_title = tk.Label(
            status_card,
            text="Durum",
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            font=("Segoe UI Semibold", 12),
        )
        status_title.pack(anchor="w")

        self.status_label = tk.Label(
            status_card,
            textvariable=self.status_var,
            bg=CARD_BG,
            fg=NEUTRAL,
            wraplength=330,
            justify="left",
            font=("Segoe UI", 10),
        )
        self.status_label.pack(anchor="w", pady=(8, 0))

    def create_card(self, parent):
        return tk.Frame(parent, bg=CARD_BG, padx=16, pady=16)

    def create_button(self, parent, text, command, primary, width):
        background = ACCENT if primary else BUTTON_BG
        foreground = "#111827" if primary else TEXT_PRIMARY
        active_background = "#f4b942" if primary else BUTTON_ACTIVE

        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            relief="flat",
            bd=0,
            bg=background,
            fg=foreground,
            activebackground=active_background,
            activeforeground=foreground,
            cursor="hand2",
            font=("Segoe UI Semibold", 10),
            padx=12,
            pady=8,
        )

    def build_metric(self, parent, column, label, variable, accent):
        metric_frame = tk.Frame(parent, bg=APP_BG, padx=14, pady=14)
        metric_frame.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 0))

        title = tk.Label(
            metric_frame,
            text=label,
            bg=APP_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        title.pack(anchor="w")

        value_label = tk.Label(
            metric_frame,
            textvariable=variable,
            bg=APP_BG,
            fg=accent,
            font=("Segoe UI Semibold", 18),
        )
        value_label.pack(anchor="w", pady=(8, 0))

    def set_status(self, message, tone):
        color = {"success": SUCCESS, "error": ERROR}.get(tone, NEUTRAL)
        self.status_var.set(message)
        self.status_label.configure(fg=color)

    def apply_value(self, value, announce=True):
        requested_value = float(value)
        clamped_value = clamp_value(requested_value)
        self.target_val = clamped_value
        self.target_display_var.set(format_fpm_value(clamped_value))
        self.sync_controls(clamped_value)

        if announce:
            if clamped_value != requested_value:
                message = f"Girilen deger sinirlandi. {build_status_message(clamped_value)}"
            else:
                message = build_status_message(clamped_value)
            self.set_status(message, "success")

    def sync_controls(self, value):
        rounded_value = int(round(value))
        self._syncing_controls = True
        self.input_var.set(str(rounded_value))
        self.scale_var.set(rounded_value)
        self._syncing_controls = False

    def on_entry_submit(self, event=None):
        try:
            requested_value = parse_fpm_input(self.input_var.get())
        except ValueError:
            self.set_status(
                "Gecerli bir sayi girin. Ornek degerler: -1500, 0, 2400.",
                "error",
            )
            self.input_entry.focus_set()
            self.input_entry.selection_range(0, tk.END)
            return "break"

        self.apply_value(requested_value)
        return "break"

    def on_scale_change(self, value):
        if self._syncing_controls:
            return
        self.apply_value(float(value))

    def reset_value(self):
        self.apply_value(0)
        self.set_status("Gosterge sifirlandi. Hedef dikey hiz 0 FPM.", "success")

    def _on_canvas_resize(self, event):
        """Debounced resize handler — redraws gauge to fit canvas."""
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(60, self._do_resize)

    def _do_resize(self):
        self._resize_job = None
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return
        self.width = w
        self.height = h
        self.cx = w / 2
        self.cy = h / 2
        # Radius: 45% of the smaller dimension, leave margin
        self.r = min(w, h) * 0.45
        self.canvas.delete("all")
        self.draw_gauge()
        # Recreate moving elements on top
        self.needle = self.canvas.create_line(
            self.cx, self.cy, self.cx, self.cy,
            fill=ACCENT, width=max(2, int(self.r * 0.018)),
            capstyle=tk.ROUND,
        )
        self.center_cap = self.canvas.create_oval(
            self.cx - self.r * 0.07, self.cy - self.r * 0.07,
            self.cx + self.r * 0.07, self.cy + self.r * 0.07,
            fill="#2a2a2a", outline="#000000", width=2,
        )
        self.update_needle(self.current_val)

    def val_to_angle(self, value):
        return 180 - clamp_value(value) * 0.03

    def draw_gauge(self):
        r = self.r
        # Scale tick lengths and font sizes with radius
        tick_major = max(12, int(r * 0.12))
        tick_mid   = max(8,  int(r * 0.07))
        tick_minor = max(4,  int(r * 0.04))
        lbl_offset = int(r * 0.26)   # distance from centre to label
        font_num   = max(10, int(r * 0.10))
        font_label = max(8,  int(r * 0.075))

        self.canvas.create_oval(
            self.cx - r - 15,
            self.cy - r - 15,
            self.cx + r + 15,
            self.cy + r + 15,
            fill="#1a1a1a",
            outline="#3a3a3a",
            width=6,
        )

        for value in range(MIN_FPM, MAX_FPM + 1, 100):
            angle = math.radians(self.val_to_angle(value))
            if value % 1000 == 0:
                length = tick_major
                width = max(2, int(r * 0.018))
            elif value % 500 == 0:
                length = tick_mid
                width = max(1, int(r * 0.009))
            else:
                length = tick_minor
                width = 1

            color = "#ffffff"
            if value > 5000 or value < -5000:
                color = "#e63946"

            x1 = self.cx + (r - length) * math.cos(angle)
            y1 = self.cy - (r - length) * math.sin(angle)
            x2 = self.cx + r * math.cos(angle)
            y2 = self.cy - r * math.sin(angle)

            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

            if value % 1000 == 0 and abs(value) not in (0, 3000, 6000):
                number = str(abs(value) // 1000)
                nx = self.cx + (r - lbl_offset) * math.cos(angle)
                ny = self.cy - (r - lbl_offset) * math.sin(angle)
                self.canvas.create_text(
                    nx, ny, text=number, fill="white",
                    font=("Segoe UI Semibold", font_num),
                )

        self.canvas.create_text(
            self.cx + (r - lbl_offset) * math.cos(math.radians(180)),
            self.cy - (r - lbl_offset) * math.sin(math.radians(180)),
            text="0", fill="white",
            font=("Segoe UI Semibold", font_num),
        )
        self.canvas.create_text(
            self.cx + (r - lbl_offset) * math.cos(math.radians(0)),
            self.cy - (r - lbl_offset) * math.sin(math.radians(0)),
            text="6", fill="white",
            font=("Segoe UI Semibold", font_num),
        )

        self.canvas.create_text(
            self.cx, self.cy - r * 0.47,
            text="VERTICAL SPEED", fill="white",
            font=("Segoe UI", font_label),
        )
        self.canvas.create_text(
            self.cx, self.cy + r * 0.47,
            text="FEET/MIN x1000", fill="white",
            font=("Segoe UI", font_label),
        )

        self.canvas.create_arc(
            self.cx - r + 8, self.cy - r + 8,
            self.cx + r - 8, self.cy + r - 8,
            start=330, extent=60,
            style=tk.ARC, outline="#e63946", width=3,
        )

    def update_needle(self, value):
        if self.needle is None:
            return
        angle = math.radians(self.val_to_angle(value))
        tail_len = self.r * 0.19
        head_len = self.r * 0.90
        tail_x = self.cx + tail_len * math.cos(angle + math.pi)
        tail_y = self.cy - tail_len * math.sin(angle + math.pi)
        head_x = self.cx + head_len * math.cos(angle)
        head_y = self.cy - head_len * math.sin(angle)

        assert self.needle is not None
        assert self.center_cap is not None
        self.canvas.coords(self.needle, tail_x, tail_y, head_x, head_y)  # type: ignore[arg-type]
        self.canvas.tag_raise(self.center_cap)  # type: ignore[arg-type]

    def animate(self):
        difference = self.target_val - self.current_val
        if abs(difference) > 2:
            self.current_val += difference * 0.08
        else:
            self.current_val = self.target_val

        self.live_display_var.set(format_fpm_value(self.current_val))
        self.update_needle(self.current_val)
        self.root.after(30, self.animate)


def main():
    root = tk.Tk()
    VSIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
