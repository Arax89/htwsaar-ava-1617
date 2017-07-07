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

## Nachrichtenformat:
Die Nachrichten, sowohl Kontroll- als auch Applikationsnachrichten, werden als JSON-formatierter Bytestream gesendet.
Das Nachrichtenformat ist in der Klasse NodeMessage in der Datei NodeMessage.py definiert. 

Nachrichten können einen folgenden Typen haben:
* control
* application
* unknown

Alle vom Benutzer von außen gesendete Nachrichten sind vom Typ "control". Die Knoten kommunizieren mit Nachrichten vom Typ "application". 
Eine Außnahme bildet hierbei die "stopall". Diese Nachricht, vom Typ "control" wird von außen durch den Benutzer an einen Knoten gesendet und dieser leitet sie an all seine Nachbarknoten weiter. Dieser wiederum leiten die Nachricht wieder an alle Nachbarn weiter. Dies geschieht solange, bis alle Knoten gestoppt wurden. 

Eine Nachricht sieht decodiert folgendermaßen aus:
    From: [sender], To: [empfänger], MsgType: [NachrichtenTyp], Msg: [Nachricht]
