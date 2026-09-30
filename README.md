# esphome-ix3212-pdm

ESPHome firmware for an M5Stack CoreS3 that controls up to four Enovation / Murphy IX3212 power distribution modules over CAN (J1939), gives a local touchscreen GUI, and bridges to Home Assistant over MQTT.

**Status:** pre-alpha. The CAN component is not written yet. `prototype/` holds a mock-data LVGL GUI that runs on the CoreS3 today.

**Spec:** kept in Aaron's Outline vault (`1 - The Van › projects › pdm-controller`).

## prototype/

| File | What it is |
| --- | --- |
| `base.yaml` | CoreS3 hardware and device identity |
| `gen2.py` | Generates the LVGL UI from mock channel data and appends it to `base.yaml` |
| `pdm_ui_v14.yaml` | Generated output — paste into the ESPHome dashboard and install |

Regenerate: `pip install pyyaml && python3 prototype/gen2.py`

The YAML expects these keys in ESPHome's `secrets.yaml`: `wifi_ssid`, `wifi_password`, `wifi_ap_password`, `api_encryption_key`.

Findings from running it on hardware: 32 px is the minimum usable touch target on the CoreS3 (~200 ppi); poll touch at 16 ms or quick swipes are missed; anchor the LVGL keyboard with `align: BOTTOM_MID`, not `y:`.
