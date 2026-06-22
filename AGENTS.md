# AGENTS.md - WallpaperInformativeTool

## Proje Yapısı
```
D:\AICodeProje\WindowsWallpaperInformativeTool\
├── src/
│   ├── __init__.py
│   ├── main.py              # Giriş noktası
│   ├── config_manager.py    # JSON ayar yönetimi
│   ├── system_info.py       # windows_sysinfo wrapper
│   ├── info_tree.py         # InfoItem modeli + kategori ağacı
│   ├── wallpaper_renderer.py # Pillow ile görüntü oluşturma
│   ├── overlay.py           # Sürüklenebilir overlay
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # Ana tkinter penceresi
├── requirements.txt
└── run.bat
```

## Mevcut windows_sysinfo Projesi
`D:\AICodeProje\PC_On_Hazirlik\BILGISAYAR_BILGI_TOPLA\windows_sysinfo`

5 Collector: NetworkCollector, HardwareCollector, SoftwareCollector, SystemCollector, DataCollector

## Önemli Kütüphaneler
- Pillow (görüntü oluşturma)
- psutil (sistem bilgileri)
- wmi (WMI sorguları)
- tkinter (GUI)

## Çalıştırma
```
python src\main.py
```

## Bilgi Öğesi Ekleme
Yeni bir bilgi öğesi eklemek için `src/info_tree.py` içinde ilgili `_build_*` fonksiyonuna:
```python
items.append(InfoItem(
    "benzersiz.id",      # id
    "Görünen Ad",        # label
    "Kategori",          # category
    "Alt Kategori",      # subcategory
    static_value="değer"  # veya getter=lambda: ...
))
```

## Derleme (EXE)
```powershell
pip install pyinstaller
pyinstaller --onefile --noconsole --name "WallpaperInformativeTool" --add-data "D:\AICodeProje\PC_On_Hazirlik\BILGISAYAR_BILGI_TOPLA\windows_sysinfo;windows_sysinfo" --add-data "help;help" --hidden-import wmi --hidden-import getpass --hidden-import pyodbc src/main.py
```

## GitHub
- **Repo:** https://github.com/Dev-Asri/Wallpaper-Informative-Tools
- **Token:** AGENTS.md içinde saklanmaz, `_open_help` token kullanmaz
- **Kullanıcı:** Dev-Asri
- **Proje:** Wallpaper-Informative-Tools
