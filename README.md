# Introduktion & Översikt

Den här applikationen är designad för att hjälpa verksamheten att estimera antalet människor framför en stor scen genom
att använda bilder från flera olika kameror. Applikationen använder en AI-modell som förutsäger antalet personer baserat
på bildinmatningar från kamerorna. Denna lösning innefattar kamerainmatning, AI-baserad bildanalys och en
lösning för att effektivt spara resultaten. Målet är att skapa en robust och tillförlitlig tjänst som kan köras
kontinuerligt och ge uppskattningar med hög frekvens (var 10 sekund).

# Syfte, omfattning och mål

Syfte:
Syftet med applikationen är att automatisera processen att räkna människor som befinner sig på ett specifikt område
genom att analysera bilder från flera kameror med hjälp av en AI-modell.

Omfattning:
Projektet omfattar utveckling av en tjänst som kontinuerligt hämtar bilder från flera kameror, använder en AI-modell för
att förutsäga antalet människor i bilderna och lagrar resultaten för senare analys i Power BI / eller annan klient.
Vilket klientgränssnitt som utvecklas har inte bestämts ännu.

Mål:

- [ ] Implementera en tjänst för kontinuerlig bildinhämtning från flera kameror samtidigt.
- [ ] Integrera AI-modellen för att förutsäga antalet personer i de insamlade bilderna.
- [ ] Spara resultatet av förutsägelserna i ett format som kan användas av Power BI.
- [ ] Utveckla en klientapplikation eller använda Power BI för att visualisera och analysera data.

# Antaganden och begränsningar

Antaganden:

- Kamerorna kommer att vara statiska och riktade mot det område där människor ska räknas.
- Kamerorna har tillräcklig upplösning och bildkvalitet för att AI-modellen ska kunna göra noggranna förutsägelser.
- Kamerorna är anslutna till ett nätverk som tillåter att bilderna kan hämtas kontinuerligt.
- Den nätverksinfrastruktur som används för att strömma kameradata är tillförlitlig och har tillräcklig bandbredd.

Begränsningar:
- Estimeringarna är beroende av kamerornas bildkvalitet och synfält; områden som inte täcks av kamerorna kan inte inkluderas i beräkningarna. AI-modellen är så bra som den data den tränats på, och det kan finnas situationer där den
inte presterar optimalt (t.ex.vid ovanliga ljusförhållanden). Om högre precision önskas så måste vi träna på egen data. 
- Power BI har begränsningar i hur ofta data kan uppdateras och hur stora datamängder som kan hanteras. Så om vi vill ha en högre frekvens än vad Power BI klarar av, måste vi hitta en annan lösning för att visualisera och analysera data.


# Systemöversikt 
Systemarkitektur:
- **Kamerasystem:** Kameror som är riktade mot scenen och kontinuerligt strömmar video.
- **Tjänst för bildbehandling:** En tjänst som hämtar bilder från kamerorna, kör AI-modellen för att uppskatta antalet människor i bilderna och sparar resultaten.
- **Lagring:** Resultaten lagras i en databas och bilder i ett filsystem, formatet måste vara kompatibelt med Power BI.
- **Power BI Integration:** En rapport eller instrumentpanel i Power BI som hämtar och visualiserar data från lagringssystemet.

Mjukvaruarkitektur:
- **AI-Modell:** Pytorch-baserad modell (CLIP-EBC) för prediktion av antalet människor i en bild.
- **Kamera Manager:** Python-modul som hanterar inhämtning av bilder från kameror, förbereder bilderna för AI-modellen och returnerar resultaten.
- **Datahantering:** En komponent för att spara resultaten från AI-prediktionerna och förbereda data för analys i Power BI.

# Krav och begränsningar på systemet och programvaran
Systemkrav:
- **Server:** En kraftfull server med GPU-stöd (om möjligt) för att köra AI-modellen med hög frekvens.
- **Kameror:** RTSP-kompatibla kameror med tillräcklig upplösning och synfält.
- **Nätverk:** Stabil och snabb nätverksanslutning för att läsa bilddata från kamerorna.

# Systemkrav och design
**Kravdefinition:**
- Funktionella krav:
    - Systemet ska kunna hämta och processa bilder från flera kameror i realtid.
    - Systemet ska kunna förutsäga antalet människor i varje bild med hjälp av AI-modellen.
    - Resultaten ska sparas i en struktur som möjliggör enkel dataanalys och visualisering.

