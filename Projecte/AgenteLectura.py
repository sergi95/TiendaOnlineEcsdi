import os
from multiprocessing import Process, Queue
import socket

from rdflib import Namespace, Graph, RDF, URIRef, Literal
from flask import Flask, request, render_template
from SPARQLWrapper import SPARQLWrapper, XML
from rdflib.namespace import FOAF

import AgentUtil
import AgentUtil.Agents
from AgentUtil.ACLMessages import build_message, send_message
from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.Agent import Agent
from AgentUtil.Logging import config_logger
from AgentUtil.OntoNamespaces import ECSDI

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


def cargarGrafo():
    g = Graph()
    if os.path.isfile(AgentUtil.Agents.path_productos):
        g.parse(AgentUtil.Agents.path_productos, format="xml")
    return g


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    graph = cargarGrafo()
    # graph.bind('ecsdi', ECSDI)

    variable = graph.value(subject=ECSDI['2'], predicate=ECSDI.codigo)
    print(variable)
    variable = graph.value(subject=ECSDI['2'], predicate=ECSDI.nombre)
    print(variable)
    variable = graph.value(subject=ECSDI['2'], predicate=ECSDI.precio)
    print(variable)
    variable = graph.value(subject=ECSDI['2'], predicate=ECSDI.descripcion)
    print(variable)
    variable = graph.value(subject=ECSDI['2'], predicate=ECSDI.tipo)
    print(variable)
    variable = graph.value(subject=ECSDI['2'], predicate=ECSDI.valoracion)
    print(variable)

    print('--------------------------------------')

    variable1 = graph.value(subject=ECSDI['1'], predicate=ECSDI.codigo)
    print(variable1)
    variable1 = graph.value(subject=ECSDI['1'], predicate=ECSDI.nombre)
    print(variable1)
    variable1 = graph.value(subject=ECSDI['1'], predicate=ECSDI.precio)
    print(variable1)
    variable1 = graph.value(subject=ECSDI['1'], predicate=ECSDI.descripcion)
    print(variable1)
    variable1 = graph.value(subject=ECSDI['1'], predicate=ECSDI.tipo)
    print(variable1)
    variable1 = graph.value(subject=ECSDI['1'], predicate=ECSDI.valoracion)
    print(variable1)
    # variable = graph.subjects(predicate=RDF.type, object='ProductoPropio')

    return 'funcionando lectura!'


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
    app.run(host=AgentUtil.Agents.hostname, port=AgentUtil.Agents.LECTURA_PORT)
    print('The End')
