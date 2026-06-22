"""Info tree model - every item has its own getter, no pre-collected data needed."""

from src.system_info import get_network_info, get_hardware_info, get_system_info, get_database_info, _info_cache
from src.i18n import _


class InfoItem:
    def __init__(self, item_id, label, category, subcategory, getter=None, static_value="", is_dynamic=False, source=""):
        self.id = item_id
        self.label = label
        self.original_label = label
        self.category = category
        self.subcategory = subcategory
        self._getter = getter
        self._static_value = static_value
        self.is_dynamic = is_dynamic
        self.source = source

        self.label_x = 20
        self.label_y = 20
        self.label_font_size = 14
        self.label_font_color = "#ffffff"
        self.label_font_name = "Consolas"

        self.value_x = 20
        self.value_y = 40
        self.value_font_size = 14
        self.value_font_color = "#00ff00"
        self.value_font_name = "Consolas"

        self.show_label = True
        self.show_value = True
        self.static_override = ""
        self.last_value = ""

    def get_value(self):
        if self.static_override:
            return self.static_override
        if self._getter is not None:
            try:
                val = self._getter()
                return str(val) if val is not None else ""
            except Exception:
                return "N/A"
        return self._static_value

    def refresh_last_value(self):
        v = self.get_value()
        if v and v not in ("N/A", "...", ""):
            self.last_value = v

    def to_dict(self):
        return {k: getattr(self, k) for k in (
            "id","label","original_label","category","subcategory",
            "label_x","label_y","label_font_size","label_font_color","label_font_name",
            "value_x","value_y","value_font_size","value_font_color","value_font_name",
            "show_label","show_value","static_override","last_value",
        )}


# ── Helpers ──
def _g(data, *keys):
    for k in keys:
        if isinstance(data, dict): data = data.get(k, "")
        elif isinstance(data, list):
            try: data = data[int(k)]
            except: return ""
        else: return ""
    return data if data is not None else ""


def _gb(val):
    try: return f"{float(val):.1f} GB"
    except: return "0 GB"


def _pct(val):
    try: return f"{float(val):.1f}%"
    except: return "0%"


def _fmt_disk(p):
    return p.replace("\\", "")


# ── Builders ──
def _build_network(items):
    items.append(InfoItem("net.hostname", _("lbl_net_hostname"), _("cat_network"), "",
                         getter=lambda: _g(get_network_info(), "hostname")))

    def add_interface_ips():
        data = get_network_info()
        ifaces = _g(data, "interfaces")
        if not isinstance(ifaces, list): return
        for idx, iface in enumerate(ifaces):
            name = iface.get("name", "")
            desc = iface.get("description", "") or name
            addrs = iface.get("addresses", [])
            for a in addrs:
                family = str(a.get("family", ""))
                addr_val = a.get("address", "")
                if family == "-1": continue
                if family == "2" and addr_val:
                    if addr_val.startswith("169.254") or addr_val == "127.0.0.1": continue
                    items.append(InfoItem(f"net.ip.{idx}", f"{desc[:25]}", _("cat_network"), f"IP > {desc[:20]}",
                                         getter=lambda i=idx: _g(_g(get_network_info(), "interfaces"), str(i), "addresses")[1].get("address","") if len(_g(get_network_info(), "interfaces")) > i and len(_g(_g(get_network_info(), "interfaces"), str(i), "addresses")) > 1 else ""))
                elif family == "23" and addr_val:
                    if addr_val == "::1": continue
                    items.append(InfoItem(f"net.ip6.{idx}", f"{desc[:25]} IPv6", _("cat_network"), f"IP > {desc[:20]}",
                                         getter=lambda i=idx: _g(_g(get_network_info(), "interfaces"), str(i), "addresses")[2].get("address","") if len(_g(get_network_info(), "interfaces")) > i and len(_g(_g(get_network_info(), "interfaces"), str(i), "addresses")) > 2 else ""))

    if "network" in _info_cache:
        add_interface_ips()


