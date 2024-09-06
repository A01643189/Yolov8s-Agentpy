# Evidencia -  TC2008B

## Python y Agentes
La parte del server de python fue desarrollada usando Flask con la finalidad de construir una API que permitiera la comunicación entre el script de los agentes y Unity.

El código de los agentes fue realizado utilizando agentpy.

## Unity
Para unity, se hizo un script contenido en los archivos de este repositorio ('APIManager') donde se maneja la conexión con nuestros agentes a través de la API.

## Visión Computacional
Para la detección de objetos/agentes en nuestra escena de unity, decidimos usar el modelo YOLOv8. Se realizó tambien fine tuning al modelo con el fin de que este identificara entre un guardia y una persona (también identifica cámaras de seguridad).
Utilizamos los scripts que nos fueron dados por Nuclea Solutions.

