#para enviar comandos:
#obj.send([str.comando]#[valor])
# comandos validos:
#  calefaccion_0,calefaccion_1,calefaccion_2. Estos no llevaran # ni valor , solo comando.
#  acs_0, acs_1, acs_2. Estos no llevaran # ni valor , solo comando.
#  tmp_amb#[valor de temperatura ambiente]
#  tmp_rad#[valor de la temperatura del liquido de circuito en el radiador]
#  tmp_acs#[valor de la temperatura del liquido de circuito en el intercambiador acs]
#  tmp_deseada#[valor de la temperatura ambiente derseada] (este valor es reciproco)
#  conf_amb activa el menu en el movil para notificar que se ha conectado fisicamente la sonda de temperatura ambiente.
#  conf_rad activa el menu en el movil para notificar que se ha conectado fisicamente la sonda de temperatura del radiador.
#  conf_acs activa el menu en el movil para notificar que se ha conectado fisicamente la sonda de temperatura del intercambiadore ACS.
#  conf_OK  envia mensaje de configuracion de sondas exitosa.
#  conf_OUT envia mensaje de que es necesaria la configuracion de las sondas.
#  quemador_1 activa icono quemador
#  quemador_0 desactiva icono quemador
#  ventilador#[valor]  (0 es automatico)
#  cambia#[valor a cambiar] modifica valor propiedades datos.json
#  borra_lista borra lista de propiedades
import  obj_aioble,confjson,asyncio,senstemp,utime,ventilador
conexion_OK=False
temp_ok= False
# temp=None


async def evento(dato,objeto):
    global temp_ok
#     global temp
    data=dato.decode('UTF-8').replace("\n","")
#     print(f'dato=   {dato}')
    #operaciones con mando bluetooth
    global conexion_OK
    if data=='desconectado':
        senstemp.blue_activo = False
        conexion_OK= False
#         temp_o = None
    print(f'>>>{data}')
    if conexion_OK:
        if 'vent#' in data:
            valor = float(data.split('#')[1])
            if valor != senstemp.actual['vent']:
                ventilador.regula(valor)
                senstemp.actual['vent'] = valor
        if data=='Calefaccion_2':
            asyncio.create_task(objeto.send('calefaccion_2\n'))
            senstemp.actual['est_rad']=2
        elif data=='Calefaccion#ON':
            asyncio.create_task(objeto.send('calefaccion_1\n'))
            senstemp.actual['est_rad']=1
            senstemp.actual['est_fire']=1
            #llamar a encender calefaccion
        elif data=='Calefaccion#OFF':
            asyncio.create_task( objeto.send('calefaccion_0\n'))
            senstemp.actual['est_rad']=0
            #llamar a apagar calefaccion
        elif data=='ACS_2':
            asyncio.create_task(objeto.send('acs_2\n'))
            senstemp.actual['est_acs']=2
        elif data=='ACS#ON':
            asyncio.create_task(objeto.send('acs_1\n'))
            senstemp.actual['est_acs']=1
            #llamar encender ACS
        elif data=='ACS#OFF':
            asyncio.create_task(objeto.send('acs_0\n'))
            senstemp.actual['est_acs']=0
            #llamar apagar ACS
        elif 'TMP#'in data:
            valor=data.split('#')[1]
            asyncio.create_task(objeto.send(f'tmp_deseada#{valor}\n'))
            senstemp.actual['th_ok']=int(valor)
        elif 'temporizador#' in data:
            valor = data.split('#')[1]
            if valor!='0':
                
                asyncio.create_task(objeto.send(f'programado#{valor}\n'))
                #configura programacion
                senstemp.actual['programa'] = int (valor) + utime.time()

            else:
                
                asyncio.create_task(objeto.send('programado#0\n'))
                #elimina programacion
                senstemp.actual['programa'] = 0
        elif 'cambia#' in data:
            lin_data= data.split('#')[1]
            vals_lin=lin_data.split(':')
            confjson.entra(vals_lin[0],vals_lin[1])
            asyncio.create_task(envia_configuracion(objeto))
#         print(senstemp.actual)
        
    if data == 'TEST BLE' and not conexion_OK:
        
        await asyncio.sleep_ms(500)
        await objeto.send('TEST OK\n')
        await envia_configuracion(objeto)
        conexion_OK=True
        senstemp.blue_activo = True
        if temp_ok == False:
            print('nuevo objeto temp')
            asyncio.create_task(senstemp.inicia(5, objeto, evento))
            temp_ok=True
        else:
            senstemp.anteriores=[0,0,0]
            await( objeto.send(f'calefaccion_{senstemp.actual['est_rad']}\n'))
            await( objeto.send(f'acs_{senstemp.actual['est_acs']}\n'))
            await( objeto.send(f'tmp_deseada#{senstemp.actual['th_ok']}\n'))
            await( objeto.send(f'quemador_{senstemp.actual['est_fire']}\n'))
            await( objeto.send(f'vent#{float(senstemp.actual['vent'])}\n'))
            if senstemp.actual['programa'] != 0:
                tiempo_restante = senstemp.actual['programa'] - utime.time()
            else:
                tiempo_restante = 0    
            asyncio.create_task(objeto.send(f'programado#{tiempo_restante}\n'))
    if data =='Aceptar': senstemp.pulsa_flash=0
async def envia_configuracion(objeto):
    propiedades=confjson.recupera()
    await objeto.send('borra_lista\n')
    for x in propiedades:
        if x != 'sondas':
            await objeto.send(f'propiedad#{x}:{propiedades[x]}')
            
ble = obj_aioble.BLE(confjson.recupera()['nombre'],evento)
asyncio.run(ble.iniciar())