def _build_hardware(items):
    get_hw = get_hardware_info

    items.append(InfoItem("hw.cpu.name", _("lbl_hw_cpu_name"), _("cat_hardware"), _("sub_processor"),
                         getter=lambda: _g(get_hw(), "cpu", "name")))
    items.append(InfoItem("hw.cpu.cores", _("lbl_hw_cpu_cores"), _("cat_hardware"), _("sub_processor"),
                         getter=lambda: _g(get_hw(), "cpu", "cores")))
    items.append(InfoItem("hw.cpu.logical", _("lbl_hw_cpu_logical"), _("cat_hardware"), _("sub_processor"),
                         getter=lambda: _g(get_hw(), "cpu", "logical_processors")))
    items.append(InfoItem("hw.cpu.speed", _("lbl_hw_cpu_speed"), _("cat_hardware"), _("sub_processor"),
                         getter=lambda: _g(get_hw(), "cpu", "max_clock_speed_mhz")))
    items.append(InfoItem("hw.cpu.usage", _("lbl_hw_cpu_usage"), _("cat_hardware"), _("sub_processor"),
                         getter=lambda: _pct(_g(get_hw(), "cpu", "usage_percent")),
                         is_dynamic=True))

    items.append(InfoItem("hw.mem.total", _("lbl_hw_mem_total"), _("cat_hardware"), _("sub_memory"),
                         getter=lambda: _gb(_g(get_hw(), "memory", "total_gb"))))
    items.append(InfoItem("hw.mem.used", _("lbl_hw_mem_used"), _("cat_hardware"), _("sub_memory"),
                         getter=lambda: _gb(_g(get_hw(), "memory", "used_gb"))))
    items.append(InfoItem("hw.mem.avail", _("lbl_hw_mem_avail"), _("cat_hardware"), _("sub_memory"),
                         getter=lambda: _gb(_g(get_hw(), "memory", "available_gb"))))
    items.append(InfoItem("hw.mem.percent", _("lbl_hw_mem_percent"), _("cat_hardware"), _("sub_memory"),
                         getter=lambda: _pct(_g(get_hw(), "memory", "percent")),
                         is_dynamic=True))

    # Disks
    def add_disks():
        disks = _g(get_hw(), "disks")
        if not isinstance(disks, list): return
        for i, d in enumerate(disks):
            dev = _fmt_disk(_g(d, "device"))
            sc = _("sub_disk", dev)
            items.append(InfoItem(f"hw.disk.{i}.total", _("lbl_hw_disk_total", dev), _("cat_hardware"), sc,
                                 getter=lambda i=i: _gb(_g(_g(get_hw(), "disks"), str(i), "total_gb"))))
            items.append(InfoItem(f"hw.disk.{i}.used", _("lbl_hw_disk_used", dev), _("cat_hardware"), sc,
                                 getter=lambda i=i: _gb(_g(_g(get_hw(), "disks"), str(i), "used_gb"))))
            items.append(InfoItem(f"hw.disk.{i}.free", _("lbl_hw_disk_free", dev), _("cat_hardware"), sc,
                                 getter=lambda i=i: _gb(_g(_g(get_hw(), "disks"), str(i), "free_gb"))))
            items.append(InfoItem(f"hw.disk.{i}.pct", _("lbl_hw_disk_pct", dev), _("cat_hardware"), sc,
                                 getter=lambda i=i: _pct(_g(_g(get_hw(), "disks"), str(i), "percent"))))

    if "hardware" in _info_cache:
        add_disks()

    # GPU
    def add_gpus():
        gpus = _g(get_hw(), "gpu")
        if not isinstance(gpus, list): return
        for i, g in enumerate(gpus):
            gn = _g(g, "name")[:30]
            sc = _("sub_gpu", gn)
            items.append(InfoItem(f"hw.gpu.{i}.name", _("lbl_hw_gpu_name", gn), _("cat_hardware"), sc,
                                 getter=lambda i=i: _g(_g(get_hw(), "gpu"), str(i), "name")))
            items.append(InfoItem(f"hw.gpu.{i}.vram", _("lbl_hw_gpu_vram"), _("cat_hardware"), sc,
                                 getter=lambda i=i: _gb(_g(_g(get_hw(), "gpu"), str(i), "adapter_ram_gb"))))
            items.append(InfoItem(f"hw.gpu.{i}.driver", _("lbl_hw_gpu_driver"), _("cat_hardware"), sc,
                                 getter=lambda i=i: _g(_g(get_hw(), "gpu"), str(i), "driver_version")))
            items.append(InfoItem(f"hw.gpu.{i}.res", _("lbl_hw_gpu_res"), _("cat_hardware"), sc,
                                 getter=lambda i=i: _g(_g(get_hw(), "gpu"), str(i), "resolution")))

    if "hardware" in _info_cache:
        add_gpus()

    # Motherboard
    items.append(InfoItem("hw.mb.mfr", _("lbl_hw_mb_mfr"), _("cat_hardware"), _("sub_motherboard"),
                         getter=lambda: _g(get_hw(), "motherboard", "manufacturer")))
    items.append(InfoItem("hw.mb.product", _("lbl_hw_mb_product"), _("cat_hardware"), _("sub_motherboard"),
                         getter=lambda: _g(get_hw(), "motherboard", "product")))
    items.append(InfoItem("hw.mb.serial", _("lbl_hw_mb_serial"), _("cat_hardware"), _("sub_motherboard"),
                         getter=lambda: _g(get_hw(), "motherboard", "serial")))


