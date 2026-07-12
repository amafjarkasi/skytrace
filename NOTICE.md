# Third-party sample media

This project downloads public media for demos. Licenses remain with upstream authors.

## Airplane / spotting videos (Wikimedia Commons)

| Local file | Source | License (as listed on Commons) |
| --- | --- | --- |
| `undershot_a380_yyz.webm` | [A380 Taking off from YYZ.webm](https://commons.wikimedia.org/wiki/File:A380_Taking_off_from_YYZ.webm) | CC BY 4.0 (LeoTor) |
| `undershot_flight_delhi.webm` | [Flight taking off.webm](https://commons.wikimedia.org/wiki/File:Flight_taking_off.webm) | CC BY-SA 3.0 (Subhashish Panigrahi) |
| `undershot_tejas.webm` | [Tejas takeoff from INS Vikrant.webm](https://commons.wikimedia.org/wiki/File:Tejas_takeoff_from_INS_Vikrant.webm) | GODL-India |
| `spotting_747_rctp.webm` | [Plane Spotting Atlas Air Cargo Boeing 747…](https://commons.wikimedia.org/wiki/File:Plane_Spotting_Atlas_Air_Cargo_Boeing_747_Runway_at_RCTP_with_ATC_%E6%A1%83%E5%9C%92%E6%A9%9F%E5%A0%B4%E8%B5%B7%E9%99%8D.webm) | See Commons file page |

## Drone videos (of drones, not filmed by drones)

| Local file | Source | License |
| --- | --- | --- |
| `drone_quadcopter_hover.webm` | [Quadcopter 20200202.webm](https://commons.wikimedia.org/wiki/File:Quadcopter_20200202.webm) | CC BY-SA 4.0 (Project Kei) |
| `drone_matrice_fire.webm` | [DJI Matrice 300RTK Feuerwehr…](https://commons.wikimedia.org/wiki/File:DJI_Matrice_300RTK_Feuerwehr_Drohne_LFV_Stmk_BFVFF.webm) | CC BY-SA 4.0 (Iswoar) |
| `drone_cobalt_vtol.webm` | [Armed Cobalt 110 G-VTOL Drone.webm](https://commons.wikimedia.org/wiki/File:Armed_Cobalt_110_G-VTOL_Drone.webm) | See Commons file page |
| `drone_peliscu.webm` | [Dron na Pelišcu 134429.webm](https://commons.wikimedia.org/wiki/File:Dron_na_Peli%C5%A1cu_134429.webm) | See Commons file page |

## Overhead stills → `overhead_apron_montage.mp4`

| Local file | Source |
| --- | --- |
| `overhead_farnborough.jpg` | [Farnborough aerial 2016](https://commons.wikimedia.org/wiki/File:Farnborough_Airport_Control_Tower_and_parked_aircraft,_aerial_2016_-_geograph.org.uk_-_4993873.jpg) (CC BY-SA 2.0) |
| `overhead_tansonnhat.jpg` | [Tansonnhat9.jpg](https://commons.wikimedia.org/wiki/File:Tansonnhat9.jpg) |
| `overhead_lappeenranta.jpg` | [Lappeenranta Airport apron](https://commons.wikimedia.org/wiki/File:Lappeenranta_Airport_apron_1986-07.jpg) |

## Detection models (Roboflow Universe)

| Alias | Model ID | Notes |
| --- | --- | --- |
| `airborne` | `airborne-object-detection/airborne-object-detection-4-aod4/6` | General airborne objects |
| `overhead_plane` | `skybot-cam/overhead-plane-detector/3` | Top-down / apron planes |
| `drone` / `drone_yolo11` | `godworkspace/drone-detection-dvhol/2` | Preferred drone detector (verified on hover clip) |
| `drone_v2` | `yolodrone/drone-object-detection-v2/1` | Earlier drone OD v2 |
| `drone_large` | `drone-detection-snemv/drone-detection-wpccn/1` | Large drone dataset (~9.6k images) |
| `tello` | `alexander437-gzzhf/tello_detect/1` | Tello-oriented drone detector |

Offline Ultralytics weights download into `weights/` (gitignored). Roboflow Inference caches Universe weights on first local run.

Models (Ultralytics YOLO / YOLO-World / Roboflow Inference weights) are subject to their own licenses when downloaded on first run.
