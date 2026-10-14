"""Copies/converts the art from ../art-jobs/out and ../frontend into demo/public/assets (run from repo root or demo/)."""
import json, shutil, sys
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[2]
O = R / "art-jobs/out"
D = Path(__file__).resolve().parents[1] / "public/assets"
if D.exists(): shutil.rmtree(D)
D.mkdir(parents=True)

def cp(src, dst):
    dst = D / dst; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy(src, dst)

def webp(src, dst, w=1920, q=82, alpha=False):
    im = Image.open(src).convert("RGBA" if alpha else "RGB")
    h = round(im.height * w / im.width); im = im.resize((w, h), Image.LANCZOS)
    dst = D / dst; dst.parent.mkdir(parents=True, exist_ok=True); im.save(dst, "WEBP", quality=q, method=6)

# rooms (composites -> webp) + manifests
webp(O/"G_rooms_galley_locker/galley_room.png", "rooms/galley.webp")
webp(O/"G_rooms_galley_locker/locker_room.png", "rooms/locker.webp")
webp(O/"H_rooms_reactor_switch/check/reactor_composite.png", "rooms/reactor.webp")
webp(O/"H_rooms_reactor_switch/check/switchboard_composite.png", "rooms/switchboard.webp")
for j in ["G_rooms_galley_locker/galley.json","G_rooms_galley_locker/locker.json","H_rooms_reactor_switch/reactor.json","H_rooms_reactor_switch/switchboard.json"]:
    d = json.load(open(O/j)); d.pop("mae", None)
    (D/"rooms").mkdir(exist_ok=True, parents=True); json.dump(d, open(D/"rooms"/Path(j).name, "w"), separators=(",",":"))
G = O/"G_rooms_galley_locker/objects"
for f in ["galley_table","locker_door_frame","locker_door_leaf_left","locker_door_leaf_right","locker_clock_hand_hour","locker_clock_hand_minute","locker_beacon"]:
    cp(G/f"{f}.svg", f"rooms/obj/{f}.svg")
cp(O/"G_rooms_galley_locker/locker_lights.svg", "rooms/locker_lights.svg")

# stations
for s in ["station_keypad_front","station_switchboard_front","station_scope_front","station_tape_front","timeclock_front"]:
    cp(O/f"K_props_stations/{s}.svg", f"props/{s}.svg")

# task panels
for p in ["panel_keypad","panel_switchboard"]:
    cp(O/f"C_task_panels/{p}.svg", f"panels/{p}.svg")
for f in (O/"C_task_panels/task_parts").glob("*.svg"):
    cp(f, f"panels/parts/{f.name}")
cp(O/"C_task_panels/panels.json", "panels/panels.json")

# UI
for f in (O/"A_icons/svg").glob("*.svg"): cp(f, f"ui/icons/{f.name}")
for f in (O/"B_ui_frames").glob("*.svg"): cp(f, f"ui/{f.name}")
cp(O/"B_ui_frames/nineslice.json", "ui/nineslice.json")

# brand & screens
cp(O/"O_brand_screens/logo.svg", "brand/logo.svg")
webp(O/"O_brand_screens/arcade.png", "brand/arcade.webp", w=900, q=88, alpha=True)
cp(O/"O_brand_screens/screens.json", "screens/screens.json")
for f in (O/"O_brand_screens/screens").glob("*_1920.webp"): cp(f, f"screens/{f.name}")
for f in (O/"O_brand_screens/screens").glob("*_rays.svg"): cp(f, f"screens/{f.name}")
for f in ["arcade_32x64.png","arcade_in_town.png"]: cp(O/f"F_brand_arcade/{f}", f"town/{f}")
cp(R/"frontend/public/assets/tilesets/tuxmon-sample-32px-extruded.png", "town/tileset.png")

# emergency button
for f in ["base","button_idle","button_lit","button_pressed","button_disabled","dome_back_strip","dome_front_strip","padlock","glow_ring_off","glow_ring_on","glow_ring_bright"]:
    cp(O/f"E_button_doors/parts/{f}.png", f"button/{f}.png")
cp(O/"E_button_doors/emergency_button_rig.json", "button/rig.json")

# cosmetics (hats + visors + toppers + decals used by the roster)
for f in (O/"M_cos_hats/svg").glob("*.svg"): cp(f, f"cos/{f.name}")
cp(O/"M_cos_hats/cosmetics.json", "cos/hats.json")
for f in (O/"N_cos_rest").glob("*.svg"): cp(f, f"cos/{f.name}")
cp(O/"N_cos_rest/cosmetics.json", "cos/rest.json")

# poses (fallen marker art fallback)
cp(O/"O_brand_screens/poses/pose_fallen_headless.png", "poses/fallen.png")
tot = sum(p.stat().st_size for p in D.rglob("*") if p.is_file())
print(f"staged {tot/1e6:.1f} MB")