- Icke-funktionella krav:
  - Systemet ska vara skalbart för att kunna hantera fler kameror i framtiden.
  - Förutsägelser ska göras med en noggrannhet på minst 90 % under normala förhållanden.
  - Systemet ska kunna köras kontinuerligt och vara motståndskraftigt mot fel. (Denna kommer vara svår att implementera nu)

- Kravtilldelning:

  - Bildinhämtning: Hanteras av kameramanagern och kamerakomponenter.
  - AI-prediktion: Hanteras av AI-modulen.
  - Datahantering och lagring: Hanteras av en dedikerad datakomponent som sparar prediktionerna.
  - Visualisering: Hanteras av Power BI-rapporter som hämtar data från datalagret. Alternativt en egen klientapplikation.

# Utvecklingsoutline och utvecklingssteg
- **Steg 1: Systemdesign**
  - [ ] Specificera detaljerna för varje systemkomponent och integration.
  - [ ] Definiera databasstrukturen för att lagra prediktionerna.
  
- **Steg 2: Implementering av Kamera Manager**
  - [ ] Implementera och testa kameraströmning och bildinhämtning.
  - [ ] Lägg till funktionalitet för att hantera flera kameror samtidigt.
  
- **Steg 3: Implementering av AI-modul**
  - [ ] Integrera den fördefinierade AI-modellen i systemet.
  - [ ] Testa prediktioner på bilder från kameror och justera modellen efter behov.

- **Steg 4: Implementering av Datahantering**
  - [ ] Implementera datalagring.
  - [ ] Testa att data lagras korrekt och att den kan hämtas till Power BI.

- **Steg 5: Testning och Validering**
  - [ ] Utför omfattande tester för att säkerställa att prediktionerna är tillförlitliga.
  - [ ] Validera att hela systemet fungerar i en produktionsliknande miljö.
  
- **Steg 6: Implementation av Power BI-rapportering**
  - [ ] Bygg och konfigurera rapport i Power BI.
  - [ ] Testa att data från systemet korrekt presenteras och kan analyseras.
  
- Steg 7: Slutgiltig granskning och lansering
  - [ ] Granska systemet med alla intressenter.
  - [ ] Lansera systemet för produktionsanvändning.


# Exempel på JSON-konfiguration
För att kunna köra applikationen så måste en config.json-fil skapas.
Nedan följer ett exempel på en JSON-konfigurationsfil som används för att definiera områden och tillhörande kameror i applikationen.

```json
{
    "areas": [
        {
            "name": "Stora scen",
            "cameras": [
                {
                    "name": "Stora scen sida",
                    "rtsp_url": "rtsp://172.22.175.138/rtsp/defaultPrimary?streamType=u",
                    "user": "CAMERA_USER",
                    "password": "CAMERA_PASSWORD",
                    "crop_polygon": [
                        [23.28, 100],
                        [18.8, 43.27],
                        [47.44, 38.28],
                        [74.16, 55.78],
                        [100, 81.96],
                        [100, 100]
                    ]
                },
                {
                    "name": "Stora scen front",
                    "rtsp_url": "rtsp://172.22.175.142/rtsp/defaultPrimary?streamType=u",
                    "user": "CAMERA_USER",
                    "password": "CAMERA_PASSWORD",
                    "crop_polygon": [
                        [0.00, 100.00],
                        [0.00, 47.96],
                        [16.32, 0.00],
                        [81.93, 0.00],
                        [95.38, 6.69],
                        [93.62, 17.39],
                        [100.00, 32.77],
                        [100.00, 100.00]
                    ]
                }
            ]
        }
    ]
}
```
- **areas:** En lista över definierade områden. Tanken är att framåt ha utrymme att addera ytterligare områden. OBS! Just nu hanteras endast ett område.
  - **name:** Namnet på området.
    - **cameras:** En lista över kameror som är riktade mot området.
      - **name:** Namnet på kameran.
      - **rtsp_url:** RTSP-URL för att strömma video från kameran.
      - **user:** Användarnamnet för att ansluta till kameran.
      - **password:** Lösenordet för att ansluta till kameran.
      - **crop_polygon:** En lista över punkter som definierar ett polygon som beskriver det område som ska analyseras i bilden.
      