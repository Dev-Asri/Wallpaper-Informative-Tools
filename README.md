# WallpaperInformativeTool

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

---

**TR:** Duvar kağıdınızda sistem bilgilerinizi görüntüleyin — BGInfo'nun modern, özelleştirilebilir alternatifi.

**EN:** Display system information on your Windows wallpaper — a modern, customizable alternative to BGInfo.

---

## Özellikler / Features

| TR | EN |
|---|---|
| CPU, RAM, Disk, GPU, Anakart bilgileri | CPU, RAM, Disk, GPU, Motherboard info |
| Ağ arayüzleri ve IP adresleri | Network interfaces and IP addresses |
| İşletim sistemi, kullanıcı, lisans bilgileri | OS, user, license information |
| SQL Server ve ODBC bağlantıları | SQL Server and ODBC connections |
| Sürükle-bırak ile öğe konumlandırma | Drag & drop item positioning |
| Sola/Sağa/Yukarı/Aşağı hizalama | Left/Right/Top/Bottom alignment |
| Çoklu seçim ile toplu taşıma | Multi-select bulk move |
| Her öğe için ayrı yazı tipi, renk, boyut | Per-item font, color, size |
| Tam ekran ön izleme + zoom | Full-screen preview + zoom |
| Masaüstü ön izleme (geçici uygulama) | Desktop preview (temporary apply) |
| Çift dilli arayüz (Türkçe / English) | Bilingual interface (Türkçe / English) |
| Taşınabilir EXE, kurulum gerekmez | Portable EXE, no installation |

---

## Ekran Görüntüsü / Screenshot

*(Ekran görüntüsü eklenecek)*

---

## Hızlı Başlangıç / Quick Start

### EXE (Önerilen / Recommended)

1. [Son sürümü indirin](https://github.com/Uzman-lab/Wallpaper-Informative-Tools/releases) (WallpaperInformativeTool.exe)
2. Çift tıklayarak çalıştırın
3. Sol ağaçtan bilgi ekleyin, konumlandırın, duvar kağıdını uygulayın

### Python ile / From Source

```bash
git clone https://github.com/Uzman-lab/Wallpaper-Informative-Tools.git
cd Wallpaper-Informative-Tools
pip install -r requirements.txt
python src/main.py
```

### EXE Derleme / Build EXE

```powershell
pip install pyinstaller
pyinstaller --onefile --noconsole --name "WallpaperInformativeTool" ^
  --add-data "windows_sysinfo;windows_sysinfo" ^
  --add-data "help;help" ^
  --hidden-import wmi --hidden-import getpass --hidden-import pyodbc src/main.py
```

---

## Kullanım / Usage

Detaylı yardım için program içindeki **❓ Yardım** / **❓ Help** butonuna tıklayın veya `help/index.html` dosyasını açın.

For detailed help, click the **❓ Help** button inside the program or open `help/index.html`.

---

## Gereksinimler / Requirements

- Windows 10/11
- Python 3.10+ (source build)
- Pillow, psutil, wmi, pyodbc (optional)
- PyInstaller (optional, for EXE build)

---

## Proje Yapısı / Project Structure

```
├── src/                  # Python kaynak kodu / Source code
│   ├── main.py           # Giriş noktası / Entry point
│   ├── config_manager.py # JSON ayar yönetimi / Settings management
│   ├── info_tree.py      # Bilgi öğeleri modeli / Info item model
│   ├── i18n.py           # Dil sistemi / Language system
│   └── system_info.py    # Donanım/yazılım sorgulama / HW/SW queries
├── ui/
│   └── main_window.py    # Ana pencere / Main window
├── help/
│   ├── index.html        # Yardım (Türkçe) / Help (Turkish)
│   └── index_en.html     # Help (English)
├── requirements.txt
└── README.md
```

---

## Lisans / License

MIT License

Copyright (c) 2026 Asri Akdeniz

---

## İletişim / Contact

**Hazırlayan / Prepared by:** Asri Akdeniz  
**E-posta / Email:** asriakdeniz@gmail.com  
**Web:** [www.asriakdeniz.com](https://www.asriakdeniz.com)  
**GitHub:** [Uzman-lab](https://github.com/Uzman-lab)
