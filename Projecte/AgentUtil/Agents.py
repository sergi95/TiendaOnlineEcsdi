import socket

from rdflib import Namespace

from AgentUtil.Agent import Agent
from AgentUtil.OntoNamespaces import ECSDI


USUARIO_PORT = 9000
BUSQUEDAS_PORT = 9001
CENTRO_LOGISTICO_PORT = 9002
DISTRIBUIDOR_BULTOS_PORT = 9003
GESTOR_DEVOLUCIONES_PORT = 9004
INFORMADOR_PORT = 9005
MEJORAR_PROCESOS_PORT = 9006
PRODUCTOS_PORT = 9007
TRANSACCIONES_PORT = 9008
TRANSPORTISTA_PORT = 9009
VENDEDOR3O_PORT = 9010
ESCRITURA_PORT = 9011
LECTURA_PORT = 9012

hostname = socket.gethostname()
# path_productos = 'Datos/productos.xml'
# path_clientes = 'Datos/clientes.xml'
# path_carrito = 'Datos/carrito.xml'
# path_lotes = 'Datos/lotes.xml'
# path_pedidos = 'Datos/pedidos.xml'
# path_bultos = 'Datos/bultos.xml'
# path_feedbacks = 'Datos/feedbacks.xml'
# path_centrosLogisticos = 'Datos/centrosLogisticos.xml'

path_productos = 'Datos/productos'
path_clientes = 'Datos/clientes'
path_carrito = 'Datos/carrito'
path_lotes = 'Datos/lotes'
path_pedidos = 'Datos/pedidos'
path_bultos = 'Datos/bultos'
path_feedbacks = 'Datos/feedbacks'
path_centrosLogisticos = 'Datos/centrosLogisticos'
path_facturas_previas = 'Datos/facturasPrevias'



AgenteUsuario = Agent('AgenteUsuario',
                        ECSDI.AgenteUsuario,
                        'http://%s:%d/comm' % (hostname, USUARIO_PORT),
                        'http://%s:%d/Stop' % (hostname, USUARIO_PORT))

AgenteBusquedas = Agent('AgenteBusquedas',
                        ECSDI.AgenteBusquedas,
                        'http://%s:%d/comm' % (hostname, BUSQUEDAS_PORT),
                        'http://%s:%d/Stop' % (hostname, BUSQUEDAS_PORT))

AgenteCentroLogistico = Agent('AgenteCentroLogistico',
                        ECSDI.AgenteCentroLogistico,
                        'http://%s:%d/comm' % (hostname, CENTRO_LOGISTICO_PORT),
                        'http://%s:%d/Stop' % (hostname, CENTRO_LOGISTICO_PORT))


AgenteDistribuidorBultos = Agent('AgenteDistribuidorBultos',
                        ECSDI.AgenteDistribuidorBultos,
                        'http://%s:%d/comm' % (hostname, DISTRIBUIDOR_BULTOS_PORT),
                        'http://%s:%d/Stop' % (hostname, DISTRIBUIDOR_BULTOS_PORT))

AgenteGestorDevoluciones = Agent('AgenteGestorDevoluciones',
                        ECSDI.AgenteGestorDevoluciones,
                        'http://%s:%d/comm' % (hostname, GESTOR_DEVOLUCIONES_PORT),
                        'http://%s:%d/Stop' % (hostname, GESTOR_DEVOLUCIONES_PORT))

AgenteInformador = Agent('AgenteInformador',
                        ECSDI.AgenteInformador,
                        'http://%s:%d/comm' % (hostname, INFORMADOR_PORT),
                        'http://%s:%d/Stop' % (hostname, INFORMADOR_PORT))

AgenteMejorarProcesos = Agent('AgenteMejorarProcesos',
                        ECSDI.AgenteMejorarProcesos,
                        'http://%s:%d/comm' % (hostname, MEJORAR_PROCESOS_PORT),
                        'http://%s:%d/Stop' % (hostname, MEJORAR_PROCESOS_PORT))

AgenteProductos = Agent('AgenteProductos',
                        ECSDI.AgenteProductos,
                        'http://%s:%d/comm' % (hostname, PRODUCTOS_PORT),
                        'http://%s:%d/Stop' % (hostname, PRODUCTOS_PORT))

AgenteTransacciones = Agent('AgenteTransacciones',
                        ECSDI.AgenteTransacciones,
                        'http://%s:%d/comm' % (hostname, TRANSACCIONES_PORT),
                        'http://%s:%d/Stop' % (hostname, TRANSACCIONES_PORT))

AgenteTransportista = Agent('AgenteTransportista',
                        ECSDI.AgenteTransportista,
                        'http://%s:%d/comm' % (hostname, TRANSPORTISTA_PORT),
                        'http://%s:%d/Stop' % (hostname, TRANSPORTISTA_PORT))

AgenteVendedor3o = Agent('AgenteVendedor3o',
                        ECSDI.AgenteVendedor3o,
                        'http://%s:%d/comm' % (hostname, VENDEDOR3O_PORT),
                        'http://%s:%d/Stop' % (hostname, VENDEDOR3O_PORT))

AgenteEscritura = Agent('AgenteEscritura',
                        ECSDI.AgenteEscritura,
                        'http://%s:%d/comm' % (hostname, ESCRITURA_PORT),
                        'http://%s:%d/Stop' % (hostname, ESCRITURA_PORT))

AgenteLectura = Agent('AgenteLectura',
                        ECSDI.AgenteLectura,
                        'http://%s:%d/comm' % (hostname, LECTURA_PORT),
                        'http://%s:%d/Stop' % (hostname, LECTURA_PORT))
