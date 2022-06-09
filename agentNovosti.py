#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Izvori:
[1] Finite State Machine Behaviour, Primjer koda, Pristupljeno: 13.3.2022. Poveznica: https://spade-mas.readthedocs.io/en/latest/behaviours.html#finite-state-machine-behaviour
'''
import time

from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message

from bs4 import BeautifulSoup
import requests

STANJE_PRVO = "STANJE_PRVO"
STANJE_DRUGO = "STANJE_DRUGO"
STANJE_TRECE = "STANJE_TRECE"

class GlavniAgent(Agent):

    listaFiltriranihNovostiSPortala = []
    class FSMPonasanje(FSMBehaviour):
        async def on_start(self):
            print(f"{GlavniAgent.__name__}: Pokrećem se ... ({self.current_state})")

        async def on_end(self):
            print(f"{GlavniAgent.__name__}: Završavam s radom ... {self.current_state}")
            await self.agent.stop()

    class StanjePrvo(State):
        async def run(self):
            print(f"{GlavniAgent.__name__}: Šaljem poruku za početak prikupljanje novosti s portala ...")
            msg = Message(to="vasprojekt2@jabber.eu.org")
            msg.body = "Započni s prikupljanjem novosti s portala!"
            await self.send(msg)
            print(f"{GlavniAgent.__name__}: Poruka poslana!")
            self.set_next_state(STANJE_DRUGO)

    class StanjeDrugo(State):
        async def run(self):
            print(f"{GlavniAgent.__name__}: Nalazim se u završnom stanju. Čekam na primitak poruke ...")
            msg = await self.receive(timeout=30)
            if msg:
                print(f"{GlavniAgent.__name__}: Poruka zaprimljena!")
                if msg.body != '':
                    print(f"{GlavniAgent.__name__}: Zaprimio sam poruku sljedećeg sadržaja: \"{msg.body}\"")
                    print(f"{GlavniAgent.__name__}: Novosti prikupljene i spremne za prikaz.")
                    self.set_next_state(STANJE_TRECE)
                else:
                    print("Nema odgovora.")
            else:
                print(f"{SearchAgent.__name__}: Nisam zaprimio poruku.")
                self.set_next_state(STANJE_DRUGO)

    class StanjeTrece(State):
        async def run(self):
            print("\n --------------------------------------------------------------------------- \n")
            print("\n ------------------------------ N O V O S T I ------------------------------ \n")
            print("\n --------------------------------------------------------------------------- \n")
            
            counter = 1
            for novost in GlavniAgent.listaFiltriranihNovostiSPortala:
                print(f"{counter}. {novost}")
                counter += 1
    
    async def setup(self):
        agent = self.FSMPonasanje()
        agent.add_state(name=STANJE_PRVO, state=self.StanjePrvo(), initial=True)
        agent.add_state(name=STANJE_DRUGO, state=self.StanjeDrugo())
        agent.add_state(name=STANJE_TRECE, state=self.StanjeTrece())
        agent.add_transition(source=STANJE_PRVO, dest=STANJE_DRUGO)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_TRECE)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_DRUGO)
        self.add_behaviour(agent)

class RSSAgent(Agent):

    class FSMPonasanje(FSMBehaviour):
        async def on_start(self):
            print(f"{RSSAgent.__name__}: Pokrećem se ... ({self.current_state})")

        async def on_end(self):
            print(f"{RSSAgent.__name__}: Završavam s radom ... {self.current_state}")
            await self.agent.stop()

    class StanjePrvo(State):
        async def run(self):
            msg = await self.receive(timeout=15) #nevažan timeout -> automatski se poruka prima
            print(f"{RSSAgent.__name__}: Zaprimio sam poruku sadržaja: \"{msg.body}\"")
            self.set_next_state(STANJE_DRUGO)

    class StanjeDrugo(State):
        async def run(self):
            listaAddr = []
            unos = ''
            izbornik = input("Način unosa izvora:\n 0 - Učitaj datoteku (.txt) s RSS izvorima [struktura datoteke: svaki izvor u svoj zaseban redak] (preporuka) \n 1 - direktan unos putem terminala (ograničeno vrijeme unosa) \n\n Vaš izbor: ")
            if (izbornik == "0"):
                putanjaDatoteke = input("Putanja do datoteke: ")
                datoteka = open(f"{putanjaDatoteke}", "r")
                for red in datoteka:
                    redak = red.strip()
                    addr = requests.get(f'{redak}')
                    nazivPortala = redak.split("//")[1]
                    RSSAgent = BeautifulSoup(addr.content, 'xml')
                    items = RSSAgent.find_all('item')
                    for item in items:
                        portal = nazivPortala
                        datum = item.pubDate.text
                        naslov = item.title.text
                        sazetak = item.description.text
                        poveznica = item.link.text
                        if(sazetak != ''):
                            SearchAgent.listaNovostiSPortala.append(f"\n\nPortal: {portal}\n\nDatum: {datum}.\n\nNaslov: {naslov}\n\nSažetak: {sazetak}\n\nPoveznica: {poveznica}\n\n--------------------------------------------------------------------------------")
                        else:
                            SearchAgent.listaNovostiSPortala.append(f"\n\nPortal: {portal}\n\nDatum: {datum}.\n\nNaslov: {naslov}\n\nPoveznica: {poveznica}\n\n--------------------------------------------------------------------------------")
                self.set_next_state(STANJE_TRECE)
            else:
                while(unos != "\s"):
                    unos = input("Unesi željeni RSS u obliku 'https://domain-name.xyz' (\"\\s\" - prekid unosa): ")
                    if(unos != '\s'):
                        listaAddr.append(f"{unos}")
                    else:
                        break
                for adresa in listaAddr:    
                    addr = requests.get(f'{adresa}')
                    nazivPortala = adresa.split("//")[1]
                    RSSAgent = BeautifulSoup(addr.content, 'xml')
                    items = RSSAgent.find_all('item')
                    for item in items:
                        portal = nazivPortala
                        datum = item.pubDate.text
                        naslov = item.title.text
                        sazetak = item.description.text
                        poveznica = item.link.text
                        if(sazetak != ''):
                            SearchAgent.listaNovostiSPortala.append(f"\n\nPortal: {portal}\n\nDatum: {datum}.\n\nNaslov: {naslov}\n\nSažetak: {sazetak}\n\nPoveznica: {poveznica}\n\n--------------------------------------------------------------------------------")
                        else:
                            SearchAgent.listaNovostiSPortala.append(f"\n\nPortal: {portal}\n\nDatum: {datum}.\n\nNaslov: {naslov}\n\nPoveznica: {poveznica}\n\n--------------------------------------------------------------------------------")
                self.set_next_state(STANJE_TRECE)
    
    class StanjeTrece(State):
        async def run(self):
            print(f"{RSSAgent.__name__}: Šaljem poruku da sam završio s prikupljanjem novosti ...")
            msg = Message(to="vasprojekt3@jabber.eu.org")
            msg.body = "Završio s prikupljanjem novosti s portala!"
            await self.send(msg)
            print(f"{RSSAgent.__name__}: Poruka poslana!")

    async def setup(self):
        agent = self.FSMPonasanje()
        agent.add_state(name=STANJE_PRVO, state=self.StanjePrvo(), initial=True)
        agent.add_state(name=STANJE_DRUGO, state=self.StanjeDrugo())
        agent.add_state(name=STANJE_TRECE, state=self.StanjeTrece())
        agent.add_transition(source=STANJE_PRVO, dest=STANJE_DRUGO)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_TRECE)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_TRECE)
        self.add_behaviour(agent)

class SearchAgent(Agent):


    listaNovostiSPortala = []
    class FSMPonasanje(FSMBehaviour):
        async def on_start(self):
            print(f"{SearchAgent.__name__}: Pokrećem se ... ({self.current_state})")

        async def on_end(self):
            print(f"{SearchAgent.__name__}: Završavam s radom ... {self.current_state}")
            await self.agent.stop()

    class StanjePrvo(State):
        async def run(self):
            msg = await self.receive(timeout=15)
            if msg:
                print(f"{SearchAgent.__name__}: Zaprimio sam poruku sadržaja: \"{msg.body}\"")
                self.set_next_state(STANJE_DRUGO)
            else:
                print(f"{SearchAgent.__name__}: Nisam zaprimio poruku.")
                self.set_next_state(STANJE_PRVO)
            
    class StanjeDrugo(State):
        async def run(self):
            
            unos = input("Unesi pojam za pretraživanje (\"all\" - prikaz svih vijesti): ")

            if (unos != "all"):
                for novost in SearchAgent.listaNovostiSPortala:
                    if(unos in novost):
                        GlavniAgent.listaFiltriranihNovostiSPortala.append(novost)
                print("Vijesti su filtrirane!")
                self.set_next_state(STANJE_TRECE)
            else:
                for novost in SearchAgent.listaNovostiSPortala:
                    GlavniAgent.listaFiltriranihNovostiSPortala.append(f"{novost}")
                    self.set_next_state(STANJE_TRECE)


    class StanjeTrece(State):
        async def run(self):
            print(f"{SearchAgent.__name__}: Šaljem poruku da sam završio s filtriranjem novosti ...")
            msg = Message(to="vasprojekt1@jabber.eu.org")
            msg.body = "Završio s filtracijom novosti s portala!"
            await self.send(msg)
            print(f"{SearchAgent.__name__}: Poruka poslana!")   

    async def setup(self):
        agent = self.FSMPonasanje()
        agent.add_state(name=STANJE_PRVO, state=self.StanjePrvo(), initial=True)
        agent.add_state(name=STANJE_DRUGO, state=self.StanjeDrugo())
        agent.add_state(name=STANJE_TRECE, state=self.StanjeTrece())
        agent.add_transition(source=STANJE_PRVO, dest=STANJE_PRVO)
        agent.add_transition(source=STANJE_PRVO, dest=STANJE_DRUGO)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_TRECE)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_TRECE)
        self.add_behaviour(agent)

if __name__ == '__main__':

    searchAgent = SearchAgent("vasprojekt3@jabber.eu.org", "112233")
    pokretanje1 = searchAgent.start()
    pokretanje1.result()

    rssagent = RSSAgent("vasprojekt2@jabber.eu.org", "135790")
    pokretanje2 = rssagent.start()
    pokretanje2.result()

    glavniAgent = GlavniAgent("vasprojekt1@jabber.eu.org", "123456")
    pokretanje3 = glavniAgent.start()
    pokretanje3.result()

    while glavniAgent.is_alive():
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            glavniAgent.stop()
            break
    print("Višeagentni sustav završio s radom.") #[1]