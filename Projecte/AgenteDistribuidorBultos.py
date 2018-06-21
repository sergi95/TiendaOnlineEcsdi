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

from rdflib import Namespace, Graph, RDF, Literal, URIRef
from flask import Flask, request, render_template

from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.Agent import Agent
import AgentUtil.Agents
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.OntoNamespaces import ACL, ECSDI
from AgentUtil.ConsistenciaUtil import cargar_grafo_turtle, guardar_grafo_turtle
import random


# Contador de mensajes
mss_cnt = 0


# Global triplestore graph
dsgraph = Graph()

cola1 = Queue()

# Flask stuff
app = Flask(__name__)


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    global dsgraph
    global mss_cnt

    message = request.args['content']
    print("requestargs")
    print(request.args['content'])
    gm = Graph()
    gm.parse(data=message)
    gr = None
    gcopia = gm

    msgdic = get_message_properties(gm)
    if msgdic is None:
        gr = build_message(Graph(), ACL['not-understood'], sender=AgentUtil.Agents.AgenteDistribuidorBultos.uri,
                           msgcnt=mss_cnt)
    else:
        perf = msgdic['performative']
        if perf == ACL.request:
            if 'content' in msgdic:
                content = msgdic['content']
                email = gcopia.value(subject=content, predicate=ECSDI.email)
                gcopia.remove((content, ECSDI.email, None))
                urgencia = gcopia.value(subject=content, predicate=ECSDI.urgencia)
                gcopia.remove((content, ECSDI.urgencia, None))
                print("busqueda: " + email)

                for (su, pd, ob) in gcopia:
                    print("sujeto "+su)
                    print("predicado " + pd)
                    print("objeto " + ob)


                codigoPedido = random.randint(0, 999999999999)
                gclientes = cargar_grafo_turtle(AgentUtil.Agents.path_clientes)
                # sujetoCliente = gclientes.subjects(predicate=ECSDI.email, object=email)

                # print("----------------------------------")
                # print(sujetoCliente)
                # print(ECSDI.sujetoCliente)
                # print(ECSDI[sujetoCliente])
                # print(ECSDI['Cliente'+email])
                # print("----------------------------------")

                gpedidos = cargar_grafo_turtle(AgentUtil.Agents.path_pedidos)
                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], RDF.type, Literal('Pedido')))
                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.codigo, Literal(codigoPedido)))
                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.estado, Literal(1)))
                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.prioridad, Literal(urgencia)))

                for item in gclientes.subjects(predicate=ECSDI.email, object=email):
                    gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.realizada_por, URIRef(item)))
                    ciudad = gclientes.value(subject=item, predicate=ECSDI.localizacion)

                gcentrosLogisticos = cargar_grafo_turtle(AgentUtil.Agents.path_centrosLogisticos)
                # ciudad = gclientes.value(subject=sujetoCliente, predicate=ECSDI.localizacion)
                print("ciudad "+ ciudad)
                # sujetoCentro = gcentrosLogisticos.subjects(predicate=ECSDI.localizacion, object=ciudad)

                gbultos = Graph()
                gbultos.bind('ecsdi', ECSDI)
                # if not sujetoCentro is None:
                for item1 in gcentrosLogisticos.subjects(predicate=ECSDI.localizacion, object=ciudad):
                    print("he entrado en item 1")
                    l = []
                    for producto in gcopia.subjects(predicate=RDF.type, object=Literal('ProductoPropio')):
                        print("he entrado en for1 producto")
                        if (item1, ECSDI.dispone_de, producto) in gcentrosLogisticos:
                            print("he entrado en anadir producto")
                            l.append(producto)
                            gcopia.remove((producto,None, None))
                    for producto in gcopia.subjects(predicate=RDF.type, object=Literal('ProductoAjenoEnvio')):
                        if (item1, ECSDI.dispone_de, producto) in gcentrosLogisticos:
                            l.append(producto)
                            gcopia.remove((producto,None, None))
                    if not len(l) == 0:
                        print("he entrado en not len 0 1")
                        codigoBulto = random.randint(0, 999999999999)
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], RDF.type, Literal('BultoEnvio')))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.codigo, Literal(codigoBulto)))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.estado, Literal(1)))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.asignado_a, URIRef(item1)))
                        for producto in l:
                            gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.compuesto_por, URIRef(producto)))
                    gcentrosLogisticos.remove((item1,None,None))
                for centro in gcentrosLogisticos.subjects(predicate=RDF.type, object=Literal('CentroLogistico')):
                    l = []
                    for producto in gcopia.subjects(predicate=RDF.type, object=Literal('ProductoPropio')):
                        if (centro, ECSDI.dispone_de, producto) in gcentrosLogisticos:
                            l.append(producto)
                            gcopia.remove((producto, None, None))
                    for producto in gcopia.subjects(predicate=RDF.type, object=Literal('ProductoAjenoEnvio')):
                        if (centro, ECSDI.dispone_de, producto) in gcentrosLogisticos:
                            l.append(producto)
                            gcopia.remove((producto,None, None))
                    if not len(l) == 0:
                        print("he entrado en not len 0 2")
                        codigoBulto = random.randint(0, 999999999999)
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], RDF.type, Literal('BultoEnvio')))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.codigo, Literal(codigoBulto)))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.estado, Literal(1)))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.asignado_a, URIRef(centro)))
                        for producto in l:
                            gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.compuesto_por, URIRef(producto)))

                for item2 in gbultos.subjects(predicate=RDF.type, object=Literal('BultoEnvio')):
                    gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.compuesto_de, URIRef(item2)))

                # gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.realizada_por, URIRef(str(sujetoCliente))))
                guardar_grafo_turtle(gpedidos, AgentUtil.Agents.path_pedidos)
                gbultosTotales = cargar_grafo_turtle(AgentUtil.Agents.path_bultos)
                gbultosTotales += gbultos
                guardar_grafo_turtle(gbultosTotales, AgentUtil.Agents.path_bultos)

                gfacturas = cargar_grafo_turtle(AgentUtil.Agents.path_facturas_previas)
                codigoFactura = random.randint(0, 999999999999)
                gfacturas.add((ECSDI['Factura' + str(codigoFactura)], RDF.type, Literal('FacturaPrevia')))
                gfacturas.add((ECSDI['Factura' + str(codigoFactura)], ECSDI.codigo, Literal(codigoFactura)))
                gfacturas.add((ECSDI['Factura' + str(codigoFactura)], ECSDI.pertence_a, ECSDI['Pedido' + str(codigoPedido)]))
                guardar_grafo_turtle(gfacturas, AgentUtil.Agents.path_facturas_previas)

                gr = build_message(Graph(), ACL.agree, sender=AgentUtil.Agents.AgenteDistribuidorBultos.uri)
            else:
                gr = build_message(Graph(), ACL['not-understood'], sender=AgentUtil.Agents.AgenteDistribuidorBultos.uri,
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
    app.run(host=AgentUtil.Agents.hostname, port=AgentUtil.Agents.DISTRIBUIDOR_BULTOS_PORT)

    # Esperamos a que acaben los behaviors
    ab1.join()
    print('The End')


