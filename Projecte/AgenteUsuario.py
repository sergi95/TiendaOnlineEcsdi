import os
import random
from multiprocessing import Process, Queue
import socket

from rdflib import Namespace, Graph, RDF, URIRef, Literal
from flask import Flask, request, render_template, redirect, url_for

from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.Agent import Agent
import AgentUtil.Agents
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.OntoNamespaces import ACL, ECSDI
from AgentUtil.ConsistenciaUtil import cargar_grafo_turtle, guardar_grafo_turtle
from operator import itemgetter

from rdflib.query import ResultParser, ResultSerializer, \
    Processor, Result, UpdateProcessor
import rdflib
from rdflib import plugin

plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')
plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

agn = Namespace("http://www.agentes.org#")

# Contador de mensajes
mss_cnt = 0

# Global triplestore graph
dsgraph = Graph()

cola1 = Queue()

# Flask stuff
app = Flask(__name__,template_folder="Usuario/templates")


# def cargarGrafo():
#     g = Graph()
#     if os.path.isfile(AgentUtil.Agents.path_productos):
#         g.parse(AgentUtil.Agents.path_productos, format="xml")
#     return g
#
# def guardarCarrito(graph):
#     file = open(AgentUtil.Agents.path_carrito, "w+")
#
#     graph.serialize(destination=file, format="xml")
#
#     file.flush()
#
#     file.close()
#
# def cargarCarrito():
#     g = Graph()
#     if os.path.isfile(AgentUtil.Agents.path_carrito):
#         g.parse(AgentUtil.Agents.path_carrito, format="xml")
#     return g

gcarrito = Graph()
gcarrito.bind('escdi', ECSDI)


@app.route("/")
def paginaPrincipal():
    """
    El hola mundo de los servicios web
    :return:
    """
    return render_template('main.html')


@app.route("/buscar")
def buscar():
    """
    Entrada que sirve una pagina de web que cuenta hasta 10
    :return:
    """
    return render_template('buscarProductos.html')


@app.route("/buscarProductos", methods=['GET','POST'])
def buscarProductos():
    # criterio = request.args['criterio']
    tipo = request.args['tipo']
    calidad = request.args['calidad']
    valMin = request.args['valMin']
    print("criterio buscar: "+tipo)
    print("criterio buscar: " + calidad)
    print("criterio buscar: " + valMin)

    gm = Graph()
    gm.bind('ecsdi', ECSDI)
    content = ECSDI['Buscar']
    gm.add((content, ECSDI.tipo, Literal(tipo)))
    gm.add((content, ECSDI.calidad, Literal(calidad)))
    gm.add((content, ECSDI.valoracionMinima, Literal(valMin)))


    # numero mensaje???????
    msg = build_message(gm, perf=ACL.request,
                        sender=AgentUtil.Agents.AgenteUsuario.uri,
                        receiver=AgentUtil.Agents.AgenteBusquedas.uri,
                        content=content)
    # graf amb tots els productes relacionats amb el criteri de busqueda
    gr = send_message(msg, AgentUtil.Agents.AgenteBusquedas.address)
    print("grafo")
    print(gr)

    ls = []

    for (s,p,o) in gr:
        print("sujeto "+s)
        print("predicado "+p)
        print("objeto "+o)
        ls.append(s)

    msgdic = get_message_properties(gr)
    perf = msgdic['performative']
    if (perf ==ACL.inform):
        msg = "ok"
        list = []
        #Todos los productos tienen el predicado "type" a productos.type.
        #De esta forma los obtenemos con mas facilidad y sin consulta sparql
        #La funcoin subjects retorna los sujetos con tal predicado y objeto
        for sujeto in gr.subjects(predicate=ECSDI.tipo, object=Literal(tipo)):
            # Anadimos los atributos que queremos renderizar a la vista
            print("dentro for")

            datosProd = {}
            datosProd['codigo'] = gr.value(subject=sujeto, predicate=ECSDI.codigo)
            datosProd['nombre'] = gr.value(subject=sujeto, predicate=ECSDI.nombre)
            datosProd['precio'] = gr.value(subject=sujeto, predicate=ECSDI.precio)
            datosProd['descripcion'] = gr.value(subject=sujeto, predicate=ECSDI.descripcion)
            datosProd['tipo'] = gr.value(subject=sujeto, predicate=ECSDI.tipo)
            datosProd['valoracion'] = gr.value(subject=sujeto, predicate=ECSDI.valoracion)
            datosProd['calidad'] = gr.value(subject=sujeto, predicate=ECSDI.calidad)
            list = list + [datosProd]
        l = sorted(list, key=itemgetter('codigo'))
    else:
        msg = "error mensaje"

    #Renderizamos la vista
    return render_template('resultadoBusqueda.html', tipo=tipo, calidad=calidad, valMin=valMin, list=l, msg=msg)


