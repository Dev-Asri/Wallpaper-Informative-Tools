class Lang:
    def __init__(self, code="tr"):
        self.code = code
        self._strings = {
            "window_title": ["Wallpaper Informative Tool - Duvar Kağıdı Bilgi Aracı", "Wallpaper Informative Tool"],
            "refresh": ["\u26a1  Verileri Güncelle", "\u26a1  Refresh Data"],
            "startup_refresh": ["Açılışta Güncelle", "Refresh on Startup"],
            "startup_run": ["Açıldığında Değiştir ve Kapat", "Change & Close on Startup"],
            "apply_wallpaper": ["\U0001f5a8  Duvar Kağıdını Uygula", "\U0001f5a8  Apply Wallpaper"],
            "remove": ["\u274c  Kaldır", "\u274c  Remove"],
            "move_up": ["\u25b2  Yukarı", "\u25b2  Move Up"],
            "move_down": ["\u25bc  Aşağı", "\u25bc  Move Down"],
            "align": ["\U0001f4cb  Hizala", "\U0001f4cb  Align"],
            "clear": ["\U0001f503  Temizle", "\U0001f503  Clear"],
            "available_info": ["Kullanılabilir Bilgiler", "Available Information"],
            "active_info": ["Aktif Bilgiler", "Active Information"],
            "properties": ["Özellikler", "Properties"],
            "drag_mode": ["Sürükleme:", "Drag Mode:"],
            "drag_h": ["\u2194 Yatay", "\u2194 Horizontal"],
            "drag_v": ["\u2195 Dikey", "\u2195 Vertical"],
            "align_btns": ["Hizalama:", "Align:"],
            "preview_frame": ["Ön İzleme (CTRL ile çoklu seçim)", "Preview (CTRL for multi-select)"],
            "row_spacing": ["Satırlar arası boşluk:", "Row Spacing:"],
            "wait_duration": ["Bekleme Süresi:", "Wait Duration:"],
            "sec": ["sn", "s"],
            "desktop_preview": ["\U0001f5a5  Masaüstü Ön izleme", "\U0001f5a5  Desktop Preview"],
            "preview": ["\U0001f50d  Ön İzle", "\U0001f50d  Preview"],
            "bg_color": ["\U0001f3a8  Arkaplan Rengi", "\U0001f3a8  Background Color"],
            "bg_image": ["\U0001f5bc  Arkaplan Resmi", "\U0001f5bc  Background Image"],
            "column_label": ["Etiket", "Label"],
            "column_value": ["Değer", "Value"],
            "selected": ["Seçili: -", "Selected: -"],
            "selected_item": ["Seçili: {0}", "Selected: {0}"],

            # Property tabs
            "tab_label": ["Etiket", "Label"],
            "tab_value": ["Değer", "Value"],
            "tab_position": ["Konum", "Position"],
            "prop_label_name": ["Etiket Adı", "Label Name"],
            "prop_font": ["Yazı Tipi", "Font"],
            "prop_font_size": ["Boyut", "Size"],
            "prop_font_color": ["Renk", "Color"],
            "prop_show": ["Göster", "Show"],
            "prop_static_value": ["Sabit Değer", "Static Value"],
            "prop_label_x": ["Label X", "Label X"],
            "prop_label_y": ["Label Y", "Label Y"],
            "prop_value_x": ["Value X", "Value X"],
            "prop_value_y": ["Value Y", "Value Y"],
            "apply_all": ["\u2192 Tümü", "\u2192 All"],

            # Category names
            "cat_network": ["Ağ", "Network"],
            "cat_hardware": ["Donanım", "Hardware"],
            "cat_system": ["Sistem", "System"],
            "cat_database": ["Veritabanı", "Database"],

            # Subcategory names
            "sub_processor": ["İşlemci", "Processor"],
            "sub_memory": ["Bellek", "Memory"],
            "sub_disk": ["Disk > {0}", "Disk > {0}"],
            "sub_gpu": ["GPU > {0}", "GPU > {0}"],
            "sub_motherboard": ["Anakart", "Motherboard"],
            "sub_os": ["İşletim Sistemi", "Operating System"],
            "sub_user": ["Kullanıcı", "User"],
            "sub_uptime": ["Çalışma Süresi", "Uptime"],
            "sub_time": ["Zaman", "Time"],
            "sub_license": ["Lisans", "License"],
            "sub_activation": ["Aktivasyon", "Activation"],
            "sub_users": ["Kullanıcılar > {0}", "Users > {0}"],
            "sub_sql": ["SQL > {0}", "SQL > {0}"],
            "sub_odbc": ["ODBC", "ODBC"],

            # Item labels - Network
            "lbl_net_hostname": ["Bilgisayar Adı", "Computer Name"],

            # Item labels - Hardware
            "lbl_hw_cpu_name": ["CPU Adı", "CPU Name"],
            "lbl_hw_cpu_cores": ["Fiziksel Çekirdek", "Physical Cores"],
            "lbl_hw_cpu_logical": ["Mantıksal Çekirdek", "Logical Cores"],
            "lbl_hw_cpu_speed": ["CPU Hızı (MHz)", "CPU Speed (MHz)"],
            "lbl_hw_cpu_usage": ["CPU Kullanımı", "CPU Usage"],
            "lbl_hw_mem_total": ["RAM Toplam", "Total RAM"],
            "lbl_hw_mem_used": ["RAM Kullanılan", "Used RAM"],
            "lbl_hw_mem_avail": ["RAM Boş", "Free RAM"],
            "lbl_hw_mem_percent": ["RAM Kullanım %", "RAM Usage %"],
            "lbl_hw_disk_total": ["{0} Toplam", "{0} Total"],
            "lbl_hw_disk_used": ["{0} Kullanılan", "{0} Used"],
            "lbl_hw_disk_free": ["{0} Boş", "{0} Free"],
            "lbl_hw_disk_pct": ["{0} Doluluk", "{0} Usage"],
            "lbl_hw_gpu_name": ["GPU: {0}", "GPU: {0}"],
            "lbl_hw_gpu_vram": ["VRAM", "VRAM"],
            "lbl_hw_gpu_driver": ["Driver", "Driver"],
            "lbl_hw_gpu_res": ["Çözünürlük", "Resolution"],
            "lbl_hw_mb_mfr": ["Anakart Üretici", "Motherboard Manufacturer"],
            "lbl_hw_mb_product": ["Anakart Modeli", "Motherboard Model"],
            "lbl_hw_mb_serial": ["Anakart Seri No", "Motherboard Serial"],

            # Item labels - System
            "lbl_sys_os_name": ["İşletim Sistemi", "Operating System"],
            "lbl_sys_os_version": ["OS Versiyon", "OS Version"],
            "lbl_sys_os_build": ["OS Build", "OS Build"],
            "lbl_sys_os_arch": ["OS Mimarisi", "OS Architecture"],
            "lbl_sys_os_install": ["Kurulum Tarihi", "Install Date"],
            "lbl_sys_user_name": ["Kullanıcı Adı", "Username"],
            "lbl_sys_user_computer": ["Bilgisayar Adı", "Computer Name"],
            "lbl_sys_user_domain": ["Domain", "Domain"],
            "lbl_sys_uptime": ["Çalışma Süresi", "Uptime"],
            "lbl_sys_tz": ["Saat Dilimi", "Timezone"],
            "lbl_sys_local_time": ["Yerel Saat", "Local Time"],
            "lbl_sys_act_status": ["Lisans Durumu", "License Status"],
            "lbl_sys_act_kms": ["KMS Sunucu", "KMS Host"],
            "lbl_sys_user_status": ["{0} Durum", "{0} Status"],
            "lbl_sys_user_type": ["{0} Tür", "{0} Type"],

            # Item labels - Database
            "lbl_db_inst_name": ["Instance: {0}", "Instance: {0}"],
            "lbl_db_odbc_sys": ["ODBC Sistem: {0}", "ODBC System: {0}"],
            "lbl_db_odbc_user": ["ODBC Kullanıcı: {0}", "ODBC User: {0}"],

            # Source checkboxes
            "src_network": ["Ağ", "Network"],
            "src_hardware": ["Donanım", "Hardware"],
            "src_system": ["Sistem", "System"],
            "src_database": ["Veritabanı", "Database"],

            # Status messages
            "loading": ["Yükleniyor...", "Loading..."],
            "items_loaded": ["{0} öğe yüklendi.", "{0} items loaded."],
            "ready": ["Hazır. \u26a1 Verileri Güncelle ile başlayın.", "Ready. \u26a1 Click Refresh Data to start."],
            "no_item_run": ["Açılışta Çalıştır: öğe bulunamadı, kapanıyor.", "Startup Run: no items found, closing."],
            "run_applied": ["Açıldığında Değiştir ve Kapat: duvar kağıdı uygulandı, {0}sn sonra kapanıyor...", "Change & Close: wallpaper applied, closing in {0}s..."],
            "run_error": ["Açıldığında Değiştir ve Kapat hatası: {0}", "Change & Close error: {0}"],
            "run_cancelled": ["Açıldığında Değiştir ve Kapat iptal edildi.", "Change & Close cancelled."],
            "collecting": ["Bilgiler toplanıyor (arka planda)...", "Collecting data (background)..."],
            "error_header": ["Hatalı: {0}", "Error: {0}"],
            "updated": ["Bilgiler güncellendi. {0} aktif öğe.", "Data updated. {0} active items."],
            "aligned": ["Öğeler hizalandı.", "Items aligned."],
            "applied_all": ["'{0}' tüm {1} öğeye uygulandı.", "'{0}' applied to all {1} items."],
            "align_select_first": ["Hizalama: önce Ctrl+click ile seçim yapın", "Align: select items with Ctrl+click first"],
            "aligned_count": ["Hizalandı ({0} öğe)", "Aligned ({0} items)"],
            "row_spacing_val": ["Satırlar arası boşluk: {0}px", "Row spacing: {0}px"],
            "zoom_pct": ["Yakınlaştırma: %{0:.0f}", "Zoom: %{0:.0f}"],
            "drag_status": ["Sürükleme: {0}", "Drag: {0}"],
            "wait_duration_val": ["Bekleme Süresi: {0} sn", "Wait Duration: {0}s"],
            "preview_hint": ["Ön İzle - ESC / tıklama ile kapatın. Fare tekerleği ile yakınlaştırın.", "Preview - ESC / click to close. Mouse wheel to zoom."],
            "color_updated": ["Renk güncellendi.", "Color updated."],
            "image_selected": ["Resim seçildi.", "Image selected."],
            "creating_wallpaper": ["Duvar kağıdı oluşturuluyor...", "Creating wallpaper..."],
            "wallpaper_applied": ["Duvar kağıdı uygulandı!", "Wallpaper applied!"],
            "desktop_prep": ["Masaüstü ön izleme hazırlanıyor...", "Preparing desktop preview..."],
            "desktop_active": ["Masaüstü ön izleme - {0} saniye sonra eski haline dönecek...", "Desktop preview - restoring in {0} seconds..."],
            "desktop_done": ["Masaüstü ön izleme tamamlandı.", "Desktop preview completed."],

            # Message boxes
            "warn": ["Uyarı", "Warning"],
            "success": ["Başarılı", "Success"],
            "confirm": ["Onay", "Confirm"],
            "no_info_selected": ["Gösterilecek bilgi seçilmedi!", "No information selected to display!"],
            "wallpaper_no_info": ["Duvar kağıdına eklenecek bilgi seçilmedi!", "No information selected for wallpaper!"],
            "wallpaper_success": ["Duvar kağıdı başarıyla uygulandı!", "Wallpaper applied successfully!"],
            "settings_saved": ["Ayarlar kaydedildi.", "Settings saved."],
            "load_confirm": ["Kayıtlı ayarlar yüklenecek. Devam?", "Load saved settings. Continue?"],
            "items_loaded_msg": ["{0} öğe yüklendi.", "{0} items loaded."],

            # Dialogs
            "dlg_bg_color": ["Arkaplan Rengi Seç", "Choose Background Color"],
            "dlg_bg_image": ["Arkaplan Resmi Seç", "Choose Background Image"],
            "dlg_all_files": ["Tüm Dosyalar", "All Files"],

            # Help button
            "help_btn": ["\u2753  Yard\u0131m", "\u2753  Help"],
            "help_not_found": ["Yard\u0131m dosyas\u0131 bulunamad\u0131.", "Help file not found."],

            # Credits
            "credits": ["Hazırlayan: Asri Akdeniz - asriakdeniz@gmail.com - www.asriakdeniz.com",
                       "Prepared by: Asri Akdeniz - asriakdeniz@gmail.com - www.asriakdeniz.com"],

            # Language
            "lang_tr": ["Türkçe", "Turkish"],
            "lang_en": ["English", "English"],

            # Item already active
            "already_active": ["'{0}' zaten aktif.", "'{0}' is already active."],
        }

    def get(self, key, *args):
        val = self._strings.get(key)
        if val is None:
            return key
        idx = 0 if self.code == "tr" else 1
        s = val[idx] if idx < len(val) else val[0]
        if args:
            return s.format(*args)
        return s

    def set_lang(self, code):
        self.code = code


_lang = Lang()

def _(key, *args):
    return _lang.get(key, *args)

def set_lang(code):
    _lang.set_lang(code)

def get_lang():
    return _lang.code