def _build_system(items):
    get_sys = get_system_info

    items.append(InfoItem("sys.os.name", _("lbl_sys_os_name"), _("cat_system"), _("sub_os"),
                         getter=lambda: _g(get_sys(), "os", "name")))
    items.append(InfoItem("sys.os.version", _("lbl_sys_os_version"), _("cat_system"), _("sub_os"),
                         getter=lambda: _g(get_sys(), "os", "version")))
    items.append(InfoItem("sys.os.build", _("lbl_sys_os_build"), _("cat_system"), _("sub_os"),
                         getter=lambda: _g(get_sys(), "os", "build")))
    items.append(InfoItem("sys.os.arch", _("lbl_sys_os_arch"), _("cat_system"), _("sub_os"),
                         getter=lambda: _g(get_sys(), "os", "architecture")))
    items.append(InfoItem("sys.os.install", _("lbl_sys_os_install"), _("cat_system"), _("sub_os"),
                         getter=lambda: str(_g(get_sys(), "os", "install_date"))[:10]))

    items.append(InfoItem("sys.user.name", _("lbl_sys_user_name"), _("cat_system"), _("sub_user"),
                         getter=lambda: _g(get_sys(), "user", "username")))
    items.append(InfoItem("sys.user.computer", _("lbl_sys_user_computer"), _("cat_system"), _("sub_user"),
                         getter=lambda: _g(get_sys(), "user", "computer_name")))
    items.append(InfoItem("sys.user.domain", _("lbl_sys_user_domain"), _("cat_system"), _("sub_user"),
                         getter=lambda: _g(get_sys(), "user", "user_domain")))

    items.append(InfoItem("sys.uptime", _("lbl_sys_uptime"), _("cat_system"), _("sub_uptime"),
                         getter=lambda: f"{_g(get_sys(),'uptime','days')}g {_g(get_sys(),'uptime','hours')}s {_g(get_sys(),'uptime','minutes')}d",
                         is_dynamic=True))

    items.append(InfoItem("sys.tz", _("lbl_sys_tz"), _("cat_system"), _("sub_time"),
                         getter=lambda: _g(get_sys(), "timezone", "timezone")))
    items.append(InfoItem("sys.local_time", _("lbl_sys_local_time"), _("cat_system"), _("sub_time"),
                         getter=lambda: _g(get_sys(), "timezone", "local_time"),
                         is_dynamic=True))

    items.append(InfoItem("sys.lic.id", "Windows Product ID", _("cat_system"), _("sub_license"),
                         getter=lambda: _g(get_sys(), "license", "product_id")))
    items.append(InfoItem("sys.lic.key", "Windows Product Key", _("cat_system"), _("sub_license"),
                         getter=lambda: _g(get_sys(), "license", "product_key")))

    items.append(InfoItem("sys.act.status", _("lbl_sys_act_status"), _("cat_system"), _("sub_activation"),
                         getter=lambda: _g(get_sys(), "activation", "license_status")))
    items.append(InfoItem("sys.act.kms", _("lbl_sys_act_kms"), _("cat_system"), _("sub_activation"),
                         getter=lambda: _g(get_sys(), "activation", "kms_host")))

    def add_users():
        users = _g(get_sys(), "users")
        if not isinstance(users, list): return
        for i, u in enumerate(users):
            un = _g(u, "name")
            sc = _("sub_users", un)
            items.append(InfoItem(f"sys.userlist.{i}.name", f"{un}", _("cat_system"), sc,
                                 getter=lambda i=i: _g(_g(get_sys(), "users"), str(i), "name")))
            items.append(InfoItem(f"sys.userlist.{i}.status", _("lbl_sys_user_status", un), _("cat_system"), sc,
                                 getter=lambda i=i: _g(_g(get_sys(), "users"), str(i), "status")))
            items.append(InfoItem(f"sys.userlist.{i}.type", _("lbl_sys_user_type", un), _("cat_system"), sc,
                                 getter=lambda i=i: _g(_g(get_sys(), "users"), str(i), "type")))

    if "system" in _info_cache:
        add_users()


