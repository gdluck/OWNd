<!-- ccr-projects-attribution: {"github_login":"gdluck"} -->
_Requested by **A** · [project thread](https://claude.ai/code/project/chan_0159fxdtgHJqHFpnbme29u2L?thread=cmsg_0159fxdtgHJqHFpnbme29u2LKAHKjwFDvBofhmvrZKsE8m)_


Before: `*#18*51*1200#1*255##` produced an `OWNEnergyEvent` with no message type and no value.

After: `message_type = auto_update_interval`, `update_interval = 255` (seconds, `0` = the stream stopped), `energy_type = 1` (1 electricity, 2 gas, 3 heat, 4 water).

### Evidence

**libqtdevices TS10_1_0_23.** `energy_device.cpp`:
```cpp
 50: enum EnergyType
 52: 	TYPE_ELECTRICITY = 1,
 53: 	TYPE_GAS = 2,
 54: 	TYPE_HEAT = 3,
 55: 	TYPE_WATER = 4,
111: 	_DIM_STATE_UPDATE_INTERVAL             = 1200,   // used to detect start/stop of automatic updates
251: 	emit sendFrame(createDimensionFrame("18", QString("#%1#%2*%3").arg(_DIM_STATE_UPDATE_INTERVAL)
252: 					    .arg(modeToEnergyType(mode)).arg(UPDATE_INTERVAL), where));
289: void AutomaticUpdates::handleAutomaticUpdate(OpenMsg &msg)
291: 	int time = msg.whatArgN(0);
301: 	if (time == 0)
303: 		qDebug("Received auto-update stop frame");
307: 		case UPDATE_AUTO:
308: 			// restart automatic updates since we need them
309: 			sendUpdateStart();
719: 	else if (what == _DIM_STATE_UPDATE_INTERVAL && msg.whatArgCnt() == 1)
721: 		current_updates->handleAutomaticUpdate(msg);
```
The client sends `*#18*W*#1200#type*time##` to start the updates and parses the `1200#type*time` reply, re-arming the stream when `time` is 0.

**Firmware.** bt_supervisione, identical on MyHomeServer1, F454, F459 and F461 (`results/spv*.tsv`):

| Frame | Reply | Bus body |
|---|---|---|
| `*#18*51*#1200#1*255##` | ACK | `D1 A1 02 32 00 02 1D FF` |
| `*#18*51*#1200#1*0##` | ACK | `D1 A1 02 32 00 02 1D 00` |
| `*#18*51*#1200#2*255##` | ACK | `D1 A1 02 32 00 02 82 FF` |
| `*#18*51*1200##` | NACK | none |
| `*#18*51*1200#1##` | NACK | none |

The write form carries the type (`1D` electricity, `82` gas) and the interval (`FF` / `00`) on the bus; the bare request forms never leave the gateway, which is why OWNd should expect the reply only as an answer to the write (and why MyHOME's `*#18*W*1200##` poll is dead, noted separately in #649's companion report).

### How

`OWNd/message/energy.py`: one `elif self._dimension == 1200` branch, two properties, the `MESSAGE_TYPE_AUTO_UPDATE_INTERVAL` constant exported from `OWNd/message/__init__.py`. Tests: `tests/test_who18_auto_update_reply.py`. `pytest`: 1240 passed, 1 skipped.

---

**How to check.** `libqtdevices` quotes are from tag `TS10_1_0_23` of OpenWebNet-HA/libqtdevices (BTicino's 2010 touch-screen client, used only as a second client, not as the reference). Firmware rows are replays of the exact frame on the original gateway translator binaries (ARM, from the MyHomeServer1, F454, F459, F461 and F450 images) under QEMU on a fake SCS bus: `ACK` = `*#*1##`, `NACK` = `*#*0##`, the bus body is what the program put on the SCS bus (hex, without the A8 / checksum / A3 framing). Spec = Legrand/BTicino "Open Web Net Language, WHO = 4" v2.0.0 (2013-11-27). Raw logs, command lists, the harness and the report are in [firmware_validation.zip](https://github.com/gdluck/OWNd/raw/firmware-validation-data/firmware_validation.zip) (`results/<program>[_<image>].tsv`, `results/*.cl` / `*.stub` / `*.mon`, `REPORT.md`). The firmware images themselves are not included.

Split out of #86 so each change can be checked on its own; all eight slices merge together without conflicts (1271 tests pass on the union).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018oHp1P4vxxoFnaLUUZpbpZ
