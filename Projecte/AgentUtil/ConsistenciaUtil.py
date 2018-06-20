import os

from rdflib import Namespace, Graph,RDF,Literal
from AgentUtil.OntoNamespaces import ECSDI


def cargar_grafo_xml(path):
    g = Graph()
    g.bind('ecsdi', ECSDI)
    if os.path.isfile(path):
        g.parse(path, format="xml")
    return g


def guardar_grafo_xml(graph, path):
    file = open(path, "w+")

    graph.serialize(destination=file, format="xml")

    file.flush()

    file.close()

def cargar_grafo_turtle(path):
    g = Graph()
    g.bind('ecsdi', ECSDI)
    if os.path.isfile(path):
        g.parse(path, format='turtle')
    return g


def guardar_grafo_turtle(graph, path):
    file = open(path, "w+")

    graph.serialize(destination=file, format='turtle')

    file.flush()

    file.close()
