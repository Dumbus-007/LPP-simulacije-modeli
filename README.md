# LPP-simulacije-modeli

## Vsebina repozitorija

- mapa ``lpp_gtfs``: vsebuje surove GTFS podatke za LPP
- mape modelov, ki vsebujejo kodo za generiranje grafa, graf v ``.graphml`` datoteki in rezultate simulacij v ``.csv`` datotekah
- python datoteko ``simulate_meetings1.py``, ki požene simulacijo na prvih dveh modelih
- ``README.md``

## Model 1: 

### Lastnosti grafa

**Vozlišča**: 905 postajališč LPP

**Uteži usmerjenih povezav**: število avtobusov, ki med danima postajališčema vozijo v enem dnevu
### Prvi rezultati 1000 simulacij
- Uspešnost srečanj: 85.20%
- Povprečno število korakov do srečanja: 1369.8 (zgornja meja: 5000 preden se simulacija prekine)

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 192x
 - Drama: 92x
 - Ajdovščina: 70x
 - Razstavišče: 63x
 - Pošta: 43x

## Model 2: 

### Lastnosti grafa

**Vozlišča**: 494 postajališč, od tega 411 "dvojnih" postajališč (vozlišča modela 1 so združena v pare npr.: Konzorcij/Pošta)
 - pravila združevanja: 
    1. združujemo zgolj vozlišča, ki niso sosednja v grafu modela 1 (torej niso zaporedna postajališča neke linije, ker želimo namreč združiti postajališči, ki ležita na nasprotnih straneh ceste),
    2. izmed nesosednjih vozlišč združimo tisti dve, ki sta si najbližji.

**Uteži usmerjenih povezav**: število avtobusov, ki med danima postajališčema vozijo v enem dnevu

### Rezultati prvih 1000 simulacij

- Uspešnost srečanj: 87.60%
- Povprečno število korakov do srečanja: 690.8 (zgornja meja: 5000)

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 132x
 - Ajdovščina: 79x
 - Drama: 59x
 - Konzorcij/Pošta: 52x
 - Razstavišče: 47x