@app.route("/anadirCarrito", methods=['GET','POST'])
def anadirCarrito():
    global gcarrito
    dicreq = request.args
    redir = dicreq['redirect']
    tipoEleccion = dicreq['tipo']
    calidadEleccion = dicreq['calidad']
    valMin = dicreq['valMin']
    cod = dicreq['codigo']
    print("codigo "+str(cod))
    gproductos = cargar_grafo_turtle(AgentUtil.Agents.path_productos)

    # gp = gproductos.query("""
    # prefix ecsdi:<http://www.semanticweb.org/usuario/ontologies/2018/4/ecsdi#>
    # SELECT ?x
    # WHERE {
    #     ?x ecsdi:codigo %s .
    # """ % cod)
    # gp = gproductos.query("""
    #     prefix ecsdi:<http://www.semanticweb.org/usuario/ontologies/2018/4/ecsdi#>
    #     SELECT ?x
    #     WHERE {
    #         ?x ecsdi:codigo '%d'
    #     """, cod)
    # gcarrito += gp
    # sub = gproductos.subjects(ECSDI.codigo, Literal(cod))
    # gcarrito += gproductos.triples(ECSDI.codigo, Literal(cod))
    # gcarrito = cargarCarrito()
    # gcarrito = gproductos.triples((None, ECSDI.codigo, cod))

    # sub = gproductos.subjects(ECSDI.codigo, Literal(cod))
    # gcarrito.add((sub[0], ECSDI.codigo, Literal(cod)))

    nombre = gproductos.value(subject=ECSDI['Producto'+cod], predicate=ECSDI.nombre)
    print("----"+ nombre)
    precio = gproductos.value(subject=ECSDI['Producto'+cod], predicate=ECSDI.precio)
    descripcion = gproductos.value(subject=ECSDI['Producto'+cod], predicate=ECSDI.descripcion)
    tipo = gproductos.value(subject=ECSDI['Producto'+cod], predicate=ECSDI.tipo)
    print("---"+tipo)
    valoracion = gproductos.value(subject=ECSDI['Producto'+cod], predicate=ECSDI.valoracion)
    type = gproductos.value(subject=ECSDI['Producto'+cod], predicate=RDF.type)
    calidad = gproductos.value(subject=ECSDI['Producto' + cod], predicate=ECSDI.calidad)

    gcarrito.add((ECSDI['Producto'+cod], RDF.type, Literal(type)))
    gcarrito.add((ECSDI['Producto'+cod], ECSDI.codigo, Literal(cod)))
    gcarrito.add((ECSDI['Producto'+cod], ECSDI.nombre, Literal(nombre)))
    gcarrito.add((ECSDI['Producto'+cod], ECSDI.precio, Literal(precio)))
    gcarrito.add((ECSDI['Producto'+cod], ECSDI.descripcion, Literal(descripcion)))
    gcarrito.add((ECSDI['Producto'+cod], ECSDI.tipo, Literal(tipo)))
    gcarrito.add((ECSDI['Producto'+cod], ECSDI.valoracion, Literal(valoracion)))
    gcarrito.add((ECSDI['Producto' + cod], ECSDI.calidad, Literal(calidad)))
    # guardarCarrito(gcarrito)

    print("-------------------------------------")
    for (s,p,o) in gcarrito:
        print("carrito")
        print("sujeto " + s)
        print("predicado " + p)
        print("objeto " + o)

    return redirect(url_for("." + redir, tipo=tipoEleccion, calidad=calidadEleccion, valMin=valMin))


