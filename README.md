# ris-scraper

Lädt öffentliche Dokumente aus dem Rösrather Ratsinformationssystem http://ratsinfo.roesrath.de/ratsinfo/roesrath/
für die lokale Archivierung, bessere Durchsuchbarkeit und ähnliche Zwecke.

## Anwendung

```nohighlight
git clone https://github.com/gruene-roesrath/ris-scraper.git
cd ris-scraper
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt

python scrape.py
```

Es werden Dokumente erfasst, die in Sitzungen innerhalb eines vorgegebenen
Zeitraums behandelt wurden. Dieser Zeitraum kann im Script angepasst werden.

Geladene Dokumente werden im Unterordner `documents` abgelegt und erhalten
den ursprünglichen Dateinamen. Zusammengehörige Dateien werden in einem 
gemeinsamen Ordner abgelegt, der nach der internen Vorlagennummer des Systems
benannt ist. Diese Nummer entspricht der, die in der URL der Detailseite in 
diesem Format verwendet wird:

    http://ratsinfo.roesrath.de/ratsinfo/roesrath/Proposal.html?select=<nummer>
