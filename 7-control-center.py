import time
import random
import json
import asyncio
import aiomqtt
from enum import Enum
import sys
import os

student_id = "6420301002"

async def publish_message(SERIAL, client, app, action, name, value):
    payload = {
                "action"    : "get",
                "project"   : student_id,
                "model"     : "model-01",
                "serial"    : SERIAL,
                "name"      : name,
                "value"     : value
            }
    print(f"{time.ctime()} - PUBLISH - [{SERIAL}] - {payload['name']} > {payload['value']}")
    await client.publish(f"v1cdti/{app}/{action}/{student_id}/model-01/{SERIAL}"
                        , payload=json.dumps(payload))

async def listen(client: aiomqtt.Client):
    async with client.messages() as messages:
        await client.subscribe(f"v1cdti/hw/get/{student_id}/model-01/model-01/+")
        print(f"{time.ctime()} - SUB v1cdti/hw/get/{student_id}/model-01/model-01/+")

        async for message in messages:
            m_decode = json.loads(message.payload)

            if message.topic.matches(f"v1cdti/app/get/{student_id}/model-01/+"):
                print(f"{time.ctime()} - MQTT {m_decode['project']} [{m_decode['serial']}]:{m_decode['name']} => {m_decode['value']}")
            
                if m_decode['name']=="STATUS" and m_decode['value']== 'OFF':
                    await asyncio.sleep(2)
                    await publish_message(m_decode['serial'], client, "hw", "set", "STATUS", "READY")
                elif m_decode['name']=="STATUS" and m_decode['value']== 'FILLWATER':
                    await asyncio.sleep(2)
                    await publish_message(m_decode['serial'], client, "hw", "set", "WATERLAVEL", "FULL")
                elif m_decode['name']=="STATUS" and m_decode['value']== 'HEATWATER':
                    await asyncio.sleep(2)
                    await publish_message(m_decode['serial'], client, "hw", "set", "TEMP", "PASS")

async def getmachine(client: aiomqtt.Client):
    while True:
        await asyncio.sleep(10)
        playload = {
            "action" : "get",
            "project" : student_id,
            "model" : "model-01"
        }
        print(f"{time.ctime()} - PUBLISH - v1cdti/hw/get/{student_id}/model-01/")
        await client.publish(f"v1cdti/hw/get/{student_id}/model-01/",playload = json.dumps(playload))

async def main():
    async with aiomqtt.Client("broker.hivemq.com") as client:
        await asyncio.gather(listen(client) , getmachine(client))

if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

asyncio.run(main())