@app.route("/verCarrito", methods=['GET','POST'])
def verCarrito():
    global gcarrito
    # gcarrito = cargarCarrito()
    list = []
    for s in gcarrito.subjects(predicate=RDF.type, object=Literal('ProductoPropio')):
        # Anadimos los atributos que queremos renderizar a la vista
        datosProd = {}
        datosProd['codigo'] = gcarrito.value(subject=s, predicate=ECSDI.codigo)
        datosProd['nombre'] = gcarrito.value(subject=s, predicate=ECSDI.nombre)
        datosProd['precio'] = gcarrito.value(subject=s, predicate=ECSDI.precio)
        datosProd['descripcion'] = gcarrito.value(subject=s, predicate=ECSDI.descripcion)
        datosProd['tipo'] = gcarrito.value(subject=s, predicate=ECSDI.tipo)
        datosProd['valoracion'] = gcarrito.value(subject=s, predicate=ECSDI.valoracion)
        datosProd['calidad'] = gcarrito.value(subject=s, predicate=ECSDI.calidad)
        list = list + [datosProd]

    l = sorted(list, key=itemgetter('codigo'))

    return render_template('verCarrito.html', list=l)


@app.route("/eliminarProductoCarrito", methods=['GET','POST'])
def eliminarProductoCarrito():
    global gcarrito
    dicreq = request.args
    cod = dicreq['codigo']

    # gcarrito = cargarCarrito()
    gcarrito.remove((ECSDI['Producto'+cod], None, None))
    # guardarCarrito(gcarrito)

    return redirect("/verCarrito")


@app.route("/vaciarCarrito", methods=['GET','POST'])
def vaciarCarrito():
    global gcarrito
    # gcarrito = cargarCarrito()
    gcarrito = Graph()
    # guardarCarrito(gcarrito)

    return redirect("/verCarrito")


@app.route("/realizarPedido", methods=['POST'])
def realizarPedido():
    global gcarrito
    dicreq = request.form
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    ciudad = request.form.get("ciudad")
    tarjeta = request.form.get("tarjeta")
    direccion = request.form.get("direccion")
    urgencia = request.form.get("urgencia")
    print("urgencia " + urgencia)

    gc = cargar_grafo_turtle(AgentUtil.Agents.path_clientes)
    gc.add((ECSDI['Cliente' + email], ECSDI.nombre, Literal(nombre)))
    gc.add((ECSDI['Cliente' + email], ECSDI.email, Literal(email)))
    gc.add((ECSDI['Cliente' + email], ECSDI.localizacion, Literal(ciudad)))
    gc.add((ECSDI['Cliente' + email], ECSDI.tarjeta, Literal(tarjeta)))
    gc.add((ECSDI['Cliente' + email], ECSDI.direccion, Literal(direccion)))
    guardar_grafo_turtle(gc, AgentUtil.Agents.path_clientes)
    gm = Graph()
    gm.bind('ecsdi', ECSDI)
    content = ECSDI['ordenCompra']
    gm.add((content, ECSDI.email, Literal(email)))
    gm.add((content, ECSDI.urgencia, Literal(urgencia)))

    gm += gcarrito

    msg = build_message(gm, perf=ACL.request,
                        sender=AgentUtil.Agents.AgenteUsuario.uri,
                        receiver=AgentUtil.Agents.AgenteDistribuidorBultos.uri,
                        content=content)
    # graf amb tots els productes relacionats amb el criteri de busqueda
    gr = send_message(msg, AgentUtil.Agents.AgenteDistribuidorBultos.address)



    msgdic = get_message_properties(gr)
    perf = msgdic['performative']
    if (perf == ACL.agree):
        mensaje = "Su pedido ha sido recibido correctamente!"

    else:
        mensaje = "Ha habido un error al enviar el pedido!"


    # gcarrito = cargarCarrito()

    # Realizar pedido contactar con agente distribuidor bultos

    gcarrito = Graph()


    # guardarCarrito(gcarrito)

    return render_template('mensajePedidoEnviado.html', mensaje=mensaje)


