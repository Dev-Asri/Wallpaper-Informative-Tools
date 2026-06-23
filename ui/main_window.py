import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import json
from PIL import Image, ImageTk, ImageDraw, ImageFont
import ctypes, os, sys, threading

from src.info_tree import build_tree, flatten_items, InfoItem, auto_align, restore_getters, CATEGORY_SOURCE_MAP
from src.config_manager import ConfigManager
from src.i18n import _, set_lang, get_lang

_FONT_DIR = r"C:\Windows\Fonts"
_FONT_MAP = {
    "Consolas": "consola.ttf",
    "Segoe UI": "segoeui.ttf",
    "Arial": "arial.ttf",
    "Courier New": "cour.ttf",
    "Tahoma": "tahoma.ttf",
    "Verdana": "verdana.ttf",
    "Lucida Console": "lucon.ttf",
}

def _load_font(name, size):
    """Load a font by name, searching Windows Fonts dir. Falls back to Segoe UI then default."""
    for try_name in (name, _FONT_MAP.get(name, name), "Segoe UI", "segoeui.ttf"):
        try:
            if not try_name.lower().endswith(".ttf"):
                fn = _FONT_MAP.get(try_name)
                if fn:
                    return ImageFont.truetype(os.path.join(_FONT_DIR, fn), size, encoding="unic")
            path = os.path.join(_FONT_DIR, try_name) if not os.path.isabs(try_name) else try_name
            return ImageFont.truetype(path, size, encoding="unic")
        except: continue
    try:
        return ImageFont.truetype(os.path.join(_FONT_DIR, "segoeui.ttf"), size, encoding="unic")
    except:
        return ImageFont.load_default()


