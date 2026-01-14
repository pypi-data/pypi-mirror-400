# llm_serving_module

Esta libería contiene distintos módulos para hacer inferencia de modelos de Ollama, HuggingFace y Google por medio de los servicios desplegados en el servidor local de Unergy/Solenium. El usuario debe tener configurada la conexión por medio de VPN al servidor para hacer uso de estos.

Entre algunas de las funcionalidades están:

1. Servicio de inferencia a Google por medio de rotación automática: Con la función 'google_inference_request', puede hacer inferencia dando el prompt de sistema, de usuario y, opcionalmente, el formato en el que quiere recibir el resultado (un objeto que herede de BaseModel de Pydantic). 

Este servicio usa como backend un sistema de colas por medio de Redis y Celery; también almacena la información de tokens en una base de datos PostgreSQL.
