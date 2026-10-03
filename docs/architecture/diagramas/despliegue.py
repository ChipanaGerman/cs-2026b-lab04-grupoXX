"""
E6 — Vista de despliegue: PicanteríaYa
Herramienta: Python Diagrams (https://diagrams.mingrammer.com/)

Instalación previa:
    pip install diagrams
    # Instalar Graphviz en el sistema: https://graphviz.org/download/
    # Windows: winget install graphviz  o descargar el instalador de graphviz.org

Ejecución:
    python despliegue.py
    # Genera: picanteria_ya_despliegue.png en la carpeta actual
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.generic.device import Mobile
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import Django
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.queue import Celery
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Internet
from diagrams.saas.chat import Slack  # usado como proxy visual para WhatsApp/FCM
from diagrams.onprem.compute import Server

graph_attr = {
    "fontsize": "18",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
}

output_path = "img/picanteria_ya_despliegue"

with Diagram(
    "PicanteríaYa — Vista de Despliegue",
    filename=output_path,
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    outformat="png",
) as diag:

    # ── Usuarios / dispositivos ──────────────────────────────────────────────
    with Cluster("Usuarios y dispositivos"):
        clientes   = Users("Clientes\n(PWA en navegador)")
        picanterias = Mobile("Picanterías\n(panel web)")
        repartidores = Mobile("Repartidores\n(app móvil GPS)")

    # ── Servicios externos ───────────────────────────────────────────────────
    with Cluster("Servicios externos (nube terceros)"):
        culqi   = Internet("Culqi / Niubiz\n(pasarela Yape)")
        gmaps   = Internet("Google Maps API\n(seguimiento GPS)")
        notifext = Internet("FCM / WhatsApp API\n(notificaciones push)")

    # ── VPS — Servidor único en la nube ─────────────────────────────────────
    with Cluster("VPS (DigitalOcean / Linode ~$20/mes)"):

        proxy = Nginx("Nginx\n(reverse proxy HTTPS\n+ SSL/TLS)")

        with Cluster("Monolito Modular (Daphne ASGI)"):
            app = Django("Django RF + Channels\n(5 módulos de dominio:\nMenú · Pedidos · Pagos\nRepartidores · Notificaciones)")

        with Cluster("Procesamiento asíncrono"):
            cola  = Redis("Redis\n(cola Celery +\ncaché menús +\nChannel Layers WS)")
            worker = Celery("Workers Celery\n(asignación repartidor\npagos · notificaciones)")

        db  = PostgreSQL("PostgreSQL 16\n(esquema por módulo)")

        with Cluster("Monitoreo"):
            prom  = Prometheus("Prometheus\n(métricas)")
            graf  = Grafana("Grafana\n(dashboards)")

    # ── Conexiones ───────────────────────────────────────────────────────────
    clientes    >> Edge(label="HTTPS / WSS") >> proxy
    picanterias >> Edge(label="HTTPS")       >> proxy
    repartidores >> Edge(label="HTTPS / WSS GPS") >> proxy

    proxy >> Edge(label="proxy_pass") >> app

    app >> Edge(label="lectura / escritura") >> db
    app >> Edge(label="caché menús")         >> cola
    app >> Edge(label="encola tarea")        >> cola
    cola >> Edge(label="consume")            >> worker

    worker >> Edge(label="pago", style="dashed")         >> culqi
    worker >> Edge(label="notificación", style="dashed") >> notifext
    app    >> Edge(label="posición GPS", style="dashed") >> gmaps

    app  >> Edge(label="métricas", style="dotted") >> prom
    prom >> Edge(label="fuente")                   >> graf

print(f"✅ Diagrama generado en: {output_path}.png")
