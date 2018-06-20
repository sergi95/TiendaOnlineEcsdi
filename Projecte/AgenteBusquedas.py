# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:58:13 2013

Esqueleto de agente usando los servicios web de Flask

/comm es la entrada para la recepcion de mensajes del agente
/Stop es la entrada que para el agente

Tiene una funcion AgentBehavior1 que se lanza como un thread concurrente

Asume que el agente de registro esta en el puerto 9000

@author: javier
"""
import os

__author__ = 'javier'

from multiprocessing import Process, Queue
import socket

from rdflib import Namespace, Graph,RDF,Literal
from flask import Flask, request, render_template

from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.Agent import Agent
import AgentUtil.Agents
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.OntoNamespaces import ACL, ECSDI
from AgentUtil.ConsistenciaUtil import cargar_grafo_turtle


# Contador de mensajes
mss_cnt = 0


# Global triplestore graph
dsgraph = Graph()

cola1 = Queue()

# Flask stuff
app = Flask(__name__)

# def cargarGrafo():
#     g = Graph()
#     if os.path.isfile(AgentUtil.Agents.path_productos):
#         g.parse(AgentUtil.Agents.path_productos, format="xml")
#     return g


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """

    print("dentro busqueda")

    global dsgraph
    global mss_cnt
    message = request.args['content']
    print("requestargs")
    print(request.args['content'])
    gm = Graph()
    gm.parse(data=message)
    gr = None

    msgdic = get_message_properties(gm)
    if msgdic is None:
        gr = build_message(Graph(), ACL['not-understood'], sender=AgentUtil.Agents.AgenteBusquedas.uri,
                           msgcnt=mss_cnt)
    else:
        perf = msgdic['performative']
        if perf == ACL.request:
            if 'content' in msgdic:
                grp = Graph()
                gp = cargar_grafo_turtle(AgentUtil.Agents.path_productos)
                content = msgdic['content']
                tipoEleccion = gm.value(subject=content, predicate=ECSDI.tipo)
                print("busqueda: "+tipoEleccion)
                calidadEleccion = gm.value(subject=content, predicate=ECSDI.calidad)
                print("busqueda: " + calidadEleccion)
                valMin = gm.value(subject=content, predicate=ECSDI.valoracionMinima)
                print("busqueda: " + valMin)
                print("tipo valMin" + str(type(valMin)))
                for producto in gp.subjects(predicate=ECSDI.tipo, object=tipoEleccion):
                    print("dentro for1")
                    codigo = gp.value(subject=producto, predicate=ECSDI.codigo)
                    nombre = gp.value(subject=producto, predicate=ECSDI.nombre)
                    precio = gp.value(subject=producto, predicate=ECSDI.precio)
                    descripcion = gp.value(subject=producto, predicate=ECSDI.descripcion)
                    tipo = gp.value(subject=producto, predicate=ECSDI.tipo)
                    valoracion = gp.value(subject=producto, predicate=ECSDI.valoracion)
                    calidad = gp.value(subject=producto, predicate=ECSDI.calidad)
                    clase = gp.value(subject=producto, predicate=RDF.type)
                    print("tipo valoracion" + str(type(valoracion)))
                    if calidad == calidadEleccion and float(valoracion) >= float(valMin):
                    # if calidad == calidadEleccion:
                        grp.add((producto, RDF.type, Literal(clase)))
                        grp.add((producto, ECSDI.codigo, Literal(codigo)))
                        grp.add((producto, ECSDI.nombre, Literal(nombre)))
                        grp.add((producto, ECSDI.precio, Literal(precio)))
                        grp.add((producto, ECSDI.descripcion, Literal(descripcion)))
                        grp.add((producto, ECSDI.tipo, Literal(tipo)))
                        grp.add((producto, ECSDI.valoracion, Literal(valoracion)))
                        grp.add((producto, ECSDI.calidad, Literal(calidad)))
                    # print("nombre producto"+gr.value(subject=producto, predicate=ECSDI.nombre))
                gr = build_message(grp, ACL.inform, sender=AgentUtil.Agents.AgenteBusquedas.uri)
            else:
                gr = build_message(Graph(), ACL['not-understood'], sender=AgentUtil.Agents.AgenteBusquedas.uri,
                                   msgcnt=mss_cnt)
    print("grafo")
    print(gr)
    # for sujeto in gr.subjects(predicate=ECSDI.tipo, object=Literal(criterios)):
    #     print("dentro chivato")
    #     variable = gr.value(subject=sujeto, predicate=ECSDI.nombre)
    #     print(variable)
    return gr.serialize(format='xml')


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
    # Ponemos en marcha los behaviors
    ab1 = Process(target=agentbehavior1, args=(cola1,))
    ab1.start()

    # Ponemos en marcha el servidor
    app.run(host=AgentUtil.Agents.hostname, port=AgentUtil.Agents.BUSQUEDAS_PORT)

    # Esperamos a que acaben los behaviors
    ab1.join()
    print('The End')


