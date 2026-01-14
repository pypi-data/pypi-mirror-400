# Innaguma MCP Server

Un servidor Model Context Protocol (MCP) que proporciona integración con la API de Innaguma para acceder a estadísticas, análisis de contenido y datos de gestión de plataformas.

## Descripción

Este MCP expone las funcionalidades principales de la API de Innaguma a través de herramientas fáciles de usar, permitiendo a los clientes MCP acceder a:

- **Estadísticas Totales**: Accesos, noticias, lectores, analistas, descargas, subidas y votos
- **Gestión de Lectores**: Información de usuarios, historial de visualizaciones, votos y descargas
- **Gestión de Noticias**: Listados, detalles, votos y estadísticas de visitas
- **Gestión de Categorías**: Categorías disponibles, suscriptores e información detallada
- **Gestión de Analistas**: Analistas, publicaciones y análisis de votación

## Instalación

### Requisitos
- Python 3.10+
- pip

### Pasos de instalación

1. Clona o crea el proyecto:
```bash
cd InnagunaMCP
```

2. Instala las dependencias:
```bash
pip install -e .
```

O instala las dependencias manualmente:
```bash
pip install fastmcp>=2.13.0 aiohttp>=3.9.0 python-dotenv>=1.0.0 pyjwt>=2.8.0
```

## Configuración

1. Copia el archivo `.env.example` a `.env`:
```bash
cp .env.example .env
```

2. Edita `.env` con tus credenciales de Innaguma:
```env
INNAGUMA_AUTH_URL=https://<tu-subdominio>.innguma.com
INNAGUMA_SITE=<tu-subdominio>
INNAGUMA_USERNAME=<tu-usuario>
INNAGUMA_PASSWORD=<tu-contraseña>
```

## Uso

### Iniciar el servidor

```bash
python MCP.py
```

O si está instalado como paquete:

```bash
innaguma-mcp
```

### Herramientas Disponibles

#### Búsqueda

- **search_innaguma(query, page, order)**: Busca contenido en Innaguma usando Elasticsearch
  - `query` - Término de búsqueda
  - `page` - Número de página (default: 1)
  - `order` - Orden: "relevance" o "date" (default: "relevance")

#### Estadísticas Totales

- **get_platform_totals()**: Obtiene estadísticas totales de la plataforma
- **get_users_totals()**: Obtiene estadísticas totales de usuarios
- **get_user_totals(user_id)**: Obtiene estadísticas de un usuario específico
- **get_news_totals()**: Obtiene estadísticas de noticias
- **get_categories_totals()**: Obtiene estadísticas de categorías
- **get_most_searched_words(from_date, to_date)**: Obtiene palabras más buscadas en rango de fechas

#### Lectores (Readers)

- **list_readers()**: Lista todos los lectores
- **get_readers_overview()**: Obtiene resumen completo de lectores
- **get_reader_overview(reader_id)**: Obtiene detalles de un lector específico
- **get_reader_viewed_news(reader_id)**: Obtiene noticias vistas por un lector
- **get_reader_voted_news(reader_id)**: Obtiene noticias votadas por un lector
- **get_reader_downloads(reader_id)**: Obtiene archivos descargados por un lector

#### Noticias

- **list_news_by_date(from_date, to_date)**: Lista noticias en rango de fechas
- **get_news_overview()**: Obtiene resumen de todas las noticias
- **get_news_details(news_id)**: Obtiene detalles de una noticia específica
- **get_news_votes(news_id)**: Obtiene votos de una noticia
- **get_news_visits(news_id)**: Obtiene visitas de una noticia

#### Categorías

- **list_categories()**: Lista todas las categorías
- **get_categories_overview()**: Obtiene resumen de categorías
- **get_category_details(category_id)**: Obtiene detalles de una categoría
- **get_category_subscriptions(category_id)**: Obtiene suscriptores de una categoría

#### Analistas

- **list_analysts()**: Lista todos los analistas
- **get_analysts_overview()**: Obtiene resumen de analistas
- **get_analyst_overview(analyst_id)**: Obtiene detalles de un analista
- **get_analyst_publications(analyst_id)**: Obtiene publicaciones de un analista
- **get_analyst_voted_publications(analyst_id)**: Obtiene publicaciones votadas de un analista

## Formato de Fechas

Las fechas deben proporcionarse en formato **YYYY-MM-DD**:
```
2024-01-15
2024-12-31
```

## Manejo de Errores

El servidor maneja los siguientes tipos de errores:

- **400 Bad Request**: Faltan cabeceras requeridas
- **401 Unauthorized**: Token de autenticación inválido o expirado
- **404 Not Found**: Recurso no encontrado o formato de fecha inválido
- **500 Internal Server Error**: Error interno del servidor

## Autenticación

El servidor obtiene automáticamente un token JWT durante la primera solicitud. El token se renovará automáticamente si expira (después de 30 días por defecto).

## Estructura del Proyecto

```
InnagunaMCP/
├── MCP.py                      # Servidor MCP principal
├── pyproject.toml              # Configuración del proyecto
├── .env.example                # Plantilla de variables de entorno
├── Especificaciones_API_Innguma.txt  # Especificaciones de la API
└── README.md                   # Este archivo
```

## Dependencias

- `fastmcp>=2.13.0`: Framework para Model Context Protocol
- `aiohttp>=3.9.0`: Cliente HTTP asincrónico
- `python-dotenv>=1.0.0`: Carga de variables de entorno
- `pyjwt>=2.8.0`: Soporte para tokens JWT
- `beautifulsoup4>=4.12.0`: Web scraping y parsing HTML
- `lxml>=4.9.0`: Parser XML/HTML rápido

## Licencia

Este proyecto es de uso interno de Ingeteam.

## Autor

Bruno Izaguirre - bruno.izaguirre@ingeteam.com
