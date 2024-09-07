# Evidencia -  TC2008B

## Python y Agentes
La parte del server de python fue desarrollada usando Flask con la finalidad de construir una API que permitiera la comunicación entre el script de los agentes y Unity.

El código de los agentes fue realizado utilizando agentpy.

## Unity
Para unity, se hizo un script contenido en los archivos de este repositorio ('APIManager') donde se maneja la conexión con nuestros agentes a través de la API.

## Visión Computacional
Para la detección de objetos/agentes en nuestra escena de unity, decidimos usar el modelo YOLOv8. Se realizó tambien fine tuning al modelo con el fin de que este identificara entre un guardia y una persona (también identifica cámaras de seguridad).
Utilizamos los scripts que nos fueron dados por Nuclea Solutions.

## Proceso de Instalación
Primero se debe instalar el `requirements.txt`. Una vez habiendo instalado las dependencias, en la terminal, se tiene que navegar a la carpeta `/examples/unity-server`.
Una vez ahí, el comando para correr el servidor es `python server_agent.py`. Se recomienda usar la versión 3.11.4 de Python (el proyecto fue desarrollado usando esta versión).

NOTA: se utilizó `ngrok` para establecer una conexión HTTPS con el servidor. 
### Para windows: 
                `choco install ngrok`

                `ngrok config add-authtoken 2lgF6oAlWIQdn3ILGPowEGjLi9b_78EkFSyayLpMi938qifWk`

                `ngrok http 8000`
### Para Mac:  
            `brew install ngrok/ngrok/ngrok`

            `ngrok config add-authtoken 2lgF6oAlWIQdn3ILGPowEGjLi9b_78EkFSyayLpMi938qifWk`

            `ngrok http 8000`

## (OPCIONAL: la escena en unity irá muy lenta si se tiene los dos servers corriendo al mismo tiempo)
Una vez terminados estos pasos, hay que activar el servidor de YOLO para que el modelo comience con la detección de objetos.

En una ventana nueva de terminal:
- Navegar hacia la carpeta `/examples/unity-server` dentro del proyecto
- Correr el comando `python server_yolo.py` 

Aquí el servidor de YOLO empezará a funcionar con nuestro modelo 'best_mdl.pt'.


## Corriendo la simulación en Unity
### NOTA: el servidor "server_agent.py" tiene que estar funcionando para que Unity pueda correr la escena
- Descargar el archivo [evidencia-final 2.zip](https://drive.google.com/drive/folders/11Mn9a7ryCoSy4MjsIBiEFEMTF4zprH-3)
- Descomprimir el archivo y abrirlo en Unity.
- Darle Play a la escena en la parte central superior de la pantalla de Unity.