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
from AgentUtil.ConsistenciaUtil import cargar_grafo, guardar_grafo
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


                codigoPedido = random.randint(0, 999999999999)
                gclientes = cargar_grafo(AgentUtil.Agents.path_clientes)
                sujetoCliente = gclientes.subjects(predicate=ECSDI.email, object=email)

                print("----------------------------------")
                print(sujetoCliente)
                print(ECSDI.sujetoCliente)
                print(ECSDI[sujetoCliente])
                print(ECSDI['Cliente'+email])
                print("----------------------------------")


                gpedidos = cargar_grafo(AgentUtil.Agents.path_pedidos)
                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], RDF.type, Literal('Pedido')))
                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.codigo, Literal(codigoPedido)))
                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.estado, Literal(1)))
                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.prioridad, Literal(urgencia)))
                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.realizada_por, Literal(sujetoCliente)))

                gcentrosLogisticos = cargar_grafo(AgentUtil.Agents.path_centrosLogisticos)
                ciudad = gclientes.value(subject=sujetoCliente, predicate=ECSDI.localizacion)
                sujetoCentro = gcentrosLogisticos.subjects(predicate=ECSDI.localizacion, object=ciudad)

                gbultos = Graph()
                if not sujetoCentro is None:
                    l = []
                    for producto in gcopia.subjects(predicate=RDF.type, object='ProductoPropio'):
                        if (sujetoCentro, ECSDI.dispone_de, producto) in gcentrosLogisticos:
                            l.append(producto)
                            gcopia.remove((producto,None, None))
                    for producto in gcopia.subjects(predicate=RDF.type, object='ProductoAjenoEnvio'):
                        if (sujetoCentro, ECSDI.dispone_de, producto) in gcentrosLogisticos:
                            l.append(producto)
                            gcopia.remove((producto,None, None))
                    if not len(l) == 0:
                        codigoBulto = random.randint(0, 999999999999)
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], RDF.type, Literal('BultoEnvio')))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.codigo, Literal(codigoBulto)))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.estado, Literal(1)))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.asignado_a, Literal(sujetoCentro)))
                        for producto in l:
                            gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.compuesto_por, producto))
                    gcentrosLogisticos.remove((sujetoCentro,None,None))
                for centro in gcentrosLogisticos.subjects(predicate=RDF.type, object='CentroLogistico'):
                    l = []
                    for producto in gcopia.subjects(predicate=RDF.type, object='ProductoPropio'):
                        if (centro, ECSDI.dispone_de, producto) in gcentrosLogisticos:
                            l.append(producto)
                            gcopia.remove((producto, None, None))
                    for producto in gcopia.subjects(predicate=RDF.type, object='ProductoAjenoEnvio'):
                        if (centro, ECSDI.dispone_de, producto) in gcentrosLogisticos:
                            l.append(producto)
                            gcopia.remove((producto,None, None))
                    if not len(l) == 0:
                        codigoBulto = random.randint(0, 999999999999)
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], RDF.type, Literal('BultoEnvio')))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.codigo, Literal(codigoBulto)))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.estado, Literal(1)))
                        gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.asignado_a, Literal(centro)))
                        for producto in l:
                            gbultos.add((ECSDI['Bulto' + str(codigoBulto)], ECSDI.compuesto_por, Literal(producto)))


                for (sujetoBulto, p, o) in gbultos:
                    gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.compuesto_de, Literal(sujetoBulto)))

                gpedidos.add((ECSDI['Pedido' + str(codigoPedido)], ECSDI.realizada_por, Literal(sujetoCliente)))
                guardar_grafo(gpedidos, AgentUtil.Agents.path_pedidos)
                gbultosTotales = cargar_grafo(AgentUtil.Agents.path_bultos)
                gbultosTotales += gbultos
                guardar_grafo(gbultosTotales, AgentUtil.Agents.path_bultos)

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





------------------------------------------------------------------------------------------------------------------------

productos = Graph()
    productos.bind('escdi', ECSDI)

    id = 'Producto1'
    productos.add((ECSDI[id],RDF.type,Literal('ProductoPropio')))
    productos.add((ECSDI[id],ECSDI.codigo,Literal(1)))
    productos.add((ECSDI[id],ECSDI.nombre,Literal('zanahoria')))
    productos.add((ECSDI[id],ECSDI.precio,Literal(1.8)))
    productos.add((ECSDI[id],ECSDI.descripcion,Literal('ricas')))
    productos.add((ECSDI[id],ECSDI.tipo,Literal('hortalizas')))
    productos.add((ECSDI[id],ECSDI.valoracion,Literal(1.5)))

    id1 = 'Producto2'
    productos.add((ECSDI[id1], RDF.type, Literal('ProductoPropio')))
    productos.add((ECSDI[id1], ECSDI.codigo, Literal(2)))
    productos.add((ECSDI[id1], ECSDI.nombre, Literal('patata')))
    productos.add((ECSDI[id1], ECSDI.precio, Literal(1.8)))
    productos.add((ECSDI[id1], ECSDI.descripcion, Literal('monalisa')))
    productos.add((ECSDI[id1], ECSDI.tipo, Literal('hortalizas')))
    productos.add((ECSDI[id1], ECSDI.valoracion, Literal(1.5)))


    id2 = 'Producto3'

    productos.add((ECSDI[id2],RDF.type,Literal('ProductoPropio')))
    productos.add((ECSDI[id2],ECSDI.codigo,Literal(3)))
    productos.add((ECSDI[id2],ECSDI.nombre,Literal('zapatos')))
    productos.add((ECSDI[id2],ECSDI.precio,Literal(2.9)))
    productos.add((ECSDI[id2],ECSDI.descripcion,Literal("buenos buenos")))
    productos.add((ECSDI[id2],ECSDI.tipo,Literal('calzado')))
    productos.add((ECSDI[id2],ECSDI.valoracion,Literal(2.5)))

    file = open(AgentUtil.Agents.path_productos, "w+")

    productos.serialize(destination=file,format='turtle')

    file.flush()

    file.close()

    centrosLogisticos = Graph()
    centrosLogisticos.bind('escdi', ECSDI)

    codigo = random.randint(0, 999999999999)
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], RDF.type, Literal('CentroLogistico')))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.codigo, Literal(codigo)))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.localizacion, Literal('Barcelona')))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.dispone_de, ECSDI[id]))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.dispone_de, ECSDI[id1]))

    codigo = random.randint(0, 999999999999)
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], RDF.type, Literal('CentroLogistico')))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.codigo, Literal(codigo)))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.localizacion, Literal('Madrid')))
    centrosLogisticos.add((ECSDI['CentroLogistico' + str(codigo)], ECSDI.dispone_de, ECSDI[id2]))

    file = open(AgentUtil.Agents.path_centrosLogisticos, "w+")

    centrosLogisticos.serialize(destination=file, format='turtle')

    file.flush()

    file.close()