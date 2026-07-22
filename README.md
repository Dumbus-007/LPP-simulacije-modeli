# LPP-simulacije-modeli

## Vsebina repozitorija

- mapa ``lpp_gtfs``: vsebuje surove GTFS podatke za LPP
- mape modelov, ki vsebujejo kodo za generiranje grafa, graf v ``.graphml`` datoteki in rezultate simulacij v ``.csv`` datotekah
- python datoteko ``simulate_meetings1.py``, ki požene simulacijo na prvih modelih 1, 1.5 in 2
- python datoteko ``simulate_meetings3.py``, ki požene simulacijo na  modelu 3
- ``README.md``

## Model 1: 

### Lastnosti grafa

**Vozlišča**: 905 postajališč LPP

**Uteži usmerjenih povezav**: število avtobusov, ki med danima postajališčema vozijo v enem dnevu
### Rezultati 5000 simulacij z naključnima začetnima vozliščema
- Uspešnost srečanj: 83.88%
- Povprečno število korakov do srečanja: 1347.7 (zgornja meja: $5 \cdot št. vozlišč = 4525$ preden se simulacija prekine)

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 1106x
 - Drama: 333x
 - Ajdovščina: 283x
 - Razstavišče: 250x
 - Pošta: 216x

### Rezultati 5000 simulacij z začetkom na **FMF** - Jadranski (proti centru) in **MF** - Kliničnem centru (proti centru)

Uspešnost srečanj: 92.82%
Povprečno število korakov do srečanja: 1331.4

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 1175x
 - Drama: 370x
 - Ajdovščina: 329x
 - Razstavišče: 276x
 - Pošta: 228x

## Model 1.5:

### Lastnosti grafa

**Vozlišča**: 132 postajališč, ki imajo vhodno stopnjo večjo od ena

**Uteži usmerjenih povezav**: število avtobusov, ki med danima postajališčema vozijo v enem dnevu

### Rezultati 5000 simulacij

Uspešnost srečanj: 93.60%
Povprečno število korakov do srečanja: 161.3 (zgornja meja: 660)

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 1147x
 - Drama: 506x
 - Ajdovščina: 426x
 - Pošta: 275x
 - Razstavišče: 248x

### Rezultati 5000 simulacij z začetkom na Hajdrihovi (proti centru) in Ambroževem trgu (proti centru)

Uspešnost srečanj: 97.30%
Povprečno število korakov do srečanja: 169.7 (zg. meja: 660)

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 1202x
 - Drama: 507x
 - Ajdovščina: 483x
 - Pošta: 274x
 - Razstavišče: 256x


## Model 2: 

### Lastnosti grafa

**Vozlišča**: 492 postajališč, od tega 413 "dvojnih" postajališč (vozlišča modela 1 so združena v pare npr.: Konzorcij/Pošta)
 - pravila združevanja: 
    1. združujemo zgolj vozlišča, ki niso sosednja v grafu modela 1 (torej niso zaporedna postajališča neke linije, ker želimo namreč združiti postajališči, ki ležita na nasprotnih straneh ceste),
    2. izmed nesosednjih vozlišč združimo tisti dve, ki sta si najbližji,
    3. če imata taki vozlišči ujemajoče ime, ju prioritetno združimo.
    
**Uteži usmerjenih povezav**: število avtobusov, ki med danima postajališčema vozijo v enem dnevu

### Rezultati 5000 simulacij

- Uspešnost srečanj: 86.26%
- Povprečno število korakov do srečanja: 642.5 (zgornja meja: 2460)

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
- Bavarski dvor: 554x
 - Ajdovščina: 397x
 - Konzorcij/Pošta: 308x
 - Drama: 231x
 - Razstavišče: 190x

### Rezultati 5000 simulacij s fiksnima začetnima točkama (Jadranska, Klinični center)

Uspešnost srečanj: 98.38%
Povprečno število korakov do srečanja: 522.1

#### TOP 5 POSTAJALIŠČ, KJER STA SE NAJPOGOSTEJE SREČALA
 - Bavarski dvor: 611x
 - Ajdovščina: 506x
 - Drama: 393x
 - Konzorcij/Pošta: 379x
 - Razstavišče: 235x

## Model 3

### Lastnosti grafa

**Vozlišča**: 905 postajališč LPP

**Povezave**: 
- BUS - utež: povprečen čas čakanja v minutah, 
- WALK (med postajališči z razdaljo <300 m) - utež: čas sprehoda + povprečen čas čakanja na dani postaji v katerokoli smer

### Rezultati 5000 simulacij z naključnima začetnima vozliščema

- Uspešnost srečanj: 90.84%
- Povprečno število korakov do srečanja: 609.6 (max korakov: $5 \cdot št. vozlišč = 4525$)

#### TOP 5 POSTAJALIŠČ SREČANJA
 - Drama: 664x
 - Križanke: 559x
 - Ajdovščina: 375x
 - Aškerčeva: 318x
 - Konzorcij: 262x


### Rezultati 5000 simulacij s fiksnima začetnima točkama (Jadranska, Klinični center)

Uspešnost srečanj: 100.00%
Povprečno število korakov do srečanja: 438.2

#### TOP 5 POSTAJALIŠČ SREČANJA
 - Drama: 820x
 - Križanke: 684x
 - Aškerčeva: 401x
 - Ajdovščina: 383x
 - Pošta: 345x

## Sintetični primeri

**20 vozlišč**, **obojesmerne povezave**, **uteži = 1**

### Rezultati 500 simulacij (zg. meja: 5*št.vozlišč):

| Topologija | Uspešnost srečanj (%) | Povprečni koraki |
| :--- | :---: | :---: |
| Path | 44.8 | 26.0 |
| Ring | 46.4 | 28.2 |
| Star | 90.6 | 1.0 |
| Lattice | 50.6 | 13.8 |
| Lollipop | 77.2 | 30.5 |
| Tadpole | 47.2 | 25.6 |
| Sun | 52.6 | 17.9 |

### Rezultati 1000 simulacij (zg. meja: 10*št.vozlišč):

|Topologija | Uspešnost srečanj (%) | Povprečni koraki |
| :--- | :---: | :---: |
|      Path  |  47.8  | 42.7
|      Ring  |  50.1  | 33.8
|      Star  |  91.4  |  1.0
|   Lattice  |  47.7  | 14.4
|  Lollipop  |  93.6  | 48.8
|   Tadpole  |  46.3  | 35.5
|       Sun  |  49.9  | 18.1