def _build_database(items):
    get_db = get_database_info

    def add_instances():
        insts = _g(get_db(), "sql_instances")
        if not isinstance(insts, list): return
        for i, inst in enumerate(insts):
            iname = _g(inst, "name")
            sc = _("sub_sql", iname)
            items.append(InfoItem(f"db.inst.{i}.name", _("lbl_db_inst_name", iname), _("cat_database"), sc,
                                 getter=lambda i=i: _g(_g(get_db(), "sql_instances"), str(i), "name")))
            items.append(InfoItem(f"db.inst.{i}.edition", f"Edition: {_g(inst, 'edition')}", _("cat_database"), sc,
                                 getter=lambda i=i: _g(_g(get_db(), "sql_instances"), str(i), "edition")))

    def add_odbc_sys():
        dsns = _g(get_db(), "odbc_system_dsns")
        if not isinstance(dsns, list): return
        for i, dsn in enumerate(dsns):
            dn = _g(dsn, "name")
            if dn:
                items.append(InfoItem(f"db.odbc_sys.{i}", _("lbl_db_odbc_sys", dn), _("cat_database"), _("sub_odbc"),
                                     getter=lambda i=i: _g(_g(get_db(), "odbc_system_dsns"), str(i), "name")))

    def add_odbc_user():
        dsns = _g(get_db(), "odbc_user_dsns")
        if not isinstance(dsns, list): return
        for i, dsn in enumerate(dsns):
            dn = _g(dsn, "name")
            if dn:
                items.append(InfoItem(f"db.odbc_user.{i}", _("lbl_db_odbc_user", dn), _("cat_database"), _("sub_odbc"),
                                     getter=lambda i=i: _g(_g(get_db(), "odbc_user_dsns"), str(i), "name")))

    if "database" in _info_cache:
        add_instances()
        add_odbc_sys()
        add_odbc_user()


CATEGORY_SOURCE_MAP = {
    "Ağ": "network", "Network": "network",
    "Donanım": "hardware", "Hardware": "hardware",
    "Sistem": "system", "System": "system",
    "Veritabanı": "database", "Database": "database",
}

def build_tree(data=None, sources=None):
    """Build tree from selected sources (list of 'network','hardware','system','database').
       If sources is None/empty, all are included."""
    source_builders = {
        "network": _build_network,
        "hardware": _build_hardware,
        "system": _build_system,
        "database": _build_database,
    }
    if not sources:
        sources = list(source_builders.keys())

    items = []
    for src in sources:
        builder = source_builders.get(src)
        if builder:
            builder(items)

    cats = {}
    for it in items:
        cat = it.category
        if cat not in cats:
            cats[cat] = InfoCategory(cat, [])
        cats[cat].items.append(it)
    return list(cats.values())


class InfoCategory:
    def __init__(self, name, items=None):
        self.name = name
        self.items = items or []


def flatten_items(categories):
    result = []
    for cat in categories:
        result.extend(cat.items)
    return result


def restore_getters(saved_items, all_tree_items):
    """Match saved items with tree items by ID to restore getter functions."""
    lookup = {it.id: it for it in all_tree_items}
    for saved in saved_items:
        match = lookup.get(saved.id)
        if match:
            saved._getter = match._getter
            saved._static_value = match._static_value
            saved.is_dynamic = match.is_dynamic
    return saved_items


def auto_align(items, start_x=30, start_y=30, label_col=200, row_height=35):
    for i, it in enumerate(items):
        it.label_x = start_x
        it.label_y = start_y + i * row_height
        it.value_x = start_x + label_col
        it.value_y = start_y + i * row_height
