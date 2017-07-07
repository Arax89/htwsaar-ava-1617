# HTW Saar AVA Übung 1

## Erzeugen eines Graphen:
    python3 graphgen.py [-h] n m savepath
    
    positional arguments:
        n           Anzahl der Knoten
        m           Anzahl der Kanten. Falls m > (n*(n-1))/2 wird die maximale Anzahl an Kanten gesetzt.
        savepath    Speicherort der Graphviz-Datei
        

## Starten der Knoten:
    python3 init.py [-h] [--c C] nodepath graphpath
    
    positional arguments:
        nodepath    Pfad zur Endpoint-Datei
        graphpath   Pfad zur Graphviz-Datei
        
    optional arguments:
        -h, --help  Zeigt die Hilfe
        --c C       Glaubensgrenze als Ganzzahl. Standard ist 1
 
## Senden von Kontrollnachrichten:
    python3 send.py endpoints nid msg
    
    positional arguments:
        endpoints   Pfad zur Endpoint-Datei
        nid         ID des Empfänger-Knoten
        msg         Die Nachricht die gesendet werden soll
