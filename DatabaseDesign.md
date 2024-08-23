## 1. Tabell: `Areas`
Den här tabellen representerar olika områden som kan innefatta en eller flera kameror.

| Fält          | Datatyp   | Beskrivning                            |
| ------------- | --------- | -------------------------------------- |
| `area_id`     | INTEGER   | Unikt ID för området (Primärnyckel).   |
| `area_name`   | TEXT      | Namn på området (ex. "Stora scenen").  |
| `description` | TEXT      | Beskrivning av området.                |

## 2. Tabell: `Cameras`
Den här tabellen innehåller information om de olika kamerorna.

| Fält           | Datatyp   | Beskrivning                            |
| -------------- | --------- | -------------------------------------- |
| `camera_id`    | INTEGER   | Unikt ID för kameran (Primärnyckel).   |
| `camera_name`  | TEXT      | Namn på kameran (ex. "Kamera 1").      |
| `rtsp_url`     | TEXT      | RTSP URL för kameran.                  |
| `area_id`      | INTEGER   | Referens till området kameran tillhör (Utländsk nyckel till `Areas`). |

## 3. Tabell: `Predictions`
Den här tabellen lagrar totalprediktionerna för ett område, vilket kan innefatta data från flera kameror.

| Fält             | Datatyp   | Beskrivning                                    |
| ---------------- | --------- | ---------------------------------------------- |
| `prediction_id`  | INTEGER   | Unikt ID för prediktionen (Primärnyckel).      |
| `area_id`        | INTEGER   | Referens till området (Utländsk nyckel till `Areas`). |
| `timestamp`      | DATETIME  | Tidpunkt för prediktionen.                     |
| `total_estimate` | INTEGER   | Totalt estimerat antal människor i området.    |

## 4. Tabell: `PredictionDetails`
Den här tabellen innehåller detaljer för varje enskild bild som används för att göra prediktionen. Varje rad i denna tabell representerar en prediktion från en specifik kamera vid en specifik tidpunkt.

| Fält              | Datatyp   | Beskrivning                                        |
| ----------------- | --------- | -------------------------------------------------- |
| `detail_id`       | INTEGER   | Unikt ID för prediktionsdetaljen (Primärnyckel).   |
| `prediction_id`   | INTEGER   | Referens till prediktionen (Utländsk nyckel till `Predictions`). |
| `camera_id`       | INTEGER   | Referens till kameran som tagit bilden (Utländsk nyckel till `Cameras`). |
| `image_path`      | TEXT      | Sökväg till den sparade bilden på disken.          |
| `estimated_count` | INTEGER   | Estimerat antal människor i denna specifika bild.  |
| `timestamp`       | DATETIME  | Tidpunkt när bilden togs.                          |

## 5. Tabell: `ScheduledTasks`
Den här tabellen innehåller konfigurationer för automatiska hämtningar och prediktioner, inklusive vilket område som ska övervakas och hur ofta dessa operationer ska utföras.

| Fält             | Datatyp   | Beskrivning                                                       |
| ---------------- | --------- | ----------------------------------------------------------------- |
| `task_id`        | INTEGER   | Unikt ID för schemalagda uppgiften (Primärnyckel).                |
| `area_id`        | INTEGER   | Referens till området som ska övervakas (Utländsk nyckel till `Areas`). |
| `frequency`      | INTEGER   | Frekvens för automatiska hämtningar och prediktioner (i minuter). |
| `last_run_time`  | DATETIME  | Tidpunkt då uppgiften senast kördes.                              |
| `next_run_time`  | DATETIME  | Tidpunkt då uppgiften är planerad att köras nästa gång.           |
