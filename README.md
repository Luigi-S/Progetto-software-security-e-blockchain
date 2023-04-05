## Progetto Software Security & Blockchain
         ______         _______  
        |       \       |       \ 
        | $$$$$$$\      | $$$$$$$\
        | $$__/ $$      | $$__/ $$
        | $$    $$      | $$    $$
        | $$$$$$$\      | $$$$$$$\
        | $$__/ $$      | $$__/ $$
        | $$    $$      | $$    $$
        \ $$$$$$$/      \ $$$$$$$/

            --BLOCK BALANCER--

BlockBalancer é una dApp che implementa un prototipo di ***load balancer*** per gli ***smart contract*** deployati su un insieme di blockchain Ethereum.

## Guida all'utilizzo (Linux o MacOS)
Per utilizzare l'applicazione è necessario installare sul proprio sistema `docker` e `docker-compose`.

Clonare il repository con:
```
git clone https://github.com/Luigi-S/Progetto-software-security-e-blockchain.git
```

Posizionandosi nella cartella di progetto eseguire `install.sh` per creare le immagini docker necessarie.

Nello stesso *path* è possibile eseguire gli script:
- `start.sh` per avviare l'applicazione
- `stop.sh` per chiudere l'applicazione
- `reset.sh` per cancellare lo stato dell'applicazione (account salvati, stato della blockchain, ABI dei contratti deployati)
- `uninstall.sh` per eliminare le immagini docker create (ma non le dipendenze)

Potrebbe essere necessario abilitare l'*execute permission* degli script *bash* o eseguirli con ruolo di super-utente.

All'esecuzione del comando `./start.sh` si accede al terminale del container *app*. Per avviare il *client* digitare il comando:

```
python main.py
```

All'avvio il *client* mostra la seguente schermata:

![](docs/menu1.png)

In questo menù è possibile registrare un nuovo account *ethereum* o effettuare il *login* con un *account* già esistente.

L'utente autenticato può navigare nel seguente menù:

![](docs/menu2.png)

per deployare uno *smart contract*, visualizzare la mappa dei *deployments*, chiamare i metodi di uno *smart contract* o accedere alle funzionalità *admin* raccolte nel seguente *submenu*:

![](docs/menu3.png)

Qui l'*admin*, ovvero l'*owner* del contratto *Manager*, può impostare un nuovo algoritmo di *sharding* o cambiare lo stato di disponibilità di una blockchain (shard). Gli utenti base possono ugualmente navigare in questo *submenu* ma l'invocazione delle *admin functions* risulterà in un errore.

Dal terminale del container *app*,  nel *path* '/app', è possibile lanciare gli *unit test* con il comando:

```
python -W ignore -m unittest discover -s ./test -p '\*TestSuite.py'
```

> **Attenzione!** I test alterano lo stato delle blockchain *ethereum* e dell'applicazione.

##Contributors
#####Christopher Buratti - Matteo Cirilli - Alessio Paolucci - Vito Scaraggi - Luigi Smargiassi