---
title: HTW Saar AVA Übung 3
parent: index.md
---

# HTW Saar AVA Übung 3

## Voraussetzung
* Endpoint-Datei enthält genau so viele Einträge, wie Knoten gestartet werden
* Endpoint-Datei enthält Port und ID aller Knoten die gestartet werden

## Starten der Knoten
Die Knoten werden mit Hilfe des bashscripts "start.sh" gestartet.

    ./start.sh
    
Die Knoten können auch einzeln manuell mit Hilfe folgendes Befehls gestartet werden:

    python3 LamportMain.py nid endpointfile
    
        nid           The ID the node shall have
        endpointfile  The path to the endpointfile

## Erläuterung der Idee
Es sollte der Lamport-Algorithmus für den wechselseitigen Ausschluss bzgl. einer Ressource mit Hilfe der Lamport-Zeit und lokalen Request-Queues realisiert werden. 

Die Prozesse sollen zu jedem beliebigen Zeitpunkt den Schreibzugriff auf die Ressource beantragen können.
Dazu sendet ein Prozess eine Request-Nachricht mit Zeitstempel an alle anderen Prozesse. Diese quittieren den Erhalt des request mit einer Reply-Message und fügen den request ihrer lokalen request queue hinzu. Diese ist als PriorityQueue implementiert. D.h. requests mit dem kleinsten Zeitstempel haben eine höhere Priorität als requests mit höheren Zeitstempeln. 

Hat der anfragende Prozess von allen anderen Prozessen eine Reply-Nachricht erhalten und befindet sich sein Request an der Spitze seiner Request-Queue, so betritt er die _critical section_

## Nachrichtenformat:
Die Nachrichten werden als JSON-formatierter Bytestream gesendet.Das Nachrichtenformat ist in der Klasse LamportMessage in der Datei LamportMessage.py definiert. 

Nachrichten können einen folgenden Typen haben:
* Acknowledge
* Request 
* Ready 
* Register
* Reply 
* Release
* Remove 
* Terminate 
Wobei _Acknowledge_, _Ready_ und _Register_ in der endgültigen Abgabefassung nicht benutzt werden. 

## Softwarestruktur
Ein Prozess besteht aus folgenden drei Threads:
* lamportListener-Thread
* lamportInterpreter-Thread
* lamportWorker-Thread

Der lamportListener-Thread empfängt Nachrichten von anderen Prozessen und fügt diese einer geteilten MessageQueue zu.
Aus diese MessageQueue entnimmt der lamportInterpreter-Thread die Nachrichten und interpretiert diese. Jenach Typ der Nachricht wird entsprechend reagiert. Der lamportWorker-Thread sendet nach start die RequestNachricht an alle anderen Prozesse und wartet dann darauf, dass der lamportInterpreter-Thread die Freigabe zum Betreten der _critical section_ gibt. 
Hat der Worker-Thread drei mal eine 0 eingelesen, sendet er außerdem die Terminierungs-Nachricht an seinen Partnerprozess und beendet. 
