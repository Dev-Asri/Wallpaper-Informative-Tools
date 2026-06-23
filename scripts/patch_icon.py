"""Patch the app_icon.ico into the compiled EXE using win32api."""
import win32api, win32con, struct

exe = "dist/WallpaperInformativeTool.exe"
ico_path = "app_icon.ico"

with open(ico_path, "rb") as f:
    ico_data = f.read()

count = struct.unpack("<H", ico_data[4:6])[0]
entries = []
for i in range(count):
    off = 6 + i * 16
    w, h, colors, reserved, planes, bpp, sz, img_off = struct.unpack("<BBBBHHII", ico_data[off:off+16])
    img_data = ico_data[img_off:img_off+sz]
    entries.append({"w": w, "h": h, "bpp": bpp, "data": img_data, "size": sz})

print(f"Patching {count} icon images into {exe}")

handle = win32api.BeginUpdateResource(exe, False)
icon_ids = []

for i, e in enumerate(entries):
    icon_id = 100 + i
    win32api.UpdateResource(handle, win32con.RT_ICON, icon_id, e["data"])
    icon_ids.append(icon_id)
    print(f"  icon {i}: {e['w']}x{e['h']}")

group = struct.pack("<HHH", 0, 1, count)
for i, e in enumerate(entries):
    group += struct.pack("<BBBBHHII", e["w"], e["h"], 0, 0, 1, e["bpp"], e["size"], icon_ids[i])

win32api.UpdateResource(handle, win32con.RT_GROUP_ICON, 1, group)
win32api.EndUpdateResource(handle, False)
print("EXE icon patched successfully!")
