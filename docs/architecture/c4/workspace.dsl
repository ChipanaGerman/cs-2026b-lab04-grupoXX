workspace "PicanteriaYa" "Modelo C4 de la plataforma de delivery de picanterias arequipenas" {

    !identifiers hierarchical

    model {

        # ─────────────────────────────────────────────────────────────────
        # PERSONAS
        # ─────────────────────────────────────────────────────────────────
        cliente = person "Cliente" "Persona que consulta el menu del dia de una picanteria, realiza pedidos y paga con Yape desde su celular o navegador."
        picanteria = person "Picanteria" "Negocio que publica su menu diario con stock disponible y atiende los pedidos confirmados."
        repartidor = person "Repartidor" "Persona que recibe la asignacion del pedido, lo recoge en la picanteria y lo entrega al cliente."

        # ─────────────────────────────────────────────────────────────────
        # SISTEMA PRINCIPAL
        # ─────────────────────────────────────────────────────────────────
        picanteriaYa = softwareSystem "PicanteriaYa" "Plataforma de delivery de picanterias arequipenas: permite consultar menus, hacer pedidos, pagar con Yape y rastrear al repartidor en tiempo real." {

            # Nivel 2: Contenedores
            pwa = container "App Cliente / PWA" "Interfaz web progresiva para que el cliente consulte el menu, arme su pedido y siga al repartidor en el mapa. Funciona sin conexion intermitente." "React + Service Worker" "Web Browser"

            appRepartidor = container "App Repartidor" "Aplicacion movil que recibe la asignacion del pedido, muestra la ruta a la picanteria y permite actualizar la posicion GPS." "React Native" "Mobile App"

            api = container "API PicanteriaYa" "Monolito modular Django REST Framework que implementa todos los casos de uso mediante una API REST y WebSocket." "Python / Django REST Framework" {

                # Nivel 3: Componentes del contenedor principal
                modMenu = component "Modulo Menu" "Publica y actualiza el menu diario de cada picanteria con su stock disponible. Sirve el catalogo al cliente." "Django app"
                modPedidos = component "Modulo Pedidos" "Gestiona el carrito, la confirmacion y el ciclo de vida del pedido (RECIBIDO, PAGADO, PREPARANDO, EN_CAMINO, ENTREGADO, CANCELADO)." "Django app"
                modPagos = component "Modulo Pagos" "Procesa el cobro con Yape a traves del puerto PasarelaPago hacia Culqi. Registra el resultado en el pedido." "Django app"
                modRepartidores = component "Modulo Repartidores" "Asigna el repartidor disponible mas cercano a la picanteria. Encola la tarea de asignacion en Celery." "Django app + Django Channels"
                modNotificaciones = component "Modulo Notificaciones" "Envia notificaciones push al cliente y mensajes WhatsApp a la picanteria sobre el estado del pedido." "Django app"
            }

            worker = container "Worker de tareas" "Ejecuta de forma asincrona la asignacion de repartidores, el reintento de notificaciones y la limpieza de pedidos expirados." "Celery"

            db = container "Base de datos" "Almacena usuarios, picanterias, menus, pedidos, pagos y repartidores. Esquema separado por modulo para respetar los limites del ADR-001." "PostgreSQL 16" "Database"

            cola = container "Cola y cache" "Cola de tareas Celery para el procesamiento asincrono del pico dominical (hasta 400 pedidos/hora). Cache de menus del dia para reducir consultas a la base de datos." "Redis 7" "Queue"

            wsGPS = container "Canal WebSocket / GPS" "Canal WebSocket gestionado por Django Channels que envia actualizaciones de posicion GPS del repartidor al cliente en tiempo real." "Django Channels + Redis" "Queue"
        }

        # ─────────────────────────────────────────────────────────────────
        # SISTEMAS EXTERNOS
        # ─────────────────────────────────────────────────────────────────
        culqi = softwareSystem "Culqi (Pasarela de pagos)" "Proveedor intermediario que procesa cobros con Yape en nombre de PicanteriaYa. Requerido porque Yape no tiene API publica abierta (restriccion R-05 del ADR-001)." "Externo"

        googleMaps = softwareSystem "Google Maps API" "API de mapas y geolocalizacion para calcular distancias entre repartidores y picanterias, y mostrar el mapa de seguimiento al cliente. Controlado para no superar el nivel gratuito (R-06)." "Externo"

        whatsappFcm = softwareSystem "WhatsApp / FCM" "Servicio de mensajeria y notificaciones push: WhatsApp Business API para avisos a la picanteria y FCM para notificaciones al cliente en la app." "Externo"

        # ─────────────────────────────────────────────────────────────────
        # RELACIONES — Nivel 1 (contexto)
        # ─────────────────────────────────────────────────────────────────
        cliente -> picanteriaYa "Consulta menu, realiza pedidos y paga"
        picanteria -> picanteriaYa "Publica y actualiza el menu diario"
        repartidor -> picanteriaYa "Recibe asignaciones y actualiza su posicion GPS"
        picanteriaYa -> culqi "Solicita cobros con Yape" "HTTPS/JSON"
        picanteriaYa -> googleMaps "Calcula distancias y rutas" "HTTPS/JSON"
        picanteriaYa -> whatsappFcm "Envia notificaciones de estado del pedido" "HTTPS/JSON"

        # ─────────────────────────────────────────────────────────────────
        # RELACIONES — Nivel 2 (contenedores)
        # ─────────────────────────────────────────────────────────────────
        cliente -> picanteriaYa.pwa "Usa para consultar menu, pedir y seguir al repartidor" "HTTPS"
        picanteria -> picanteriaYa.pwa "Usa para publicar el menu y ver pedidos asignados" "HTTPS"
        repartidor -> picanteriaYa.appRepartidor "Usa para recibir pedidos y actualizar posicion GPS" "HTTPS"

        picanteriaYa.pwa -> picanteriaYa.api "Llama a la API REST" "HTTPS/JSON"
        picanteriaYa.appRepartidor -> picanteriaYa.api "Envia actualizaciones de posicion GPS" "HTTPS/JSON"
        picanteriaYa.pwa -> picanteriaYa.wsGPS "Se suscribe al canal WebSocket para seguimiento en tiempo real" "WebSocket"

        picanteriaYa.api -> picanteriaYa.db "Lee y escribe datos de todos los modulos" "SQL/TCP"
        picanteriaYa.api -> picanteriaYa.cola "Encola tareas de asignacion y lee cache de menus" "Redis protocol"
        picanteriaYa.api -> picanteriaYa.wsGPS "Publica actualizaciones de posicion GPS" "Redis protocol"
        picanteriaYa.worker -> picanteriaYa.cola "Consume y procesa tareas asincronas" "Redis protocol"
        picanteriaYa.worker -> picanteriaYa.db "Lee y escribe datos de asignacion y notificaciones" "SQL/TCP"
        picanteriaYa.worker -> culqi "Reintenta cobros fallidos" "HTTPS/JSON"
        picanteriaYa.worker -> whatsappFcm "Envia mensajes y notificaciones push" "HTTPS/JSON"
        picanteriaYa.api -> culqi "Solicita cobro inicial con Yape" "HTTPS/JSON"
        picanteriaYa.api -> googleMaps "Calcula distancia repartidor-picanteria para asignacion" "HTTPS/JSON"

        # ─────────────────────────────────────────────────────────────────
        # RELACIONES — Nivel 3 (componentes dentro de la API)
        # ─────────────────────────────────────────────────────────────────
        picanteriaYa.pwa -> picanteriaYa.api.modMenu "Consulta menu y stock del dia" "HTTPS/JSON"
        picanteriaYa.pwa -> picanteriaYa.api.modPedidos "Crea y confirma pedidos" "HTTPS/JSON"
        picanteriaYa.api.modPedidos -> picanteriaYa.api.modMenu "Reserva stock de platos al confirmar"
        picanteriaYa.api.modPedidos -> picanteriaYa.api.modPagos "Solicita el cobro al confirmar el pedido"
        picanteriaYa.api.modPedidos -> picanteriaYa.api.modRepartidores "Solicita asignacion de repartidor tras pago exitoso"
        picanteriaYa.api.modPedidos -> picanteriaYa.api.modNotificaciones "Pide notificar al cliente y picanteria"
        picanteriaYa.api.modPagos -> culqi "Cobra con Yape via Culqi" "HTTPS/JSON"
        picanteriaYa.api.modRepartidores -> picanteriaYa.cola "Encola la tarea de asignacion del repartidor mas cercano" "Redis protocol"
        picanteriaYa.api.modRepartidores -> googleMaps "Calcula distancia entre repartidores disponibles y la picanteria" "HTTPS/JSON"
        picanteriaYa.api.modNotificaciones -> picanteriaYa.cola "Encola mensajes para envio asincrono" "Redis protocol"
        picanteriaYa.api.modMenu -> picanteriaYa.db "Lee y escribe menus y stock" "SQL"
        picanteriaYa.api.modPedidos -> picanteriaYa.db "Lee y escribe pedidos y lineas de pedido" "SQL"

        # ─────────────────────────────────────────────────────────────────
        # VISTA DE DESPLIEGUE — Entorno Produccion
        # ─────────────────────────────────────────────────────────────────
        produccion = deploymentEnvironment "Produccion" {

            deploymentNode "Celular o navegador del cliente" "" "Android / iOS / navegador web moderno" {
                containerInstance picanteriaYa.pwa
            }

            deploymentNode "Celular del repartidor" "" "Android" {
                containerInstance picanteriaYa.appRepartidor
            }

            deploymentNode "VPS en la nube" "" "Ubuntu 24.04 LTS, 2 vCPU, 4 GB RAM, ~20 USD/mes (DigitalOcean / Linode)" {

                deploymentNode "Docker Compose" "" "Docker 27 + Docker Compose v2" {

                    deploymentNode "Contenedor Django + Gunicorn" "" "Python 3.12, Gunicorn 21" {
                        containerInstance picanteriaYa.api
                    }

                    deploymentNode "Contenedor Django Channels + Daphne" "" "Daphne 4, WebSocket" {
                        containerInstance picanteriaYa.wsGPS
                    }

                    deploymentNode "Contenedor Celery Worker" "" "Celery 5.3" {
                        containerInstance picanteriaYa.worker
                    }

                    deploymentNode "Contenedor PostgreSQL" "" "PostgreSQL 16" {
                        containerInstance picanteriaYa.db
                    }

                    deploymentNode "Contenedor Redis" "" "Redis 7 (cola + cache)" {
                        containerInstance picanteriaYa.cola
                    }
                }
            }
        }
    }

    # ─────────────────────────────────────────────────────────────────────
    # VISTAS
    # ─────────────────────────────────────────────────────────────────────
    views {

        # E1 — Nivel 1: Contexto del sistema
        systemContext picanteriaYa "Contexto" "Nivel 1: PicanteriaYa y su entorno. Muestra quienes usan el sistema y de que servicios externos depende, sin mostrar tecnologias internas." {
            include *
            autolayout lr
        }

        # E2 — Nivel 2: Contenedores
        container picanteriaYa "Contenedores" "Nivel 2: contenedores de PicanteriaYa. Cada caja es una unidad que se despliega por separado. Se muestran las tecnologias y los protocolos de comunicacion." {
            include *
            autolayout lr
        }

        # E3 — Nivel 3: Componentes de la API
        component picanteriaYa.api "Componentes" "Nivel 3: modulos del monolito modular (API PicanteriaYa). Coherente con el diagrama de paquetes del Laboratorio 05." {
            include *
            autolayout lr
        }

        # E4 — Vista dinamica: flujo critico "Pedir menu y pagar con Yape"
        dynamic picanteriaYa.api "PedirYPagar" "Vista dinamica: flujo critico del pedido del menu del dia y pago con Yape. Equivalente de alto nivel del diagrama de secuencia del Laboratorio 05." {
            picanteriaYa.pwa -> picanteriaYa.api.modMenu "1. Consulta menu y platos disponibles"
            picanteriaYa.pwa -> picanteriaYa.api.modPedidos "2. POST /pedidos/ con lineas seleccionadas"
            picanteriaYa.api.modPedidos -> picanteriaYa.api.modMenu "3. Reserva el stock de cada plato"
            picanteriaYa.api.modPedidos -> picanteriaYa.api.modPagos "4. Solicita el cobro al confirmar"
            picanteriaYa.api.modPagos -> culqi "5. Cobra con Yape via Culqi (HTTPS/JSON)"
            picanteriaYa.api.modPedidos -> picanteriaYa.api.modRepartidores "6. Solicita asignacion de repartidor"
            picanteriaYa.api.modRepartidores -> picanteriaYa.cola "7. Encola tarea de asignacion asincrona"
            picanteriaYa.api.modPedidos -> picanteriaYa.api.modNotificaciones "8. Pide notificar al cliente y picanteria"
            autolayout lr
        }

        # E5 — Vista de despliegue
        deployment picanteriaYa produccion "Despliegue" "Vista de despliegue del entorno de produccion: dispositivos del cliente y repartidor, VPS con Docker Compose. Coherente con la restriccion R-03 (presupuesto ~20 USD/mes)." {
            include *
            autolayout lr
        }

        # ─────────────────────────────────────────────────────────────────
        # ESTILOS (paleta C4 estandar + etiquetas de forma)
        # ─────────────────────────────────────────────────────────────────
        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
                fontSize 14
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
                background #438DD5
                color #ffffff
            }
            element "Queue" {
                shape pipe
                background #438DD5
                color #ffffff
            }
            element "Web Browser" {
                shape WebBrowser
            }
            element "Mobile App" {
                shape MobileDeviceLandscape
            }
        }
    }
}
