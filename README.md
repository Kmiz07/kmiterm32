# kmiterm32
Software y hardware para control de un sistema de calefacción para autocaravana/camper.
![image](https://github.com/user-attachments/assets/5d72325a-72a1-46c5-8bac-9c52b57b173a)

Descripción del Hardware.

Se trata de un sistema de control para un dispositivo de calefacción y ACS, compuesto por un quemador de gasoil, y un doble circuito para radiador e intercambiador ACS controlado por una válvula bypass para el control de los fluidos y un ventilador con velocidad regulable por PWM.
El corazón del sistema es un esp32S, que dispone de conectividad tanto wifi como Bluetooth.
El diseño de la pcb ha sido realizado pensando en posibles futuras ampliaciones dando salida a la mayoría de los pines disponibles en el chip.
No se ha tenido en cuenta el aislamiento mediante opto acopladores. En posibles ampliaciones, si las entradas/salidas lo requieren deberá tenerse en cuenta.
El circuito consta de salida por doble relé para la válvula bypass de 12v(Fig. 1)
![image](https://github.com/user-attachments/assets/a1593144-c1db-4b91-bf6f-7ba533bd6b1f)
fig. 1

Dicha válvula tiene doble circuito con final de carrera. Para optimizar el consumo y desgaste de materiales, se ha optado por temporizar la acción de cada circuito en un tiempo de 8 segundos configurable desde la app móvil.

Consta de otra salida por relé simple para la linea de maniobra del quemador. La corriente de potencia del quemador tiene conexión directa a batería y no es controlada por el circuito.

La salida para control de velocidad del ventilador dispone de un transistor mosfet de potencia y baja entrada y produce una salida pwm adecuada para un grupo de 4 ventiladores con un consumo maximo total de 2A.

Toma los datos de temperatura ambiente, y temperaturas de fluidos mediante tres sensores ds18b20, encapsulados en un paquete de acero inoxidable impermeable. Estos sensores funcionan mediante el protocolo onewire y con un solo pin de datos se pueden muestrear las tres temperaturas.(fig.2)
![image](https://github.com/user-attachments/assets/eec37993-0454-4b55-9f88-e3056e983b31)
fig. 2

La alimentacion del chip, se obtiene a partir de los 12V mediante un sistema dc-dc del tipo MINI 560 (Fig.3)
![image](https://github.com/user-attachments/assets/77006aa3-844e-4db5-9ef2-30d3f0f2510f)
fig. 3

Se ha elegido este tipo de dispositivo pero en el pcb esta disponible tambien la posibilidad de montar un LF33cv.


![image](https://github.com/user-attachments/assets/28e9574b-473e-42fc-8266-3a432e29568f)
circuito electrico

Descripción del software.

El software esta realizado en Micropython (v1.24.1  2024-11-29 ). La estructura del código trabaja en modo asincrónico, por lo que se ha utilizado la librería aible en lugar de la ble tradicional para no interferir en el bucle de programa asincrónico.
En el inicio, el programa se pone a la espera para recibir una petición de conexión por Bluetooth y no hará nada mas mientras no reciba esa primera conexión.
Una vez recibe la primera petición, envía los datos configurables por usuario a la app y acto seguido comprueba la comunicación de las sondas de temperatura. Si estas no existen o no comunican se pone en marcha una rutina de configuración de las sondas mediante peticiones de modo que se pueda diferenciar el id de cada sonda y pueda ser memorizado en el archivo de configuración para próximos arranques.
Esta integridad de los ids de cada sonda se comprueba a cada bucle de programa. Si esta falla, se detiene la calefacción y se retorna a la rutina de configuración.
A cada vuelta del loop de programa, se comprueban las opciones requeridas por la app,(temperatura deseada, programación, velocidad de ventilador…..) y se toman las decisiones pertinentes.

Si la velocidad del ventilador se coloca en auto, esta vendrá definida por un algoritmo dependiendo del diferencial de temperatura deseada versus temperatura ambiente, y solo funcionara cuando el fluido de calefacción alcance una temperatura definida en la app.
Si se define en la app esta sera fija.
Se puede programar un cambio de estado. Esto es, si la calefacción esta en ON, se pondrá en OFF y viceversa.
Esto se programa en la app móvil y se ajusta la hora del cambio. Cuando el programa recibe la orden, lo traduce a segundos de espera y llegado el momento hace el cambio.
La comparación de tiempos la hace también a cada bucle de programa.
En cualquier momento se puede desactivar mediante la app.
El programa dispone de un archivo de configuración, en el cual, en una estructura json, se definen las variables perdurables y definibles del programa.
Mediante la librería confjson, se puede editar este archivo y recuperar las variables definidas en el json.
En este archivo se guardan también los Ids de las sondas de temperatura.
El consumo eléctrico de la centralita en total reposo es de 14mA (utilizando el dc-dc) a 12v.
Cuando se activa el quemador, el rele sube el consumo hasta 44 mA y mientras cambia de estado la válvula tres vías sube momentáneamente (8 segundos cada cambio) hasta los 75 mA.
El consumo cuando se activa el ventilador si que ya puede subir hasta los 2A con los ventiladores que actualmente tengo instalados. El transistor mosfet consigue el funcionamiento si apenas calentarse por lo que he prescindido de refrigerarlo.
El PWM del ventilador trabaja a una frecuencia de 30KHz, evitando el típico silbido que se genera a bajas frecuencias.

Descripción de la app móvil.

La app móvil, esta programada en appinventor. 
He elegido esta plataforma porque, para aplicaciones sencillas, da unos resultados óptimos y esta al alcance de cualquier persona que tenga algunos conocimientos de cualquier lenguaje de programación.
Cuando inicia la aplicación, si no es la primera vez que conecta, intentara conectar con el ultimo dispositivo con el que lo hizo satisfactoriamente. Si es la primera vez, directamente mostrara una lista de posibles candidatos.
Cada vez que se cambia algún parámetro en la app, esta envia la solicitud a la centralita, y esta, una vez entiende la orden, le confirma la recepción a la app, y es solo entonces cuando se refleja este cambio en la app.
De este modo se evitan posibles ordenes falsas o nulas.
Por lo demás, dispone de la típicas ordenes que podría tener cualquier sistema de calefacción con ACS.
Elección de la temperatura ambiente, activar o desactivar calefacción. Forzar quemador para ACS. Programar cambio de estado, controlar velocidad de ventilador…
Ademas, en la opción Propiedades se puede editar las propiedades del archivo de configuración de la centralita.
La centralita inicia a la espera de una conexión, y no hace nada mas mientras no se conecte vía Bluetooth a la app, pero una vez esta en funcionamiento, se puede cerrar la app sin provocar la parada, la centralita seguirá funcionando con la configuración que tenga, y, en el caso de que se conecte de nuevo a la app, la centralita enviara una actualización de datos para componer las opciones de la app tal y como las tiene la centralita.

![image](https://github.com/user-attachments/assets/00cc1e74-0859-4ac0-b95e-ddf6262d21d3)