@app.route("/verFacturasPrevias")
def verFacturasPrevias():
    dicreq = request.args
    email = dicreq['email']

    gm = Graph()
    gm.bind('ecsdi', ECSDI)
    content = ECSDI['obtenerFacturasPrevias']
    gm.add((content, ECSDI.email, Literal(email)))

    msg = build_message(gm, perf=ACL.request,
                        sender=AgentUtil.Agents.AgenteUsuario.uri,
                        receiver=AgentUtil.Agents.AgenteInformador.uri,
                        content=content)

    gr = send_message(msg, AgentUtil.Agents.AgenteInformador.address)

    msgdic = get_message_properties(gr)
    perf = msgdic['performative']

    if (perf == ACL.inform):
        msg = "ok"
        print("ok dentro")
        l = []

        for sujeto in gr.subjects(predicate=RDF.type, object=Literal('FacturaPrevia')):
            # Anadimos los atributos que queremos renderizar a la vista
            print("dentro for")

            codigo = gr.value(subject=sujeto, predicate=ECSDI.codigo)
            l.append(codigo)

    else:
        print("bad rquest")
        msg = "error mensaje"

    # Renderizamos la vista
    return render_template('listadoFacturasPrevias.html', list=l, msg=msg)


@app.route("/mostrarFacturaPrevia")
def mostrarFacturaPrevia():
    dicreq = request.args
    codigo = dicreq['codigo']

    gm = Graph()
    gm.bind('ecsdi', ECSDI)
    content = ECSDI['obtenerFacturaPrevia']
    gm.add((content, ECSDI.codigo, Literal(codigo)))

    msg = build_message(gm, perf=ACL.request,
                        sender=AgentUtil.Agents.AgenteUsuario.uri,
                        receiver=AgentUtil.Agents.AgenteInformador.uri,
                        content=content)

    gr = send_message(msg, AgentUtil.Agents.AgenteInformador.address)

    msgdic = get_message_properties(gr)
    perf = msgdic['performative']
    if (perf == ACL.inform):
        msg = "ok"
        list = []

        for sujeto in gr.subjects(predicate=RDF.type, object=Literal('ProductoPropio')):

            print("dentro for productos")

            datosProd = {}
            datosProd['codigo'] = gr.value(subject=sujeto, predicate=ECSDI.codigo)
            datosProd['nombre'] = gr.value(subject=sujeto, predicate=ECSDI.nombre)
            datosProd['precio'] = gr.value(subject=sujeto, predicate=ECSDI.precio)
            datosProd['descripcion'] = gr.value(subject=sujeto, predicate=ECSDI.descripcion)
            datosProd['tipo'] = gr.value(subject=sujeto, predicate=ECSDI.tipo)
            datosProd['valoracion'] = gr.value(subject=sujeto, predicate=ECSDI.valoracion)
            datosProd['calidad'] = gr.value(subject=sujeto, predicate=ECSDI.calidad)
            list = list + [datosProd]
        l = sorted(list, key=itemgetter('codigo'))
        for pedido in gr.subjects(predicate=RDF.type, object=Literal('Pedido')):
            print("dentro for pedido")
            datosProd = {}
            prioridad = gr.value(subject=pedido, predicate=ECSDI.prioridad)
            print("prioridad " + str(prioridad))
            # datosProd['prioridadPedido'] = gr.value(subject=pedido, predicate=ECSDI.prioridad)
            datosProd['prioridadPedido'] = int(prioridad)
            l = l + [datosProd]
    else:
        msg = "error mensaje"

    # Renderizamos la vista
    return render_template('mostrarFacturaPrevia.html', list=l, msg=msg)


@app.route("/comm")
def comunicacion():
    """
    Entrypoint de comunicacion
    """
    global dsgraph
    global mss_cnt
    pass


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
    app.run(host=AgentUtil.Agents.hostname, port=AgentUtil.Agents.USUARIO_PORT)

    # Esperamos a que acaben los behaviors
    ab1.join()
    print('The End')
