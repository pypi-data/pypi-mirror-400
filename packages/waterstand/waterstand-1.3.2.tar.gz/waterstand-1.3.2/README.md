# waterstand
Ophalen van de actuele waterstand.

Gegevens komen van Rijkswaterstaat.

## Gebruik
Installeer de package:  
`pip install waterstand`  

Of zet waterstand in `requirements.txt` en installeer het op die manier.  
`pip install -r requirements.txt --upgrade`

Ga naar [de site van RWS](https://waterinfo.rws.nl/#/publiek/waterhoogte) en 
zoek daar een locatie waarvan je hoogte wilt ophalen. Wanneer je de locatie aanklikt 
en op meer details klikt, verschijnt in de adresbalk de naam en afkorting van deze
locatie. Bijvoorbeeld voor Lobith staat er ...waterhoogte/Lobith%28LOBI%29/details... in
het pad.
Neem het voor de naam het deel tussen de `hoogte/` en `%28` en voor de afkorting het deel
tussen `%28` en `%29`. In het voorbeeld wordt dat dus `Lobith` en `LOBI`.
Het meest eenvoudige programma wordt dan als volgt:
```Python
from waterstand import *
print(haalwaterstand('Lobith', 'LOBI'))
```
