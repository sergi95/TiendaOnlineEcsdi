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

    msgdic = get_message_properties(gm)
    if msgdic is None:
        gr = build_message(Graph(), ACL['not-understood'], sender=AgentUtil.Agents.AgenteInformador.uri,
                           msgcnt=mss_cnt)
    else:
        perf = msgdic['performative']
        if perf == ACL.request:
            if 'content' in msgdic:
                content = msgdic['content']
                if 'obtenerFacturasPrevias' in str(content):
                    print("dentro facturas")
                    grf = Graph()
                    gpedidos = cargar_grafo_turtle(AgentUtil.Agents.path_pedidos)
                    gclientes = cargar_grafo_turtle(AgentUtil.Agents.path_clientes)
                    gfacturasPrevias = cargar_grafo_turtle(AgentUtil.Agents.path_facturas_previas)
                    email = gm.value(subject=content, predicate=ECSDI.email)
                    print("email" + email)

                    for sujetoCliente in gclientes.subjects(predicate=ECSDI.email, object=email):
                        print("dentro for clientes")
                        for pedidoCliente in gpedidos.subjects(predicate=ECSDI.realizada_por, object=sujetoCliente):
                            print("dentro for pedidos")
                            for facturaCliente in gfacturasPrevias.subjects(predicate=ECSDI.pertenece_a, object=pedidoCliente):
                                print("dentro for facturas")
                                codigo = gfacturasPrevias.value(subject=facturaCliente, predicate=ECSDI.codigo)
                                print("codigo " + str(codigo))
                                clase = gfacturasPrevias.value(subject=facturaCliente, predicate=RDF.type)
                                grf.add((facturaCliente, RDF.type, Literal(clase)))
                                grf.add((facturaCliente, ECSDI.codigo, Literal(codigo)))

                    gr = build_message(grf, ACL.inform, sender=AgentUtil.Agents.AgenteInformador.uri)
                if 'obtenerFacturaPrevia' in str(content):
                    print("dentro factura")
                    grf = Graph()
                    gpedidos = cargar_grafo_turtle(AgentUtil.Agents.path_pedidos)
                    gclientes = cargar_grafo_turtle(AgentUtil.Agents.path_clientes)
                    gfacturasPrevias = cargar_grafo_turtle(AgentUtil.Agents.path_facturas_previas)

                    print("-------------------------------------")
                    for suje, pred, obj in gfacturasPrevias:
                        print("dentro for prueba")
                        print("sujeto " + suje)
                        print("predicado " + pred)
                        print("objeto " + obj)

                    codigoFactura = gm.value(subject=content, predicate=ECSDI.codigo)

                    codigoFactura1 = int(codigoFactura)


                    for facturaPrevia in gfacturasPrevias.subjects(predicate=ECSDI.codigo, object=Literal(codigoFactura1)):
                    # for facturaPrevia, predi, obje in gfacturasPrevias1.triples((None, ECSDI.codigo, Literal(codigoFactura))):
                        print("dentro for facturas")
                        pedido = gfacturasPrevias.value(subject=facturaPrevia, predicate=ECSDI.pertenece_a)
                        clasePedido = gpedidos.value(subject=pedido, predicate=RDF.type)
                        prioridad = gpedidos.value(subject=pedido, predicate=ECSDI.prioridad)
                        print("prioridad "+ str(prioridad))
                        grf.add((pedido, RDF.type, Literal(clasePedido)))
                        grf.add((pedido, ECSDI.prioridad, Literal(prioridad)))
                        for s, p, o in gpedidos.triples((pedido, ECSDI.compuesto_de, None)):
                            print("dentro for pedidos")
                            gbultos = cargar_grafo_turtle(AgentUtil.Agents.path_bultos)
                            for su, pd, ob in gbultos.triples((o, ECSDI.compuesto_por, None)):
                                print("dentro for bultos")
                                gproductos = cargar_grafo_turtle(AgentUtil.Agents.path_productos)
                                codigo = gproductos.value(subject=ob, predicate=ECSDI.codigo)
                                nombre = gproductos.value(subject=ob, predicate=ECSDI.nombre)
                                print("nombre producto " + nombre)
                                precio = gproductos.value(subject=ob, predicate=ECSDI.precio)
                                descripcion = gproductos.value(subject=ob, predicate=ECSDI.descripcion)
                                tipo = gproductos.value(subject=ob, predicate=ECSDI.tipo)
                                valoracion = gproductos.value(subject=ob, predicate=ECSDI.valoracion)
                                calidad = gproductos.value(subject=ob, predicate=ECSDI.calidad)
                                clase = gproductos.value(subject=ob, predicate=RDF.type)
                                grf.add((ob, RDF.type, Literal(clase)))
                                grf.add((ob, ECSDI.codigo, Literal(codigo)))
                                grf.add((ob, ECSDI.nombre, Literal(nombre)))
                                grf.add((ob, ECSDI.precio, Literal(precio)))
                                grf.add((ob, ECSDI.descripcion, Literal(descripcion)))
                                grf.add((ob, ECSDI.tipo, Literal(tipo)))
                                grf.add((ob, ECSDI.valoracion, Literal(valoracion)))
                                grf.add((ob, ECSDI.calidad, Literal(calidad)))
                    gr = build_message(grf, ACL.inform, sender=AgentUtil.Agents.AgenteInformador.uri)

            else:
                gr = build_message(Graph(), ACL['not-understood'], sender=AgentUtil.Agents.AgenteInformador.uri,
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
    app.run(host=AgentUtil.Agents.hostname, port=AgentUtil.Agents.INFORMADOR_PORT)

    # Esperamos a que acaben los behaviors
    ab1.join()
    print('The End')