def _find_icon():
    """Locate app_icon.ico for dev mode and frozen EXE."""
    try:
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for name in ("app_icon.ico", "icon.ico"):
            path = os.path.join(base, name)
            if os.path.isfile(path):
                return path
    except: pass
    return None


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(_("window_title"))
        self.root.state("zoomed")
        self.root.minsize(1200, 700)
        try:
            ico = _find_icon()
            if ico:
                self.root.iconbitmap(ico)
        except: pass
        self._first_map = True

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._init_styles()

        self.C = {"toolbar": "#2d2d2d", "bg": "#1e1e2e", "fg": "#ffffff",
                   "accent": "#7c3aed", "accent2": "#06b6d4", "success": "#10b981",
                   "panel": "#252538", "border": "#3d3d5c"}
        self.root.configure(bg=self.C["bg"])

        self.config_mgr = ConfigManager()

        self._all_data = {}
        self._all_items = []
        self._active_items = []
        self._sel_index = None
        self._sel_item = None
        self._bg_color = "#1e1e2e"
        self._bg_image = ""
        self._bg_type = "color"
        self._scale = 0.25
        self._preview_img = None
        self._drag_item = None
        self._drag_part = None
        self._drag_off_x = 0
        self._drag_off_y = 0
        self._preview_off = (0, 0)
        self._preview_zoom = 1.0
        self._panning = False
        self._pan_start = (0, 0)
        self._pan_off0 = (0, 0)
        self._updating = False
        self._multi_sel = []
        self._multi_init = {}
        self._data_sources = ["network", "hardware", "system"]
        self._startup_refresh = tk.BooleanVar(value=True)
        self._preview_dur_sec = self.config_mgr.get("preview_duration", 5)
        self._row_spacing = self.config_mgr.get("row_spacing", 35)
        self._startup_run_pending = False

        saved_lang = self.config_mgr.load().get("lang", "tr")
        set_lang(saved_lang)
        self._setup_ui()
        if hasattr(self, "_lang_var"):
            self._lang_var.set(saved_lang)
        self._startup()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_styles(self):
        s = self.style
        s.configure("Treeview", rowheight=28, font=("Segoe UI", 9),
                    background="#252538", foreground="#e0e0e0", fieldbackground="#1e1e2e")
        s.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                    background="#2d2d2d", foreground="#ffffff")
        s.map("Treeview", background=[("selected", "#7c3aed")])

    def _setup_ui(self):
        tb = tk.Frame(self.root, bg=self.C["toolbar"], height=44)
        tb.pack(fill=tk.X, side=tk.TOP)
        tb.pack_propagate(False)
        inner = tk.Frame(tb, bg=self.C["toolbar"])
        inner.pack(expand=True, fill=tk.X, padx=10)

        tk.Button(inner, text=_("refresh"), command=self._refresh_data,
                 bg=self.C["accent"], fg="white", font=("Segoe UI", 9, "bold"),
                 relief=tk.FLAT, padx=12, pady=4, cursor="hand2",
                 activebackground=self._lighten(self.C["accent"]),
                 activeforeground="white").pack(side=tk.LEFT, padx=3, pady=4)

        self._source_vars = {}
        for key, lbl in [("network","src_network"), ("hardware","src_hardware"), ("system","src_system"), ("database","src_database")]:
            var = tk.BooleanVar(value=key in self._data_sources)
            self._source_vars[key] = var
            tk.Checkbutton(inner, text=_(lbl), variable=var, bg=self.C["toolbar"], fg="#cccccc",
                          activebackground=self.C["toolbar"], activeforeground="white",
                          selectcolor="#444444", font=("Segoe UI", 9), cursor="hand2",
                          command=self._on_source_toggle).pack(side=tk.LEFT, padx=2, pady=4)

        ttk.Checkbutton(inner, text=_("startup_refresh"), variable=self._startup_refresh,
                        command=self._on_startup_refresh_toggle).pack(side=tk.LEFT, padx=10)

        self._startup_run = tk.BooleanVar(value=self.config_mgr.get("startup_run_enabled", False))
        self._startup_run_dur = tk.StringVar(value=str(self.config_mgr.get("startup_run_duration", 3)))
        def _on_startup_run_toggle():
            self._silent_save()
        ttk.Checkbutton(inner, text=_("startup_run"), variable=self._startup_run,
                        command=_on_startup_run_toggle).pack(side=tk.LEFT, padx=(10, 2))
        sp_sr = tk.Spinbox(inner, from_=1, to=10, textvariable=self._startup_run_dur, width=2,
                           bg="#333333", fg="white", relief=tk.FLAT, buttonbackground="#555555",
                           font=("Segoe UI", 9), justify=tk.CENTER,
                           command=self._silent_save)
        sp_sr.bind("<KeyRelease>", lambda e: self._silent_save())
        sp_sr.pack(side=tk.LEFT, padx=(0, 1))
        tk.Label(inner, text=_("sec"), bg=self.C["toolbar"], fg="#cccccc",
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))

        self._lang_var = tk.StringVar(value=get_lang())
        tk.Label(inner, text="  ", bg=self.C["toolbar"]).pack(side=tk.LEFT)
        for code in ("tr", "en"):
            tk.Radiobutton(inner, text=_("lang_"+code), variable=self._lang_var, value=code,
                           bg=self.C["toolbar"], fg="#cccccc", selectcolor="#444444",
                           activebackground=self.C["toolbar"], activeforeground="white",
                           font=("Segoe UI", 9), cursor="hand2",
                           command=self._on_lang_change).pack(side=tk.LEFT, padx=1, pady=2)

        for text, clr, cmd in [
            (_("help_btn"), "#6b7280", self._open_help),
            (_("bg_color"), self.C["accent2"], self._choose_bg_color),
            (_("bg_image"), self.C["accent2"], self._choose_bg_image),
            (_("apply_wallpaper"), "#ef4444", self._apply_wallpaper),
        ]:
            tk.Button(inner, text=text, command=cmd, bg=clr, fg="white",
                     font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=12, pady=4,
                     cursor="hand2", activebackground=self._lighten(clr),
                     activeforeground="white").pack(side=tk.RIGHT, padx=3, pady=4)

        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # LEFT: Tree
        lf = ttk.LabelFrame(self.main_pane, text=_("available_info"))
        tree_frame = ttk.Frame(lf)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.tree = ttk.Treeview(tree_frame, columns=("deger",), show="tree", height=20)
        self.tree.column("#0", width=180, anchor=tk.W)
        self.tree.column("deger", width=120, anchor=tk.W)
        self.tree.heading("deger", text=_("column_value"))
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self._on_tree_dclick)
        self.main_pane.add(lf, weight=0)

        # CENTER
        cf = ttk.Frame(self.main_pane)

        ag = ttk.LabelFrame(cf, text=_("active_info"))
        ag.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 2))
        ag_top = ttk.Frame(ag)
        ag_top.pack(fill=tk.X, padx=4, pady=2)
        for txt, cmd, w in [(_("remove"), self._remove_selected, 10),
                            (_("move_up"), lambda: self._move_item(-1), 8),
                            (_("move_down"), lambda: self._move_item(1), 8),
                            (_("align"), self._auto_align, 10),
                            (_("clear"), self._clear_all, 10)]:
            ttk.Button(ag_top, text=txt, command=cmd, width=w).pack(side=tk.LEFT, padx=1)

        self.grid = ttk.Treeview(ag, columns=("label","value"), show="headings", height=5, selectmode="browse")
        self.grid.heading("label", text=_("column_label")); self.grid.column("label", width=130, anchor=tk.W, stretch=False)
        self.grid.heading("value", text=_("column_value")); self.grid.column("value", width=130, anchor=tk.W, stretch=False)
        self.grid.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.grid.bind("<<TreeviewSelect>>", self._on_grid_select)

        pf = ttk.LabelFrame(cf, text=_("properties"))
        pf.pack(fill=tk.X, padx=2, pady=(2, 0))
        self._build_props(pf)
        self.main_pane.add(cf, weight=0)

        # RIGHT
        right_outer = ttk.Frame(self.main_pane)

        top_bar = tk.Frame(right_outer, bg=self.C["toolbar"])
        top_bar.pack(fill=tk.X, padx=2, pady=(4, 0))
        row1 = tk.Frame(top_bar, bg=self.C["toolbar"])
        row1.pack(expand=True, fill=tk.X, padx=6, pady=(4, 4))

        tk.Label(row1, text=_("drag_mode"), bg=self.C["toolbar"],
                fg="#cccccc", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4), pady=2)
        self._move_h = tk.BooleanVar(value=True)
        self._move_v = tk.BooleanVar(value=True)
        tk.Checkbutton(row1, text=_("drag_h"), variable=self._move_h,
                      bg=self.C["toolbar"], fg="#cccccc", selectcolor="#444444",
                      activebackground=self.C["toolbar"], activeforeground="white",
                      font=("Segoe UI", 9), cursor="hand2",
                      command=self._on_move_mode_change).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Checkbutton(row1, text=_("drag_v"), variable=self._move_v,
                      bg=self.C["toolbar"], fg="#cccccc", selectcolor="#444444",
                      activebackground=self.C["toolbar"], activeforeground="white",
                      font=("Segoe UI", 9), cursor="hand2",
                      command=self._on_move_mode_change).pack(side=tk.LEFT, padx=2, pady=2)

        tk.Label(row1, text=_("align_btns"), bg=self.C["toolbar"],
                fg="#cccccc", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(8, 2), pady=2)
        for txt, cmd in [("←", self._align_left), ("→", self._align_right),
                         ("↑", self._align_top), ("↓", self._align_bottom)]:
            tk.Button(row1, text=txt, command=cmd, bg="#444444", fg="white",
                     font=("Segoe UI", 8), relief=tk.FLAT, padx=5, pady=1,
                     cursor="hand2", activebackground="#666666",
                     activeforeground="white").pack(side=tk.LEFT, padx=1, pady=2)

        rf = ttk.LabelFrame(right_outer, text=_("preview_frame"))
        rf.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.preview = tk.Canvas(rf, bg="#111111", highlightthickness=0, cursor="crosshair")
        self.preview.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.preview.bind("<Button-1>", self._on_preview_click)
        self.preview.bind("<B1-Motion>", self._on_preview_drag)
        self.preview.bind("<MouseWheel>", self._on_preview_wheel)

        bot_bar = tk.Frame(right_outer, bg=self.C["toolbar"])
        bot_bar.pack(fill=tk.X, padx=2, pady=(0, 4))
        row2 = tk.Frame(bot_bar, bg=self.C["toolbar"])
        row2.pack(expand=True, fill=tk.X, padx=6, pady=4)

        tk.Label(row2, text=_("row_spacing"), bg=self.C["toolbar"],
                fg="#cccccc", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 2), pady=2)
        self._row_spacing_var = tk.StringVar(value=str(self._row_spacing))
        sp_rs = tk.Spinbox(row2, from_=10, to=100, textvariable=self._row_spacing_var, width=3,
                           bg="#333333", fg="white", relief=tk.FLAT, buttonbackground="#555555",
                           font=("Segoe UI", 9), justify=tk.CENTER,
                           command=self._on_row_spacing_change)
        sp_rs.bind("<KeyRelease>", lambda e: self._on_row_spacing_change())
        sp_rs.pack(side=tk.LEFT, padx=(0, 4), pady=2)

        tk.Label(row2, text=_("wait_duration"), bg=self.C["toolbar"],
                fg="#cccccc", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(4, 2), pady=2)
        self._preview_dur_var = tk.StringVar(value=str(self._preview_dur_sec))
        sp = tk.Spinbox(row2, from_=1, to=60, textvariable=self._preview_dur_var, width=3,
                        bg="#333333", fg="white", relief=tk.FLAT, buttonbackground="#555555",
                        font=("Segoe UI", 9), justify=tk.CENTER,
                        command=self._on_preview_dur_change)
        sp.bind("<KeyRelease>", lambda e: self._on_preview_dur_change())
        sp.pack(side=tk.LEFT, padx=(0, 1), pady=2)
        tk.Label(row2, text=_("sec"), bg=self.C["toolbar"], fg="#cccccc",
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4), pady=2)

        tk.Button(row2, text=_("desktop_preview"), command=self._preview_desktop,
                 bg="#f59e0b", fg="white", relief=tk.FLAT,
                 font=("Segoe UI", 9, "bold"), padx=10, cursor="hand2",
                 activebackground=self._lighten("#f59e0b"),
                 activeforeground="white").pack(side=tk.LEFT, padx=4, pady=2)
        tk.Button(row2, text=_("preview"), command=self._show_fullscreen,
                 bg=self.C["accent2"], fg="white", relief=tk.FLAT,
                 font=("Segoe UI", 9, "bold"), padx=10, cursor="hand2",
                 activebackground=self._lighten(self.C["accent2"]),
                 activeforeground="white").pack(side=tk.LEFT, padx=4, pady=2)

        self.main_pane.add(right_outer, weight=1)

        self._sv = tk.StringVar()
        sb_frame = tk.Frame(self.root, bg=self.C["toolbar"])
        sb_frame.pack(fill=tk.X, side=tk.BOTTOM)
        sb = tk.Entry(sb_frame, textvariable=self._sv, bg=self.C["toolbar"],
                      fg="#aaaaaa", font=("Segoe UI", 9), relief=tk.FLAT,
                      state="readonly", readonlybackground=self.C["toolbar"],
                      borderwidth=0, insertwidth=0)
        sb.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)
        tk.Label(sb_frame, text=_("credits"),
                 bg=self.C["toolbar"], fg="#666666", font=("Segoe UI", 8),
                 anchor=tk.E, padx=8).pack(side=tk.RIGHT, ipady=2)

    # ── Properties ──
    def _build_props(self, parent):
        self._pr = {}
        self._pr_sel = tk.StringVar(value=_("selected"))
        ttk.Label(parent, textvariable=self._pr_sel, font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, padx=6, pady=(2, 0))

        nb = ttk.Notebook(parent)
        nb.pack(fill=tk.X, padx=4, pady=4)

        # Etiket tab
        etab = ttk.Frame(nb)
        nb.add(etab, text=_("tab_label"))
        for lbl, attr, vtype in [
            (_("prop_label_name"), "label", "str"),
            (_("prop_font"), "label_font_name", "font"),
            (_("prop_font_size"), "label_font_size", "int"),
            (_("prop_font_color"), "label_font_color", "color"),
            (_("prop_show"), "show_label", "bool"),
        ]:
            self._build_row(etab, lbl, attr, vtype)

        # Değer tab
        dtab = ttk.Frame(nb)
        nb.add(dtab, text=_("tab_value"))
        for lbl, attr, vtype in [
            (_("prop_static_value"), "static_override", "str"),
            (_("prop_font"), "value_font_name", "font"),
            (_("prop_font_size"), "value_font_size", "int"),
            (_("prop_font_color"), "value_font_color", "color"),
            (_("prop_show"), "show_value", "bool"),
        ]:
            self._build_row(dtab, lbl, attr, vtype)

        # Konum tab
        pt = ttk.Frame(nb)
        nb.add(pt, text=_("tab_position"))
        for i, (lbl, key) in enumerate([(_("prop_label_x"),"label_x"),(_("prop_label_y"),"label_y"),
                                         (_("prop_value_x"),"value_x"),(_("prop_value_y"),"value_y")]):
            r, c = i // 2, (i % 2) * 3
            tk.Label(pt, text=lbl, bg=self.C["panel"], fg="#e0e0e0",
                    font=("Segoe UI", 9)).grid(row=r, column=c, sticky=tk.W, padx=(8,2), pady=1)
            var = tk.IntVar(value=20)
            ttk.Spinbox(pt, from_=0, to=5000, textvariable=var, width=7).grid(row=r, column=c+1, sticky=tk.W, pady=1)
            self._pr[key] = var
            var.trace_add("write", lambda *a: self._apply_prop())

    def _build_row(self, parent, lbl, attr, vtype):
        f = tk.Frame(parent, bg=self.C["panel"])
        f.pack(fill=tk.X, padx=4, pady=1)
        f.columnconfigure(1, weight=1)

        tk.Label(f, text=lbl, bg=self.C["panel"], fg="#e0e0e0",
                font=("Segoe UI", 9), width=12, anchor=tk.W).grid(row=0, column=0, padx=4, pady=2)

        k = attr
        color_frame_ref = [None]
        color_btn_ref = [None]

        if vtype == "str":
            var = tk.StringVar()
            w = tk.Entry(f, textvariable=var, bg="#1e1e2e", fg="white",
                       relief=tk.FLAT, insertbackground="white", font=("Segoe UI", 9))
            w.grid(row=0, column=1, sticky=tk.EW, padx=4, pady=2)
            var.trace_add("write", lambda *a: self._apply_prop())
        elif vtype == "font":
            var = tk.StringVar(value="Consolas")
            w = ttk.Combobox(f, textvariable=var, values=["Consolas","Arial","Segoe UI",
                "Courier New","Tahoma","Verdana","Lucida Console"], width=18, state="readonly")
            w.grid(row=0, column=1, sticky=tk.EW, padx=4, pady=2)
            var.trace_add("write", lambda *a: self._apply_prop())
        elif vtype == "int":
            var = tk.IntVar(value=14)
            w = ttk.Spinbox(f, from_=6, to=120, textvariable=var, width=8)
            w.grid(row=0, column=1, sticky=tk.W, padx=4, pady=2)
            var.trace_add("write", lambda *a: self._apply_prop())
        elif vtype == "color":
            var = tk.StringVar(value="#ffffff")
            cf = tk.Frame(f, bg=self.C["panel"])
            cf.grid(row=0, column=1, sticky=tk.W, padx=4, pady=2)
            color_frame_ref[0] = cf
            tk.Entry(cf, textvariable=var, width=10, font=("Consolas", 9),
                    bg="#1e1e2e", fg="white", relief=tk.FLAT,
                    insertbackground="white").pack(side=tk.LEFT)

            def pick(v=var, lbl=lbl):
                c = colorchooser.askcolor(color=v.get(), title=lbl)[1]
                if c: v.set(c); self._apply_prop()
            btn = tk.Button(cf, text="\u2588\u2588", command=pick, bg=var.get(),
                          fg="white", relief=tk.FLAT, width=3, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2)
            color_btn_ref[0] = btn

            def on_color_change(*a, v=var, b=btn):
                try: b.configure(bg=v.get())
                except: pass
                self._apply_prop()
            var.trace_add("write", on_color_change)
        elif vtype == "bool":
            var = tk.BooleanVar(value=True)
            w = ttk.Checkbutton(f, variable=var)
            w.grid(row=0, column=1, sticky=tk.W, padx=4, pady=2)
            var.trace_add("write", lambda *a: self._apply_prop())

        self._pr[k] = var

        def make_all(k2=k, vt=vtype):
            return lambda: self._apply_to_all(k2, vt)
        tk.Button(f, text=_("apply_all"), command=make_all(),
                 bg=self.C["accent2"], fg="white", relief=tk.FLAT,
                 font=("Segoe UI", 8, "bold"), padx=6, cursor="hand2",
                 activebackground=self._lighten(self.C["accent2"]),
                 activeforeground="white").grid(row=0, column=2, padx=4, pady=2)

    # ── Startup ──
    def _startup(self):
        self._status(_("loading"))
        self.root.update_idletasks()
        try:
            st = self.config_mgr.load()
            self._bg_type = st.get("background_type", "color")
            self._bg_color = st.get("background_color", "#1e1e2e")
            self._bg_image = st.get("background_image", "")
            self._data_sources = st.get("data_sources", ["network", "hardware", "system"])
            saved_lang = st.get("lang", "tr")
            set_lang(saved_lang)
            if hasattr(self, "_lang_var"):
                self._lang_var.set(saved_lang)
            self._startup_refresh.set(st.get("startup_refresh", True))
            self._preview_dur_sec = st.get("preview_duration", 5)
            self._row_spacing = st.get("row_spacing", 35)
            if hasattr(self, "_row_spacing_var"):
                self._row_spacing_var.set(str(self._row_spacing))
            if hasattr(self, "_preview_dur_var"):
                self._preview_dur_var.set(str(self._preview_dur_sec))
            if hasattr(self, "_startup_run"):
                self._startup_run.set(st.get("startup_run_enabled", False))
            if hasattr(self, "_startup_run_dur"):
                self._startup_run_dur.set(str(st.get("startup_run_duration", 3)))
            if hasattr(self, "_move_h"):
                self._move_h.set(st.get("move_h", True))
            if hasattr(self, "_move_v"):
                self._move_v.set(st.get("move_v", True))
            if hasattr(self, "_source_vars"):
                for k, var in self._source_vars.items():
                    var.set(k in self._data_sources)

            from src.system_info import _info_cache
            cached = self._load_cached_data()
            _info_cache.update(cached)

            self._tree_cats = build_tree(sources=self._data_sources)
            self._all_items = flatten_items(self._tree_cats)
            for it in self._all_items:
                it.last_value = st.get("last_values", {}).get(it.id, "")
            self._populate_tree(cats=self._tree_cats)

            saved = st.get("items", [])
            if saved:
                for sd in saved:
                    it = InfoItem(sd["id"], sd["label"], sd.get("category",""), sd.get("subcategory",""))
                    for k, v in sd.items():
                        if hasattr(it, k) and k not in ("id","category","subcategory"):
                            setattr(it, k, v)
                    self._active_items.append(it)
                self._active_items = restore_getters(self._active_items, self._all_items)
                self._refresh_grid()
                self._status(_("items_loaded", len(self._active_items)))
            else:
                self._status(_("ready"))
            self.root.update_idletasks()
            self._center_preview()
            self._render_preview()
            if self._startup_run.get():
                self._startup_run_pending = True
                self._startup_refresh.set(True)
                self.root.after(50, self.root.iconify)
            if self._startup_refresh.get():
                self.root.after(200, self._refresh_data)
        except Exception as e:
            self._status(f"Hata: {e}")

    def _do_startup_run(self):
        if not self._active_items:
            self._status(_("no_item_run")); self.root.after(1000, self._on_close); return
        try:
            img = self._compose_wallpaper()
            t = os.path.join(os.environ["TEMP"], "wallpaper_run_temp.bmp")
            img.save(t, "BMP")
            ctypes.windll.user32.SystemParametersInfoW(20, 0, t, 0x01|0x02)
            self._status(_("run_applied", self._startup_run_dur.get()))
            dur_ms = int(float(self._startup_run_dur.get()) * 1000)
            self.root.after(dur_ms, self._check_and_close)
        except Exception as e:
            self._status(_("run_error", e))
            self.root.after(2000, self._check_and_close)

    def _check_and_close(self):
        if self._startup_run.get():
            self._on_close()
        else:
            self._status(_("run_cancelled"))

    def _on_startup_refresh_toggle(self):
        self._silent_save()

    def _on_lang_change(self):
        new_lang = self._lang_var.get()
        if new_lang == get_lang():
            return
        set_lang(new_lang)
        self.config_mgr.set("lang", new_lang)
        self._silent_save()
        saved_active = list(self._active_items)
        saved_sel = self._sel_item
        saved_multi = list(self._multi_sel)
        for w in list(self.root.children.values()):
            w.destroy()
        self._setup_ui()
        cats = build_tree(sources=self._data_sources)
        self._populate_tree(cats=cats)
        all_tree = flatten_items(cats)
        tree_lookup = {it.id: it for it in all_tree}
        for it in saved_active:
            match = tree_lookup.get(it.id)
            if match:
                it.label = match.label
                it.original_label = match.label
                it.category = match.category
                it.subcategory = match.subcategory
        self._active_items = saved_active
        self._multi_sel = saved_multi
        if self._active_items:
            self._refresh_grid()
            if saved_sel and saved_sel in self._active_items:
                idx = self._active_items.index(saved_sel)
                self._select_grid_row(idx)
        self._render_preview()
        self.root.update_idletasks()
        self._status(_("ready"))

    # ── Data (tümünü sorgulama + ağaç) ──
    def _refresh_data(self):
        self._status(_("collecting"))
        self.root.update_idletasks()
        threading.Thread(target=self._do_refresh, daemon=True).start()

    def _do_refresh(self):
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except: pass
        try:
            from src.system_info import clear_info_cache, clear_collector_cache, get_selected_info, _info_cache, ALL_SOURCES
            clear_collector_cache()
            frozen = {}
            for s in ALL_SOURCES:
                if s not in self._data_sources and s in _info_cache:
                    frozen[s] = _info_cache[s]
            clear_info_cache()
            get_selected_info(self._data_sources)
            _info_cache.update(frozen)
            items = flatten_items(build_tree(sources=self._data_sources))
            self.root.after(0, self._on_refresh_done, items)
        except Exception as e:
            self.root.after(0, self._status, f"Hata: {e}")
        finally:
            try: pythoncom.CoUninitialize()
            except: pass

    def _on_refresh_done(self, items):
        self._all_items = items
        self._populate_tree()
        self._active_items = restore_getters(self._active_items, self._all_items)
        self._refresh_grid()
        self._render_preview()
        from src.system_info import _info_cache
        self._save_cached_data(_info_cache)
        errors = {k: v.get("_error","?") for k, v in _info_cache.items() if isinstance(v, dict) and "_error" in v}
        if errors:
            err_msg = "; ".join(f"{k}: {e}" for k, e in errors.items())
            self._status(_("error_header", err_msg))
        else:
            self._status(_("updated", len(self._active_items)))
        if self._startup_run_pending:
            self._startup_run_pending = False
            self._do_startup_run()

    def _get_data_dir(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _save_cached_data(self, cache):
        try:
            _dir = self._get_data_dir()
            with open(os.path.join(_dir, "cached_data.json"), "w", encoding="utf-8") as _f:
                json.dump(cache, _f, indent=2, ensure_ascii=False, default=str)
        except:
            pass

    def _load_cached_data(self):
        try:
            _dir = self._get_data_dir()
            p = os.path.join(_dir, "cached_data.json")
            if os.path.isfile(p):
                with open(p, "r", encoding="utf-8") as _f:
                    return json.load(_f)
        except:
            pass
        return {}

    def _populate_tree(self, cats=None):
        from src.system_info import _info_cache
        if cats is None:
            cats = build_tree(sources=self._data_sources)
        self.tree.delete(*self.tree.get_children())
        for cat in cats:
            cid = f"cat_{id(cat)}"
            self.tree.insert("", "end", iid=cid, text=cat.name, open=True)
            for it in cat.items:
                src = CATEGORY_SOURCE_MAP.get(it.category, "")
                if _info_cache.get(src):
                    v = it.get_value()[:40] if it.get_value() else ""
                elif it.last_value:
                    v = it.last_value[:40]
                else:
                    v = "..."
                self.tree.insert(cid, "end", iid=it.id, text=it.label, values=(v,))

    def _on_tree_dclick(self, event):
        sel = self.tree.selection()
        if not sel: return
        iid = sel[0]
        if iid.startswith("cat_"): return
        for it in self._all_items:
            if it.id == iid:
                if it in self._active_items:
                    self._status(f"'{it.label}' zaten aktif.")
                else:
                    self._add_item(it)
                break

    def _add_item(self, item):
        self._active_items.append(item)
        if self._active_items:
            base_y = self._active_items[0].label_y
            i = len(self._active_items) - 1
            item.label_y = base_y + i * self._row_spacing
            item.value_y = base_y + i * self._row_spacing
        self._refresh_grid(); self._render_preview(); self._silent_save()

    # ── Grid ──
    def _on_grid_select(self, event):
        sel = self.grid.selection()
        if sel:
            idx = self.grid.index(sel[0])
            if 0 <= idx < len(self._active_items):
                self._sel_index = idx
                self._sel_item = self._active_items[idx]
                self._load_props(self._sel_item)

    def _refresh_grid(self):
        self.grid.delete(*self.grid.get_children())
        for it in self._active_items:
            v = self._get_display_val(it)
            self.grid.insert("", "end", values=(it.label, v[:60] if v else ""))

    def _remove_selected(self):
        sel = self.grid.selection()
        if sel:
            idx = self.grid.index(sel[0])
            if 0 <= idx < len(self._active_items):
                del self._active_items[idx]
                self._sel_index = None; self._sel_item = None
                self._pr_sel.set(_("selected"))
                self._refresh_grid(); self._render_preview(); self._silent_save()

    def _clear_all(self):
        self._active_items.clear()
        self._sel_index = None; self._sel_item = None
        self._pr_sel.set(_("selected"))
        self._refresh_grid(); self._render_preview(); self._silent_save()

    def _move_item(self, d):
        sel = self.grid.selection()
        if not sel: return
        idx = self.grid.index(sel[0])
        ni = idx + d
        if ni < 0 or ni >= len(self._active_items): return
        self._active_items[idx], self._active_items[ni] = self._active_items[ni], self._active_items[idx]
        self._refresh_grid(); self._render_preview(); self._silent_save()

    def _auto_align(self):
        if not self._active_items: return
        auto_align(self._active_items, row_height=self._row_spacing)
        self._refresh_grid(); self._render_preview()
        if self._sel_item: self._load_props(self._sel_item)
        self._silent_save(); self._status(_("aligned"))

    # ── Properties ──
    def _load_props(self, item):
        self._pr_sel.set(_("selected_item", item.label))
        self._updating = True
        for k, var in self._pr.items():
            if hasattr(item, k):
                try: var.set(getattr(item, k))
                except: pass
        self._updating = False

    def _apply_prop(self):
        if self._updating or not self._sel_item: return
        it = self._sel_item
        for k, var in self._pr.items():
            if hasattr(it, k):
                try: setattr(it, k, var.get())
                except: pass
        self._refresh_grid(); self._render_preview(); self._silent_save()

    def _apply_to_all(self, key, vtype):
        if not self._sel_item or len(self._active_items) < 2: return
        val = self._pr[key].get()
        for it in self._active_items:
            if hasattr(it, key): setattr(it, key, val)
        self._refresh_grid(); self._render_preview(); self._silent_save()
        self._status(_("applied_all", key, len(self._active_items)))

    # ── Preview ──
    def _center_preview(self):
        cw = self.preview.winfo_width()
        ch = self.preview.winfo_height()
        if cw <= 1: cw = 640
        if ch <= 1: ch = 400
        sw = ctypes.windll.user32.GetSystemMetrics(0)
        sh = ctypes.windll.user32.GetSystemMetrics(1)
        s = min(cw / sw, ch / sh, 0.5) * self._preview_zoom
        pw, ph = int(sw * s), int(sh * s)
        self._preview_off = ((cw - pw) // 2, (ch - ph) // 2)

    def _render_preview(self):
        cw = self.preview.winfo_width()
        ch = self.preview.winfo_height()
        if cw <= 1: cw = 640
        if ch <= 1: ch = 400

        sw = ctypes.windll.user32.GetSystemMetrics(0)
        sh = ctypes.windll.user32.GetSystemMetrics(1)
        s = min(cw / sw, ch / sh, 0.5) * self._preview_zoom
        self._scale = s

        pw, ph = int(sw * s), int(sh * s)
        img = self._create_img(pw, ph)
        self._preview_img = ImageTk.PhotoImage(img)

        self.preview.delete("all")
        ox, oy = self._preview_off
        self.preview.create_image(ox, oy, image=self._preview_img, anchor=tk.NW, tags="bg")

    def _create_img(self, w, h):
        if self._bg_type == "image" and self._bg_image and os.path.isfile(self._bg_image):
            img = Image.open(self._bg_image).convert("RGB").resize((w, h), Image.LANCZOS)
        else:
            try:
                hc = self._bg_color.lstrip("#")
                rgb = tuple(int(hc[i:i+2],16) for i in (0,2,4))
            except: rgb = (30,30,46)
            img = Image.new("RGB", (w, h), rgb)

        draw = ImageDraw.Draw(img)
        s = self._scale
        for it in self._active_items:
            try:
                fsize_label = max(1, int(it.label_font_size*s))
                fsize_value = max(1, int(it.value_font_size*s))
                if it.show_label:
                    lf = _load_font(it.label_font_name, fsize_label)
                    if (it, "label") in self._multi_sel:
                        bb = draw.textbbox((0,0), it.label, font=lf)
                        draw.rectangle((int(it.label_x*s)+bb[0]-2, int(it.label_y*s)+bb[1]-2,
                                        int(it.label_x*s)+bb[2]+2, int(it.label_y*s)+bb[3]+2),
                                       outline=(124,58,237), width=2)
                    lc = it.label_font_color.lstrip("#")
                    lrgb = tuple(int(lc[i:i+2],16) for i in (0,2,4)) if len(lc)==6 else (255,255,255)
                    draw.text((int(it.label_x*s), int(it.label_y*s)), it.label, fill=lrgb, font=lf)
                if it.show_value:
                    vf = _load_font(it.value_font_name, fsize_value)
                    display_val = self._get_display_val(it)
                    if (it, "value") in self._multi_sel:
                        bb = draw.textbbox((0,0), display_val, font=vf)
                        draw.rectangle((int(it.value_x*s)+bb[0]-2, int(it.value_y*s)+bb[1]-2,
                                        int(it.value_x*s)+bb[2]+2, int(it.value_y*s)+bb[3]+2),
                                       outline=(124,58,237), width=2)
                    vc = it.value_font_color.lstrip("#")
                    vrgb = tuple(int(vc[i:i+2],16) for i in (0,2,4)) if len(vc)==6 else (0,255,0)
                    draw.text((int(it.value_x*s), int(it.value_y*s)), display_val, fill=vrgb, font=vf)
            except: continue
        return img

    def _get_display_val(self, it):
        from src.system_info import _info_cache
        from src.info_tree import CATEGORY_SOURCE_MAP
        src = CATEGORY_SOURCE_MAP.get(it.category, "")
        if _info_cache.get(src):
            v = it.get_value()
            if v and v not in ("N/A", "...", ""):
                it.last_value = v
            return v
        if it.static_override:
            return it.static_override
        if it.last_value:
            return it.last_value
        return "..."

    def _hit_test(self, cx, cy):
        for i in range(len(self._active_items)-1, -1, -1):
            it = self._active_items[i]
            if it.show_value and it.value_x-5 <= cx <= it.value_x+300 and it.value_y-5 <= cy <= it.value_y+25:
                return i, it, "value"
            if it.show_label and it.label_x-5 <= cx <= it.label_x+220 and it.label_y-5 <= cy <= it.label_y+25:
                return i, it, "label"
        return -1, None, None

    def _on_preview_click(self, event):
        ox, oy = self._preview_off
        s = self._scale
        if s <= 0: return
        cx, cy = (event.x-ox)/s, (event.y-oy)/s
        self._drag_item = None; self._drag_part = None
        self._panning = False
        hi, hit_item, hit_part = self._hit_test(cx, cy)

        if event.state & 0x0004:  # Ctrl
            if hit_item:
                sel = (hit_item, hit_part)
                if sel in self._multi_sel:
                    self._multi_sel.remove(sel)
                else:
                    self._multi_sel.append(sel)
                self._select_grid_row(hi)
                self._render_preview()
            return

        if hit_item:
            if (hit_item, "label") not in self._multi_sel and (hit_item, "value") not in self._multi_sel:
                self._multi_sel.clear()
            self._drag_item = hit_item
            self._drag_part = hit_part
            bx = hit_item.value_x if hit_part == "value" else hit_item.label_x
            by = hit_item.value_y if hit_part == "value" else hit_item.label_y
            self._drag_off_x = cx - bx
            self._drag_off_y = cy - by
            self._multi_init = {}
            for mit, mpart in self._multi_sel:
                self._multi_init[(mit, mpart)] = {
                    "x": mit.value_x if mpart == "value" else mit.label_x,
                    "y": mit.value_y if mpart == "value" else mit.label_y,
                }
            self._select_grid_row(hi)
            return

        self._multi_sel.clear()
        self._render_preview()
        self._panning = True
        self._pan_start = (event.x, event.y)
        self._pan_off0 = self._preview_off

    def _on_preview_drag(self, event):
        s = self._scale
        if s <= 0: return
        if self._panning:
            dx, dy = event.x - self._pan_start[0], event.y - self._pan_start[1]
            self._preview_off = (self._pan_off0[0] + dx, self._pan_off0[1] + dy)
            self._render_preview()
            return
        if not self._drag_item: return
        ox, oy = self._preview_off
        cx, cy = (event.x-ox)/s, (event.y-oy)/s
        nx, ny = max(0, int(cx-self._drag_off_x)), max(0, int(cy-self._drag_off_y))
        if self._multi_sel:
            mit = self._drag_item
            mip = self._drag_part
            base = self._multi_init.get((mit, mip))
            if not base: return
            dx = nx - base["x"]
            dy = ny - base["y"]
            for m, mp in self._multi_sel:
                ib = self._multi_init.get((m, mp))
                if not ib: continue
                h_ok = self._move_h.get() or not any((self._move_h.get(), self._move_v.get()))
                v_ok = self._move_v.get() or not any((self._move_h.get(), self._move_v.get()))
                if h_ok:
                    if mp == "label":
                        m.label_x = max(0, ib["x"] + dx)
                    else:
                        m.value_x = max(0, ib["x"] + dx)
                if v_ok:
                    if mp == "label":
                        m.label_y = max(0, ib["y"] + dy)
                    else:
                        m.value_y = max(0, ib["y"] + dy)
        else:
            h_ok = self._move_h.get() or not any((self._move_h.get(), self._move_v.get()))
            v_ok = self._move_v.get() or not any((self._move_h.get(), self._move_v.get()))
            if self._drag_part == "label":
                if h_ok: self._drag_item.label_x = nx
                if v_ok: self._drag_item.label_y = ny
            elif self._drag_part == "value":
                if h_ok: self._drag_item.value_x = nx
                if v_ok: self._drag_item.value_y = ny
        if self._sel_item is self._drag_item: self._load_props(self._sel_item)
        self._refresh_grid(); self._render_preview()

    def _align_parts(self, axis, to_min):
        items = self._multi_sel[:] if self._multi_sel else []
        if not items and self._sel_item:
            items = [(self._sel_item, "label"), (self._sel_item, "value")]
        if not items:
            self._status(_("align_select_first")); return
        from PIL import ImageDraw
        def _get_size(m, mp):
            txt = m.label if mp == "label" else self._get_display_val(m)
            fs = m.label_font_size if mp == "label" else m.value_font_size
            fn = m.label_font_name if mp == "label" else m.value_font_name
            try:
                font = _load_font(fn, fs)
                bb = ImageDraw.Draw(Image.new("RGB", (1,1))).textbbox((0,0), txt, font=font)
                return bb[2]-bb[0], bb[3]-bb[1]
            except:
                return len(txt) * fs // 2, fs
        vals = []
        for m, mp in items:
            pos = m.label_x if mp == "label" else m.value_x
            if axis == "y":
                pos = m.label_y if mp == "label" else m.value_y
                w, h = _get_size(m, mp)
                vals.append(pos) if to_min else vals.append(pos + h)
            else:
                w, h = _get_size(m, mp)
                vals.append(pos) if to_min else vals.append(pos + w)
        target = (min if to_min else max)(vals)
        for m, mp in items:
            w, h = _get_size(m, mp)
            offset = (0 if to_min else (-w if axis == "x" else -h))
            if mp == "label":
                if axis == "x": m.label_x = target + offset
                else: m.label_y = target + offset
            else:
                if axis == "x": m.value_x = target + offset
                else: m.value_y = target + offset
        self._refresh_grid(); self._render_preview(); self._silent_save()
        self._status(_("aligned_count", len(items)))

    def _on_row_spacing_change(self):
        try:
            v = int(self._row_spacing_var.get())
            v = max(10, min(100, v))
            self._row_spacing = v
            self._row_spacing_var.set(str(v))
            if self._active_items:
                base_y = self._active_items[0].label_y
                for i, it in enumerate(self._active_items):
                    dy = i * v
                    it.label_y = base_y + dy
                    it.value_y = base_y + dy
            self._refresh_grid(); self._render_preview(); self._silent_save()
            self._status(_("row_spacing_val", v))
        except ValueError:
            pass

    def _align_left(self): self._align_parts("x", True)
    def _align_right(self): self._align_parts("x", False)
    def _align_top(self): self._align_parts("y", True)
    def _align_bottom(self): self._align_parts("y", False)

    def _on_preview_wheel(self, event):
        old = self._preview_zoom
        self._preview_zoom = max(0.2, min(5.0, self._preview_zoom + (event.delta // 120) * 0.1))
        if self._preview_zoom != old:
            cw = self.preview.winfo_width()
            ch = self.preview.winfo_height()
            if cw <= 1: cw = 640
            if ch <= 1: ch = 400
            cx, cy = cw / 2, ch / 2
            s0 = min(cw / ctypes.windll.user32.GetSystemMetrics(0), ch / ctypes.windll.user32.GetSystemMetrics(1), 0.5) * old
            s1 = min(cw / ctypes.windll.user32.GetSystemMetrics(0), ch / ctypes.windll.user32.GetSystemMetrics(1), 0.5) * self._preview_zoom
            if s0 > 0 and s1 > 0:
                ix = (cx - self._preview_off[0]) / s0
                iy = (cy - self._preview_off[1]) / s0
                self._preview_off = (cx - ix * s1, cy - iy * s1)
            self._render_preview()
            self._status(_("zoom_pct", self._preview_zoom*100))

    def _on_source_toggle(self):
        self._data_sources = [k for k, var in self._source_vars.items() if var.get()]
        self._silent_save()

    def _on_move_mode_change(self):
        self._silent_save()
        h = self._move_h.get()
        v = self._move_v.get()
        if h and v:
            txt = "↔ ↕"
        elif h:
            txt = "↔"
        elif v:
            txt = "↕"
        else:
            txt = "✚"
        self._status(_("drag_status", txt))

    def _on_preview_dur_change(self):
        try:
            v = int(self._preview_dur_var.get())
            v = max(1, min(60, v))
            self._preview_dur_sec = v
            self._preview_dur_var.set(str(v))
            self.config_mgr.set("preview_duration", v)
            self._silent_save()
            self._status(_("wait_duration_val", v))
        except ValueError:
            pass

    def _select_grid_row(self, idx):
        for child in self.grid.get_children():
            if self.grid.index(child) == idx:
                self.grid.selection_set(child); self.grid.focus(child); self.grid.see(child)
                self._on_grid_select(None); return

    # ── Fullscreen Preview (composed wallpaper + zoom) ──
    def _show_fullscreen(self):
        if not self._active_items:
            messagebox.showwarning(_("warn"), _("no_info_selected")); return

        sw, sh = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
        img = self._compose_wallpaper((sw, sh))

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.geometry(f"{sw}x{sh}+0+0")
        win.configure(bg="black")
        win.transient(self.root)
        win.deiconify()
        win.lift()
        win.focus_force()
        win.grab_set()
        win.update_idletasks()

        fs_zoom = [1.0]
        fs_photo = [None]
        fs_canvas = tk.Canvas(win, bg="black", highlightthickness=0)
        fs_canvas.pack(fill=tk.BOTH, expand=True)
        fs_img = img

        def fs_update():
            nw, nh = int(sw * fs_zoom[0]), int(sh * fs_zoom[0])
            try:
                resized = fs_img.resize((nw, nh), Image.LANCZOS)
                fs_photo[0] = ImageTk.PhotoImage(resized)
                fs_canvas.delete("all")
                fs_canvas.create_image(sw//2, sh//2, image=fs_photo[0], anchor=tk.CENTER)
            except: pass

        def fs_zoom_handler(event):
            fs_zoom[0] = max(0.1, min(5.0, fs_zoom[0] + (event.delta // 120) * 0.1))
            fs_update()

        fs_photo[0] = ImageTk.PhotoImage(img)
        fs_canvas.create_image(sw//2, sh//2, image=fs_photo[0], anchor=tk.CENTER)
        fs_canvas.bind("<MouseWheel>", fs_zoom_handler)

        def _close_fs(e=None):
            try: win.grab_release()
            except: pass
            try: win.destroy()
            except: pass
        win.bind("<Escape>", _close_fs)
        win.bind("<Button-1>", _close_fs)
        win.focus_set()
        self._status(_("preview_hint"))

    # ── Actions ──
    def _open_help(self):
        import webbrowser, os, sys
        from src.i18n import get_lang
        fn = "index_en.html" if get_lang() == "en" else "index.html"
        candidates = []
        if getattr(sys, 'frozen', False):
            candidates.append(os.path.join(sys._MEIPASS, "help", fn))
            candidates.append(os.path.join(os.path.dirname(sys.executable), "help", fn))
        else:
            candidates.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "help", fn))
        for p in candidates:
            if os.path.isfile(p):
                webbrowser.open(p)
                return
        self._status(_("help_not_found"))

    def _choose_bg_color(self):
        c = colorchooser.askcolor(color=self._bg_color, title=_("dlg_bg_color"))[1]
        if c: self._bg_color = c; self._bg_type = "color"; self._render_preview(); self._silent_save(); self._status(_("color_updated"))

    def _choose_bg_image(self):
        bg_dir = r"C:\Windows\Web\Wallpaper"
        p = filedialog.askopenfilename(title=_("dlg_bg_image"), initialdir=bg_dir,
              filetypes=[(_("dlg_all_files"),"*.jpg *.jpeg *.png *.bmp"),(_("dlg_all_files"),"*.*")])
        if p: self._bg_image = p; self._bg_type = "image"; self._render_preview(); self._silent_save(); self._status(_("image_selected"))

    def _apply_wallpaper(self):
        if not self._active_items:
            messagebox.showwarning(_("warn"), _("wallpaper_no_info")); return
        self._status(_("creating_wallpaper")); self.root.update_idletasks()

        img = self._compose_wallpaper()
        t = os.path.join(os.environ["TEMP"], "wallpaper_info_temp.bmp")
        img.save(t, "BMP")
        ctypes.windll.user32.SystemParametersInfoW(20, 0, t, 0x01|0x02)
        self._status(_("wallpaper_applied"))
        messagebox.showinfo(_("success"), _("wallpaper_success"))

    def _get_screen_size(self):
        try:
            log_w = ctypes.windll.user32.GetSystemMetrics(0)
            log_h = ctypes.windll.user32.GetSystemMetrics(1)
            try:
                dc = ctypes.windll.user32.GetDC(0)
                phys_w = ctypes.windll.gdi32.GetDeviceCaps(dc, 118)
                phys_h = ctypes.windll.gdi32.GetDeviceCaps(dc, 117)
                ctypes.windll.user32.ReleaseDC(0, dc)
                if phys_w > 0 and phys_h > 0:
                    return phys_w, phys_h
            except:
                pass
            return log_w, log_h
        except:
            return 1920, 1080

    def _compose_wallpaper(self, size=None):
        sw, sh = size if size else self._get_screen_size()
        if self._bg_type == "image" and self._bg_image and os.path.isfile(self._bg_image):
            img = Image.open(self._bg_image).convert("RGB").resize((sw, sh), Image.LANCZOS)
        else:
            try:
                hc = self._bg_color.lstrip("#")
                rgb = tuple(int(hc[i:i+2],16) for i in (0,2,4))
            except: rgb = (30,30,46)
            img = Image.new("RGB", (sw, sh), rgb)
        draw = ImageDraw.Draw(img)
        for it in self._active_items:
            try:
                if it.show_label:
                    lf = _load_font(it.label_font_name, it.label_font_size)
                    lc = it.label_font_color.lstrip("#")
                    lrgb = tuple(int(lc[i:i+2],16) for i in (0,2,4)) if len(lc)==6 else (255,255,255)
                    draw.text((it.label_x, it.label_y), it.label, fill=lrgb, font=lf)
                if it.show_value:
                    vf = _load_font(it.value_font_name, it.value_font_size)
                    vc = it.value_font_color.lstrip("#")
                    vrgb = tuple(int(vc[i:i+2],16) for i in (0,2,4)) if len(vc)==6 else (0,255,0)
                    draw.text((it.value_x, it.value_y), self._get_display_val(it), fill=vrgb, font=vf)
            except: continue
        return img

    def _preview_desktop(self):
        if not self._active_items:
            messagebox.showwarning(_("warn"), _("no_info_selected")); return
        self._status(_("desktop_prep")); self.root.update_idletasks()
        try:
            import win32com.client
            shell = win32com.client.Dispatch("Shell.Application")
            shell.MinimizeAll()
        except Exception:
            pass
        self.root.after(100, lambda: self._do_preview_desktop())

    def _do_preview_desktop(self):
        try:
            import ctypes.wintypes
            buf = ctypes.create_unicode_buffer(512)
            ctypes.windll.user32.SystemParametersInfoW(0x0073, 512, buf, 0)
            old_wall = buf.value
        except:
            old_wall = ""
        t = os.path.join(os.environ["TEMP"], "wallpaper_preview_temp.bmp")
        try:
            img = self._compose_wallpaper()
            img.save(t, "BMP")
            ctypes.windll.user32.SystemParametersInfoW(20, 0, t, 0x01|0x02)
            self._status(_("desktop_active", self._preview_dur_sec))
            ms = int(self._preview_dur_sec * 1000)
            self.root.after(ms, lambda: self._restore_wallpaper(old_wall))
        except Exception as e:
            self._status(f"Hata: {e}")
            if old_wall:
                self._restore_wallpaper(old_wall)
    def _restore_wallpaper(self, path):
        try:
            if path and os.path.isfile(path):
                ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0x01|0x02)
            self._status(_("desktop_done"))
            self.root.wm_deiconify()
            self.root.state("zoomed")
            self.root.lift()
            self.root.focus_force()
        except:
            pass

    # ── Config ──
    def _silent_save(self):
        try:
            self.config_mgr.save({
                "background_type": self._bg_type, "background_color": self._bg_color,
                "background_image": self._bg_image,
                "items": [it.to_dict() for it in self._active_items],
                "data_sources": self._data_sources,
                "startup_refresh": self._startup_refresh.get(),
                "preview_duration": self._preview_dur_sec,
                "move_h": self._move_h.get() if hasattr(self, "_move_h") else True,
                "move_v": self._move_v.get() if hasattr(self, "_move_v") else True,
                "row_spacing": self._row_spacing,
                "last_values": {it.id: it.last_value for it in self._all_items if it.last_value},
                "startup_run_enabled": self._startup_run.get() if hasattr(self, "_startup_run") else False,
                "startup_run_duration": int(self._startup_run_dur.get()) if hasattr(self, "_startup_run_dur") else 3,
            })
        except: pass

    def _save_config(self, show_msg=False):
        self._silent_save()
        if show_msg: messagebox.showinfo(_("success"), _("settings_saved"))
        self._status("Ayarlar kaydedildi.")

    def _load_config(self):
        if not messagebox.askyesno(_("confirm"), _("load_confirm")): return
        st = self.config_mgr.load()
        self._bg_type = st.get("background_type","color")
        self._bg_color = st.get("background_color","#1e1e2e")
        self._bg_image = st.get("background_image","")
        self._active_items.clear()
        for sd in st.get("items",[]):
            it = InfoItem(sd["id"],sd["label"],sd.get("category",""),sd.get("subcategory",""))
            for k,v in sd.items():
                if hasattr(it,k) and k not in ("id","category","subcategory"): setattr(it,k,v)
            self._active_items.append(it)
        self._active_items = restore_getters(self._active_items, self._all_items)
        self._sel_index = None; self._sel_item = None
        self._pr_sel.set(_("selected"))
        self._refresh_grid(); self._render_preview()
        self._status(_("items_loaded_msg", len(self._active_items)))

    def _on_close(self):
        self._silent_save(); self.root.destroy()

    def _lighten(self, c):
        try:
            h = c.lstrip("#")
            r,g,b = min(255,int(h[0:2],16)+35), min(255,int(h[2:4],16)+35), min(255,int(h[4:6],16)+35)
            return f"#{r:02x}{g:02x}{b:02x}"
        except: return c

    def _status(self, msg): self._sv.set(f"  {msg}")
    def run(self): self.root.mainloop()
