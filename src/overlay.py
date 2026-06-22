"""Draggable overlay - transparent label/value elements on desktop."""

import tkinter as tk


class OverlayWindow:
    def __init__(self, config_items, update_interval=10):
        self.config_items = config_items
        self.update_interval = update_interval
        self._running = False
        self._widgets = []
        self._after_id = None

        self.root = tk.Tk()
        self.root.title("Overlay")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.configure(bg="black")

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self._build_all()
        self.root.bind("<Escape>", lambda e: self.stop())
        self.root.after(100, self.root.focus_force)
        self.root.bind("<Button-1>", lambda e: self.root.focus_set())

    def _build_all(self):
        for cfg in self.config_items:
            try:
                self._make_part(cfg, "label", cfg.get("label_font_color", "#ffffff"),
                               f"{cfg.get('label', '')}:", cfg.get("label_x", 20), cfg.get("label_y", 20),
                               cfg.get("label_font_name", "Consolas"), cfg.get("label_font_size", 14),
                               cfg.get("show_label", True))
                val = cfg.get("static_override", "")
                self._make_part(cfg, "value", cfg.get("value_font_color", "#00ff00"),
                               val, cfg.get("value_x", 20), cfg.get("value_y", 20),
                               cfg.get("value_font_name", "Consolas"), cfg.get("value_font_size", 14),
                               cfg.get("show_value", True))
            except Exception:
                pass

    def _make_part(self, cfg, part, color, text, x, y, font_name, font_size, visible):
        if not visible or not text:
            return
        try:
            lbl = tk.Label(self.root, text=text, fg=color, bg="black",
                          font=(font_name, font_size), cursor="fleur")
        except Exception:
            lbl = tk.Label(self.root, text=text, fg=color, bg="black",
                          font=("Consolas", 12), cursor="fleur")
        lbl.place(x=x, y=y)
        lbl._cfg = cfg
        lbl._part = part
        self._make_draggable(lbl)
        self._widgets.append(lbl)

    def _make_draggable(self, w):
        def on_start(e):
            w._sx, w._sy = e.x_root, e.y_root
            w._ox, w._oy = w.winfo_x(), w.winfo_y()

        def on_move(e):
            dx, dy = e.x_root - w._sx, e.y_root - w._sy
            nx, ny = w._ox + dx, w._oy + dy
            w.place(x=nx, y=ny)

        w.bind("<ButtonPress-1>", on_start)
        w.bind("<B1-Motion>", on_move)

    def _update_values(self):
        if not self._running:
            return
        try:
            for w in self._widgets:
                if hasattr(w, "_cfg") and w._part == "value":
                    cfg = w._cfg
                    s = cfg.get("static_override", "")
                    w.config(text=s if s else "N/A")
        except Exception:
            pass
        if self._running:
            self._after_id = self.root.after(self.update_interval * 1000, self._update_values)

    def start(self):
        self._running = True
        self._update_values()
        self.root.mainloop()

    def stop(self):
        self._running = False
        if self._after_id:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
        self.root.destroy()
