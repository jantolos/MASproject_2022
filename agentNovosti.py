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

    listaFiltriranihNovostiIndexHr = []
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
            print(f"{GlavniAgent.__name__}: Poruka zaprimljena!")
                    
            if msg:
                if msg.body != '':
                    print(f"{GlavniAgent.__name__}: Zaprimio sam poruku sljedećeg sadržaja: \"{msg.body}\"")
                    print(f"{GlavniAgent.__name__}: Novosti prikupljene i spremne za prikaz.")
                    print("\n --------------------------------------------------------------------------- \n")
                    print("\n ------------------------------ N O V O S T I ------------------------------ \n")
                    print("\n --------------------------------------------------------------------------- \n")

                    counter = 1
                    for novost in GlavniAgent.listaFiltriranihNovostiIndexHr:
                        print(f"{counter}. {novost}")
                        counter += 1
                else:
                    print("Nema odgovora.")

    async def setup(self):
        agent = self.FSMPonasanje()
        agent.add_state(name=STANJE_PRVO, state=self.StanjePrvo(), initial=True)
        agent.add_state(name=STANJE_DRUGO, state=self.StanjeDrugo())
        agent.add_transition(source=STANJE_PRVO, dest=STANJE_DRUGO)
        self.add_behaviour(agent)

class IndexRSS(Agent):

    class FSMPonasanje(FSMBehaviour):
        async def on_start(self):
            print(f"{IndexRSS.__name__}: Pokrećem se ... ({self.current_state})")

        async def on_end(self):
            print(f"{IndexRSS.__name__}: Završavam s radom ... {self.current_state}")
            await self.agent.stop()

    class StanjePrvo(State):
        async def run(self):
            msg = await self.receive(timeout=15)
            print(f"{IndexRSS.__name__}: Zaprimio sam poruku sadržaja: \"{msg.body}\"")
            self.set_next_state(STANJE_DRUGO)

    class StanjeDrugo(State):
        async def run(self):
            
            addr = requests.get('https://www.index.hr/rss')

            indexRSS = BeautifulSoup(addr.content, 'xml')
            items = indexRSS.find_all('item')
            for item in items:
                SearchAgent.listaNovostiIndexHr.append(f"\n\nDatum: {item.pubDate.text}.\n\nNaslov: {item.title.text}\n\nSažetak: {item.description.text}\n\nPoveznica: {item.link.text}\n\n--------------------------------------------------------------------------------")
            self.set_next_state(STANJE_TRECE)

    class StanjeTrece(State):
        async def run(self):
            print(f"{IndexRSS.__name__}: Šaljem poruku da sam završio s prikupljanjem novosti ...")
            msg = Message(to="vasprojekt3@jabber.eu.org")
            msg.body = "Završio s prikupljanjem novosti s portala!"
            await self.send(msg)
            print(f"{IndexRSS.__name__}: Poruka poslana!")

    async def setup(self):
        agent = self.FSMPonasanje()
        agent.add_state(name=STANJE_PRVO, state=self.StanjePrvo(), initial=True)
        agent.add_state(name=STANJE_DRUGO, state=self.StanjeDrugo())
        agent.add_state(name=STANJE_TRECE, state=self.StanjeTrece())
        agent.add_transition(source=STANJE_PRVO, dest=STANJE_DRUGO)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_TRECE)
        self.add_behaviour(agent)

class SearchAgent(Agent):


    listaNovostiIndexHr = []
    class FSMPonasanje(FSMBehaviour):
        async def on_start(self):
            print(f"{SearchAgent.__name__}: Pokrećem se ... ({self.current_state})")

        async def on_end(self):
            print(f"{SearchAgent.__name__}: Završavam s radom ... {self.current_state}")
            await self.agent.stop()

    class StanjePrvo(State):
        async def run(self):
            msg = await self.receive(timeout=15)
            print(f"{SearchAgent.__name__}: Zaprimio sam poruku sadržaja: \"{msg.body}\"")
            self.set_next_state(STANJE_DRUGO)
            
    class StanjeDrugo(State):
        async def run(self):
            
            unos = input("Unesi pojam za pretraživanje (\"all\" - prikaz svih vijesti): ")

            if (unos != "all"):
                for novost in SearchAgent.listaNovostiIndexHr:
                        if(unos in novost):
                            GlavniAgent.listaFiltriranihNovostiIndexHr.append(novost)
                print("Vijesti su filtrirane!")
                self.set_next_state(STANJE_TRECE)
            else:
                for novost in SearchAgent.listaNovostiIndexHr:
                    GlavniAgent.listaFiltriranihNovostiIndexHr.append(f"{novost}")
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
        agent.add_transition(source=STANJE_PRVO, dest=STANJE_DRUGO)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_TRECE)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_TRECE)
        self.add_behaviour(agent)

if __name__ == '__main__':

    searchAgent = SearchAgent("vasprojekt3@jabber.eu.org", "112233")
    pokretanje1 = searchAgent.start()
    pokretanje1.result()

    rssagent = IndexRSS("vasprojekt2@jabber.eu.org", "135790")
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

