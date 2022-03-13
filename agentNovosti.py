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

listaNovostiIndexHr = []

class FSMPonasanje(FSMBehaviour):
    async def on_start(self):
        print(f"Agent se pokreće u početnom stanju ({self.current_state})")

    async def on_end(self):
        print(f"Agent završava s radom u {self.current_state}")
        await self.agent.stop()

class StanjePrvo(State):
    async def run(self):
        print("Šaljem poruku za početak prikupljanje novosti s portala.")
        msg = Message(to=str(self.agent.jid))
        msg.body = "Započni s prikupljanjem novosti s portala!"
        await self.send(msg)
        self.set_next_state(STANJE_DRUGO)

class StanjeDrugo(State):
    async def run(self):
        msg = await self.receive(timeout=10)
        print(f"Drugo stanje zaprimilo poruku sadržaja: \" {msg.body}\"")

        addr = requests.get('https://www.index.hr/rss')

        indexRSS = BeautifulSoup(addr.content, 'xml')
        items = indexRSS.find_all('item')
        for item in items:
            listaNovostiIndexHr.append(f"\n\nDatum: {item.pubDate.text}.\n\nNaslov: {item.title.text}\n\nSažetak: {item.description.text}\n\nPoveznica: {item.link.text}\n\n--------------------------------------------------------------------------------")

        msg = Message(to=str(self.agent.jid))
        msg.body = "Završio s prikupljanjem novosti s portala!"
        await self.send(msg)
        self.set_next_state(STANJE_TRECE)

class StanjeTrece(State):
    async def run(self):
        print("Agent se nalazi u trećem stanju (završno stanje)")
        msg = await self.receive(timeout=5)
                
        if msg:
            if msg.body != '':
                print(f"Treće stanje zaprimilo poruku sadržaja: \" {msg.body}\"")
                print("Novosti prikupljene i spremne za prikaz.\n")
                print("\n --------------------------------------------------------------------------- \n")
                print("\n ------------------------------ N O V O S T I ------------------------------ \n")
                print("\n --------------------------------------------------------------------------- \n")

                counter = 1
                for novost in listaNovostiIndexHr:
                    print(f"{counter}. {novost}")
                    counter += 1
            else:
                print("Nema odgovora.")
class FSMAgent(Agent):
    async def setup(self):
        agent = FSMPonasanje()
        agent.add_state(name=STANJE_PRVO, state=StanjePrvo(), initial=True)
        agent.add_state(name=STANJE_DRUGO, state=StanjeDrugo())
        agent.add_state(name=STANJE_TRECE, state=StanjeTrece())
        agent.add_transition(source=STANJE_PRVO, dest=STANJE_DRUGO)
        agent.add_transition(source=STANJE_DRUGO, dest=STANJE_TRECE)
        self.add_behaviour(agent)

if __name__ == '__main__':

    fsmagent = FSMAgent("vasprojekt1@jabber.eu.org", "123456")
    future = fsmagent.start()
    future.result()

    while fsmagent.is_alive():
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            fsmagent.stop()
            break
    print("Agent zavrsio s radom.") #[1]
