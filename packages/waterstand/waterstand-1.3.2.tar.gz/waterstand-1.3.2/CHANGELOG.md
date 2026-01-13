## Version 1.3.2
2026-01-04

### Gewijzigd
* Dependencies bijgewerkt

### Hersteld
  * Geen crash als er geen actuele data is

## Version 1.3.1
2025-06-11

### Gewijzigd
* Dependencies bijgewerkt

### Hersteld
* Geen crash als er geen data is

## Version 1.3.0
2025-06-08

### Nieuw
Retry na timeout bij ophalen waterstand
### Gewijzigd
* Type bij variabelen
* Dependencies bijgewerkt

## Version 1.2.2
2025-05-18

### Nieuw
* Download-URL in projectfile
* Extra check met mypy 

### Gewijzigd
* `requests` gebruiken in plaats van `urllib`
* Documentatie in source uitgebreid

### Verwijderd
* scipts voor upload naar pypi.org

## Version 1.2.1
2025-01-25

### Nieuw
* Gebruik maken van github actions voor
  * pylint
  * pytest
  * upload release to pypi.org
### Gewijzigd
* Alleen echte requirements
* Diverse afhankelijkheden bijgewerkt naar nieuwe versie
* Verbeteringen in de code nav checks

## Version 1.2.0
2025-01-01
### Nieuw
* Deze release notes.
### Gewijzigd
* Diverse afhankelijkheden bijgewerkt naar nieuwe versie.
* Test-coverage ingebouwd, met minimum van 90%.
* Configuratie van pylint in coverage in `pyproject.toml`.
* Virtual env (venv) laden met `env.sh` flexibeler gemaakt.
### Hersteld
* Als de huidige stand niet in de gegevens staat wordt -99

## Version 1.1.1
Datum: 2025-12-20
### Hersteld
* Resultaat had soms veld `result` in plaats van `resultaat`. Dat is aangepast naar altijd `resultaat`. 

## Version 1.1.0
Datum: 2025-12-12
### Gewijzigd
* Resultaat heeft veld `resultaat` met status `OK` of `NOK`. Bij `NOK` is er een toelichting.

## Version 1.0.0
Datum: 2025-12-09
### Nieuw
* Eerste versie in productie

## Version a.b.c
2025-xx-yy

### Nieuw
### Gewijzigd
### Hersteld
### Verwijderd
