import os
from multiprocessing import Process, Queue
import socket

from rdflib import Namespace, Graph, RDF, URIRef, Literal
from flask import Flask, request, render_template
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3
from rdflib.namespace import FOAF

import AgentUtil
import AgentUtil.Agents
from AgentUtil.ACLMessages import build_message, send_message
from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.Agent import Agent
from AgentUtil.Logging import config_logger
from AgentUtil.OntoNamespaces import ECSDI
import random

# Para el sleep
import time

from AgentUtil.OntoNamespaces import ACL
from AgentUtil.SPARQLHelper import filterSPARQLValues

import argparse
import requests
from requests import ConnectionError

__author__ = 'Sergi'


# Definimos los parametros de la linea de comandos
# parser = argparse.ArgumentParser()
# parser.add_argument('--host', default='localhost', help="Host del agente")
# parser.add_argument('--port', type=int, help="Puerto de comunicacion del agente")
# parser.add_argument('--filters', nargs='+', default=[], help="criterios de busqueda")


# Flask stuff
app = Flask(__name__)


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    productos = Graph()
    productos.bind('escdi', ECSDI)

    # id = 'Producto1'
    # productos.add((ECSDI[id],RDF.type,Literal('ProductoPropio')))
    # productos.add((ECSDI[id],ECSDI.codigo,Literal(1)))
    # productos.add((ECSDI[id],ECSDI.nombre,Literal('zanahoria')))
    # productos.add((ECSDI[id],ECSDI.precio,Literal(1.8)))
    # productos.add((ECSDI[id],ECSDI.descripcion,Literal('ricas')))
    # productos.add((ECSDI[id],ECSDI.tipo,Literal('hortalizas')))
    # productos.add((ECSDI[id],ECSDI.valoracion,Literal(1.5)))
    # productos.add((ECSDI[id], ECSDI.calidad, Literal('normal')))
    #
    # id = 'Producto2'
    # productos.add((ECSDI[id], RDF.type, Literal('ProductoPropio')))
    # productos.add((ECSDI[id], ECSDI.codigo, Literal(2)))
    # productos.add((ECSDI[id], ECSDI.nombre, Literal('patata')))
    # productos.add((ECSDI[id], ECSDI.precio, Literal(1.8)))
    # productos.add((ECSDI[id], ECSDI.descripcion, Literal('monalisa')))
    # productos.add((ECSDI[id], ECSDI.tipo, Literal('hortalizas')))
    # productos.add((ECSDI[id], ECSDI.valoracion, Literal(1.5)))
    # productos.add((ECSDI[id], ECSDI.calidad, Literal('superior')))
    #
    #
    # id = 'Producto3'
    #
    # productos.add((ECSDI[id],RDF.type,Literal('ProductoPropio')))
    # productos.add((ECSDI[id],ECSDI.codigo,Literal(3)))
    # productos.add((ECSDI[id],ECSDI.nombre,Literal('zapatos')))
    # productos.add((ECSDI[id],ECSDI.precio,Literal(2.9)))
    # productos.add((ECSDI[id],ECSDI.descripcion,Literal("buenos buenos")))
    # productos.add((ECSDI[id],ECSDI.tipo,Literal('calzado')))
    # productos.add((ECSDI[id],ECSDI.valoracion,Literal(2.5)))
    # productos.add((ECSDI[id], ECSDI.calidad, Literal('premium')))
    #
    # random.randint(0, 999999999999)


    tipos = ['hortalizas', 'calzado', 'electronica']
    descripciones = ['a', 'b', 'c', 'd', 'e','f', 'g', 'h']
    calidades = ['normal', 'superior', 'premium']
    nombresHortalizas = ['tomate', 'rabano', 'pepino', 'lechuga', 'patata', 'zanahoria', 'cebolla', 'pimiento', 'ajo', 'calabaza']
    nombresCalzado = ['zapatillas', 'zapatos', 'botines', 'botas', 'mocasin', 'nautico', 'zuecos', 'manoletinas', 'chanclas', 'sandalias']
    nombresElectronica = ['iphone', 'auricalares', 'teclado', 'altavoz', 'router', 'despertados', 'videojuego', 'camara', 'reader', 'telefono']
    for i in range(1,100):
        tipo = random.choice(tipos)
        if tipo == 'hortalizas':
            nombre = random.choice(nombresHortalizas)
        elif tipo == 'calzado':
            nombre = random.choice(nombresCalzado)
        else:
            nombre = random.choice(nombresElectronica)
        calidad = random.choice(calidades)
        descripcion = random.choice(descripciones)
        precio = random.uniform(1.0, 15.0)
        valoracion = random.uniform(1.0, 4.9)

        productos.add((ECSDI['Producto' + str(i)], RDF.type, Literal('ProductoPropio')))
        productos.add((ECSDI['Producto' + str(i)], ECSDI.codigo, Literal(i)))
        productos.add((ECSDI['Producto' + str(i)], ECSDI.nombre, Literal(nombre)))
        productos.add((ECSDI['Producto' + str(i)], ECSDI.precio, Literal(precio)))
        productos.add((ECSDI['Producto' + str(i)], ECSDI.descripcion, Literal(descripcion)))
        productos.add((ECSDI['Producto' + str(i)], ECSDI.tipo, Literal(tipo)))
        productos.add((ECSDI['Producto' + str(i)], ECSDI.valoracion, Literal(valoracion)))
        productos.add((ECSDI['Producto' + str(i)], ECSDI.calidad, Literal(calidad)))



    file = open(AgentUtil.Agents.path_productos, "w+")

    productos.serialize(destination=file,format='turtle')

    file.flush()

    file.close()

    centrosLogisticos = Graph()
    centrosLogisticos.bind('escdi', ECSDI)

    codigo = 1
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], RDF.type, Literal('CentroLogistico')))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.codigo, Literal(codigo)))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.localizacion, Literal('Barcelona')))

    codigo = 2
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], RDF.type, Literal('CentroLogistico')))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.codigo, Literal(codigo)))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.localizacion, Literal('Madrid')))

    codigo = 3
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], RDF.type, Literal('CentroLogistico')))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.codigo, Literal(codigo)))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.localizacion, Literal('Valencia')))

    codigo = 4
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], RDF.type, Literal('CentroLogistico')))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.codigo, Literal(codigo)))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.localizacion, Literal('Bilbao')))


    for i in range(1, 100):
        centro = random.randint(1, 4)
        centro2 = centro
        while centro == centro2:
            centro2 = random.randint(1,4)
        centrosLogisticos.add((ECSDI['CentroLogistico' + str(centro)], ECSDI.dispone_de, ECSDI['Producto' + str(i)]))
        centrosLogisticos.add((ECSDI['CentroLogistico' + str(centro2)], ECSDI.dispone_de, ECSDI['Producto' + str(i)]))

    file = open(AgentUtil.Agents.path_centrosLogisticos, "w+")

    centrosLogisticos.serialize(destination=file, format='turtle')

    file.flush()

    file.close()


    return "funcionando escritura!"


@app.route("/Stop")
def stop():
    """
    Entrypoint que para el agente

    :return:
    """
    tidyup()
    shutdown_server()
    return "Parando Servidor"


def tidyup():
    """
    Acciones previas a parar el agente

    """
    pass


def agentbehavior1(cola):
    """
    Un comportamiento del agente

    :return:
    """
    
    pass


if __name__ == '__main__':
    # parsing de los parametros de la linea de comandos
    # args = parser.parse_args()

    # Ponemos en marcha el servidor
    # app.run(host=args.host, port=args.port)
    app.run(host=AgentUtil.Agents.hostname, port=AgentUtil.Agents.ESCRITURA_PORT)
    print('The End')
