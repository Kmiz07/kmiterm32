import asyncio
import aioble
import bluetooth
from machine import Pin

class BLE():
    def __init__(self, name, evento):
        self.NUS_UUID = bluetooth.UUID('6e400001-b5a3-f393-e0a9-e50e24dcca9e')
        self.TX_UUID = bluetooth.UUID('6e400003-b5a3-f393-e0a9-e50e24dcca9e')
        self.RX_UUID = bluetooth.UUID('6e400002-b5a3-f393-e0a9-e50e24dcca9e')
        ble_service = aioble.Service(self.NUS_UUID)
        self.TX_Characteristic = aioble.Characteristic(ble_service, self.TX_UUID, read=True, notify=True)
        self.RX_Characteristic = aioble.Characteristic(ble_service, self.RX_UUID, read=True, write=True, notify=True, capture=True)
        aioble.register_services(ble_service)
        aioble.core.ble.gatts_set_buffer(self.RX_Characteristic._value_handle, 512) #para sobrepasar los 20 bytes de limitacion
        #aioble.core.ble.gatts_set_buffer(self.TX_Characteristic._value_handle, 512)
        self._ADV_INTERVAL_MS = 250_000
        self.nombre = name
        self.evento = evento
        self.conectado = False
        self.led = Pin(2, Pin.OUT,0)
        
    async def parpadeo(self):
        asyncio.create_task(self.evento(b'desconectado',self))
        while not self.conectado:
            self.led.value(not self.led.value())
            await asyncio.sleep(0.5)
        self.led.value(0)
    
    async def send(self,mensaje):
        print(f'enviando:{mensaje}')
        self.TX_Characteristic.write(mensaje, send_update=True)
        await asyncio.sleep_ms(1000)
    
    async def peripheral_task(self):
        while True:
            try:
                async with await aioble.advertise(self._ADV_INTERVAL_MS,name=self.nombre,services=[self.NUS_UUID],) as connection:
                        print(f"Conectado con {connection.device}")
                        self.conectado=True
                        aioble.config(mtu=128)
                        await connection.disconnected()
                        asyncio.create_task(self.parpadeo())
                        print(f'Desconectado de{connection.device}')
                        self.conectado=False
                        
                        

            except asyncio.CancelledError:
                # Catch the CancelledError
                print("Peripheral task cancelled")
            except Exception as e:
                print("Error in peripheral_task:", e)
            finally:
                # Ensure the loop continues to the next iteration
                await asyncio.sleep_ms(100)
        
    async def wait_for_write(self):
        while True:
            try:
                connection, data = await self.RX_Characteristic.written()
                await self.evento(data,self)
            except asyncio.CancelledError:
                # Catch the CancelledError
                print("Peripheral task cancelled")
            except Exception as e:
                print("Error in peripheral_task:", e)
            finally:
                # Ensure the loop continues to the next iteration
                await asyncio.sleep_ms(100)
    async def iniciar(self):
        t1 = asyncio.create_task(self.parpadeo())
        t2 = asyncio.create_task(self.peripheral_task())
        t3 = asyncio.create_task(self.wait_for_write())
        await asyncio.gather(t2)
    