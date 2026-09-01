# LPP-simulacije-modeli

## Vsebina repozitorija

- mapa ``lpp_gtfs``: vsebuje surove GTFS podatke za LPP
- mape modelov:
  - model 1:
    - koda za pridobivanje podatkov: ``count_all_trips.py``
    - pridobljeni podatki: ``all_lines_trips.csv``
    - koda za generiranje grafa ``model1_graph_generation.py``
    - graf v ``.graphml`` datoteki
    - ``.csv`` datoteki z rezultati simulacij
    - jupyter notebook ``analiza_simulacij.ipynb`` z analizo najpogostejših krajev srečanj in testom ustreznosti krajev srečanj
  - model 2:
    - koda za generiranje grafa ``model2_graph_generation.py``
    - graf v ``.graphml`` datoteki
    - ``.csv`` datoteki z rezultati simulacij
    - jupyter notebook ``analiza_simulacij.ipynb`` z analizo najpogostejših krajev srečanj
  - model 3:
    - koda za generiranje grafa ``model3_graph_generation.py``
    - graf v ``.graphml`` datoteki
    - ``.csv`` datoteki z rezultati simulacij
    - jupyter notebook ``analiza_simulacij.ipynb`` z analizo najpogostejših krajev srečanj
    - koda za generiranje toplotnega zemljevida krajev srečanja ``heatmap.py``
    - datoteki ``nodes.csv`` in ``edges.csv``, ki omogočata lažji vnos multigrafa v program, kot je Gephi
  - sintetični primeri:
    - koda za izvedbo simulacij na sintetičnih grafih ``sinteticne_simulacije.py``
    - ``.csv`` datoteka z rezultati simulacij
    - jupyter notebook ``matrike_casov.ipynb`` z izračuni matrik pričakovanih časov srečanja
- python datoteka ``simulate_meetings1.py``, ki požene simulacijo na modelih 1 in 2
- python datoteka ``simulate_meetings3.py``, ki požene simulacijo na  modelu 3
- python datoteka ``animacija.py``, ki izvede animacijo dveh sprehodov na izbranem sintetičnem grafu
- jupyter notebook ``matrike_za_modele.ipynb`` z numeričnimi izračuni matrik pričakovanih časov srečanj za vse tri modele
- interaktivni toplotni zemljevid ``toplotni_zemljevid_srecanj.html``, ki ga zgenerira ``heatmap.py``
- ``README.md``

## Model 1: 

### Lastnosti grafa

**Vozlišča**: 857 postajališč LPP (brez Grosuplja)

**Uteži usmerjenih povezav**: število avtobusov, ki med danima postajališčema vozijo v enem dnevu
### Rezultati 5000 simulacij z naključnima začetnima vozliščema
- Trajanje: 70.08 s
- Uspešnost srečanj: 92.78%
- Povprečno število korakov do srečanja: 1288.8 (zgornja meja: $5 \cdot št. vozlišč = 4525$ preden se simulacija prekine)

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 1205x
 - Drama: 347x
 - Ajdovščina: 289x
 - Razstavišče: 277x
 - Pošta: 258x

### Rezultati 5000 simulacij z začetkom na **FMF** - Jadranski (proti centru) in **MF** - Kliničnem centru (proti centru)

- Trajanje: 51.78s
- Uspešnost srečanj: 92.64%
- Povprečno število korakov do srečanja: 1284.0

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 1193x
 - Drama: 383x
 - Ajdovščina: 296x
 - Razstavišče: 285x
 - Pošta: 245x


## Model 2: 

### Lastnosti grafa

**Vozlišča**: 461 postajališč, od tega 396 "dvojnih" postajališč (vozlišča modela 1 so združena v pare npr.: Konzorcij/Pošta)
 - pravila združevanja: 
    1. združujemo zgolj vozlišča, ki niso sosednja v grafu modela 1 (torej niso zaporedna postajališča neke linije, ker želimo namreč združiti postajališči, ki ležita na nasprotnih straneh ceste),
    2. izmed nesosednjih vozlišč združimo tisti dve, ki sta si najbližji,
    3. če imata taki vozlišči ujemajoče ime, ju prioritetno združimo.
    
**Uteži usmerjenih povezav**: število avtobusov, ki med danima postajališčema vozijo v enem dnevu

### Rezultati 5000 simulacij

- Trajanje: 29.46s
- Uspešnost srečanj: 96.08%
- Povprečno število korakov do srečanja: 654.1 (zgornja meja: 2460)

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 694x
 - Ajdovščina: 414x
 - Konzorcij/Pošta: 296x
 - Razstavišče: 262x
 - Drama: 236x

### Rezultati 5000 simulacij s fiksnima začetnima točkama (Jadranska, Klinični center)

- Trajanje: 22.53s
- Uspešnost srečanj: 97.20%
- Povprečno število korakov do srečanja: 511.3

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 747x
 - Ajdovščina: 422x
 - Konzorcij/Pošta: 385x
 - Drama: 355x
 - Razstavišče: 253x

## Model 3

### Lastnosti grafa

**Vozlišča**: 857 postajališč LPP

**Povezave**: 
- BUS - utež: povprečen čas čakanja v minutah, 
- WALK (med postajališči z razdaljo <300 m) - utež: čas sprehoda + povprečen čas čakanja na dani postaji v katerokoli smer

### Rezultati 5000 simulacij z naključnima začetnima vozliščema

- Trajanje: 111.18s
- Uspešnost srečanj: 99.72%
- Povprečno število korakov do srečanja: 779.4 (max korakov: $5 \cdot št. vozlišč = 4525$)

#### TOP 5 POSTAJALIŠČ SREČANJA
 - Ajdovščina: 508x
 - Pošta: 349x
 - Križanke: 329x
 - Drama: 289x
 - Bavarski dvor: 256x


### Rezultati 5000 simulacij s fiksnima začetnima točkama (Jadranska, Klinični center)

- Trajanje: 75.54s
- Uspešnost srečanj: 99.76%
- Povprečno število korakov do srečanja: 643.6

#### TOP 5 POSTAJALIŠČ SREČANJA
 - Ajdovščina: 551x
 - Pošta: 381x
 - Drama: 329x
 - Križanke: 327x
 - Bavarski dvor: 239x


## Uporaba UI

Koda je bila razvita s pomočjo uporabe Gemini Flash 3.6.