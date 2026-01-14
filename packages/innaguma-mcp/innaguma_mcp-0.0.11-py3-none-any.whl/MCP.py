#!/usr/bin/env python3
"""
Innaguma MCP Server - Analytics and Content Management Integration
Provides tools for accessing Innaguma statistics API endpoints
"""

import os
import json
import logging
from typing import Any, Optional
from dotenv import load_dotenv
import aiohttp
from bs4 import BeautifulSoup
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("innaguma-mcp")

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(name="Innaguma MCP", version="0.0.1")

# Configuration
INNAGUMA_BASE_URL = os.getenv("INNAGUMA_BASE_URL", "https://u973mdkqc3.execute-api.eu-west-1.amazonaws.com/v1/stats")
INNAGUMA_AUTH_URL = os.getenv("INNAGUMA_AUTH_URL")
INNAGUMA_USERNAME = os.getenv("INNAGUMA_USERNAME")
INNAGUMA_PASSWORD = os.getenv("INNAGUMA_PASSWORD")
INNAGUMA_SITE = os.getenv("INNAGUMA_SITE")
JWT_TOKEN: Optional[str] = None

logger.info("Innaguma MCP Server initialized")
logger.info(f"Base URL: {INNAGUMA_BASE_URL}")
logger.info(f"Site: {INNAGUMA_SITE}")


def validate_config() -> None:
    """Validates that all required environment variables are set."""
    missing = []
    if not INNAGUMA_AUTH_URL:
        missing.append("INNAGUMA_AUTH_URL")
    if not INNAGUMA_USERNAME:
        missing.append("INNAGUMA_USERNAME")
    if not INNAGUMA_PASSWORD:
        missing.append("INNAGUMA_PASSWORD")
    if not INNAGUMA_SITE:
        missing.append("INNAGUMA_SITE")
    
    if missing:
        raise ToolError(f"Missing environment variables: {', '.join(missing)}")


async def get_jwt_token() -> str:
    """
    Obtiene un token JWT de la API de autenticación de Innaguma.
    Usa multipart/form-data según la especificación de la API.
    """
    global JWT_TOKEN
    
    validate_config()
    
    logger.info("Requesting new JWT token...")
    
    # Log RAW values before any manipulation
    raw_password = INNAGUMA_PASSWORD if INNAGUMA_PASSWORD else ""
    logger.info(f"RAW password from env: repr={repr(raw_password)}, length={len(raw_password)}")
    
    # Use raw values directly - NO strip() to avoid any character loss
    username = INNAGUMA_USERNAME if INNAGUMA_USERNAME else ""
    password = INNAGUMA_PASSWORD if INNAGUMA_PASSWORD else ""
    site = INNAGUMA_SITE if INNAGUMA_SITE else ""
    auth_url = INNAGUMA_AUTH_URL if INNAGUMA_AUTH_URL else ""
    
    # Build the correct auth URL according to API spec: https://<site>.innguma.com
    expected_auth_url = f"https://{site}.innguma.com"
    
    # Debug logging
    logger.info(f"=== Authentication Request Details ===")
    logger.info(f"Auth URL configured: {auth_url}")
    logger.info(f"Auth URL expected (per API spec): {expected_auth_url}")
    logger.info(f"Username: '{username}' (length: {len(username)})")
    logger.info(f"Password: first 2 chars='{password[:2] if len(password) >= 2 else password}', last 2 chars='{password[-2:] if len(password) >= 2 else password}' (total length: {len(password)})")
    logger.info(f"Site: '{site}'")
    logger.info(f"Form fields: username, passwd, efgroup=authentication, efevent=requestJWTToken, payload-options={{\"site\":\"{site}\"}}")
    logger.info(f"======================================")
    
    try:
        # Crear FormData para multipart/form-data (requerido por la API según especificación)
        # API spec: -F "username=..." -F "passwd=..." -F "efgroup=authentication" -F "efevent=requestJWTToken" -F "payload-options={...}"
        form_data = aiohttp.FormData()
        form_data.add_field("username", username)
        form_data.add_field("passwd", password)
        form_data.add_field("efgroup", "authentication")
        form_data.add_field("efevent", "requestJWTToken")
        form_data.add_field("payload-options", json.dumps({"site": site}))
        
        logger.info(f"Sending POST request to: {auth_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=form_data) as response:
                # Log response details
                logger.info(f"Response status: {response.status}")
                logger.info(f"Response content-type: {response.headers.get('Content-Type', 'unknown')}")
                
                # Get response text first (works for both JSON and HTML)
                text = await response.text()
                logger.info(f"Response body (first 500 chars): {text[:500]}")
                
                # Try to parse as JSON regardless of content-type
                try:
                    result = json.loads(text)
                    logger.info(f"Parsed JSON response: result={result.get('result')}, status={result.get('status')}, message={result.get('message')}")
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse response as JSON. Raw response: {text[:300]}")
                    raise ToolError(f"Invalid response format from auth server (not JSON): {text[:200]}")
                
                # Check if authentication was successful
                # Token is nested in result["data"]["token"], not at the top level
                if result.get("result") == True and result.get("data", {}).get("token"):
                    JWT_TOKEN = result["data"]["token"]
                    logger.info("JWT token obtained successfully!")
                    logger.info(f"Token expires at: {result.get('data', {}).get('expiration')}")
                    logger.info(f"User: {result.get('data', {}).get('userData', {}).get('name')}")
                    return JWT_TOKEN
                else:
                    # Authentication failed - log ALL details from the response
                    error_msg = result.get("message", "No message provided")
                    error_status = result.get("status", response.status)
                    error_result = result.get("result")
                    
                    logger.error(f"=== Authentication Failed ===")
                    logger.error(f"HTTP Status: {response.status}")
                    logger.error(f"API result: {error_result}")
                    logger.error(f"API status: {error_status}")
                    logger.error(f"API message: {error_msg}")
                    logger.error(f"Full response: {result}")
                    logger.error(f"=============================")
                    
                    raise ToolError(f"Authentication failed (status {error_status}): {error_msg}")
    except aiohttp.ClientError as e:
        logger.error(f"Network error during authentication: {str(e)}")
        raise ToolError(f"Network error during authentication: {str(e)}")
    except Exception as e:
        if isinstance(e, ToolError):
            raise
        logger.error(f"Failed to get authentication token: {str(e)}")
        raise ToolError(f"Failed to get authentication token: {str(e)}")


async def make_request(endpoint: str, params: Optional[dict] = None) -> Any:
    """
    Realiza una solicitud autenticada a la API de Innaguma.
    """
    global JWT_TOKEN
    
    validate_config()
    
    if not JWT_TOKEN:
        JWT_TOKEN = await get_jwt_token()
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
        "X-site": INNAGUMA_SITE,
        "X-secret": f"prod/corporate/{INNAGUMA_SITE}"
    }
    
    url = f"{INNAGUMA_BASE_URL}{endpoint}"
    logger.info(f"Making request to: {endpoint}")
    if params:
        logger.debug(f"Request params: {params}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                # Intentar parsear como JSON en todos los casos
                try:
                    response_data = await response.json()
                except aiohttp.ContentTypeError:
                    response_data = None
                
                if response.status == 401:
                    # Token expirado, renovar y reintentar
                    logger.warning("Token expired, refreshing...")
                    JWT_TOKEN = await get_jwt_token()
                    headers["Authorization"] = f"Bearer {JWT_TOKEN}"
                    async with session.get(url, headers=headers, params=params) as retry_response:
                        try:
                            retry_data = await retry_response.json()
                        except aiohttp.ContentTypeError:
                            retry_data = None
                        
                        if retry_response.status == 200:
                            logger.info(f"Request successful after token refresh: {endpoint}")
                            return retry_data
                        else:
                            error_msg = retry_data.get('message', 'Unknown error') if retry_data else await retry_response.text()
                            logger.error(f"API Error after retry ({retry_response.status}): {error_msg}")
                            raise ToolError(f"API Error after retry ({retry_response.status}): {str(error_msg)[:200]}")
                
                elif response.status == 200:
                    logger.info(f"Request successful: {endpoint}")
                    return response_data
                
                elif response.status == 404:
                    error_msg = response_data.get('message', 'Resource not found') if response_data else await response.text()
                    logger.warning(f"Not Found (404): {error_msg}")
                    raise ToolError(f"Not Found: {str(error_msg)[:200]}")
                
                else:
                    error_msg = response_data.get('message', 'Unknown error') if response_data else await response.text()
                    logger.error(f"API Error ({response.status}): {error_msg}")
                    raise ToolError(f"API Error ({response.status}): {str(error_msg)[:200]}")
    
    except aiohttp.ClientError as e:
        logger.error(f"Network error: {str(e)}")
        raise ToolError(f"Network error: {str(e)}")
    except Exception as e:
        if isinstance(e, ToolError):
            raise
        logger.error(f"Request failed: {str(e)}")
        raise ToolError(f"Request failed: {str(e)}")


# ============================================================================
# SEARCH (ELASTICSEARCH) ENDPOINT
# ============================================================================

@mcp.tool(name="search_innaguma", description="Search content in Innaguma using Elasticsearch. Returns search results with titles and links.")
async def search_innaguma(query: str, ctx: Context, page: int = 1, order: str = "relevance") -> dict:
    """
    Search content in Innaguma using the built-in search functionality.
    
    Args:
        query: Search term
        page: Page number (default: 1)
        order: Sort order - 'relevance' or 'date' (default: 'relevance')
    
    Returns:
        Dictionary with search results including titles and links
    """
    validate_config()
    
    # Extract site domain from INNAGUMA_SITE
    search_url = f"https://{INNAGUMA_SITE}.innguma.com/index.php"
    
    params = {
        "option": "com_elasticsearch",
        "view": "search",
        "task": "search",
        "format": "html",
        "page": page,
        "order": order,
        "q": query,
        "form": "1"
    }
    
    logger.info(f"Searching Innaguma for: '{query}' (page {page}, order: {order})")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Search failed with status {response.status}")
                    raise ToolError(f"Search failed with status {response.status}")
                
                html_content = await response.text()
                logger.debug(f"Received HTML content ({len(html_content)} bytes)")
                
                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(html_content, 'lxml')
                
                results = []
                
                # Find the results container
                results_div = soup.find('div', id='results-list')
                if not results_div:
                    logger.warning("No results-list div found in HTML")
                    return {
                        "query": query,
                        "page": page,
                        "order": order,
                        "total_results": 0,
                        "results": []
                    }
                
                # Extract search results from <li class="search-result"> elements
                search_items = results_div.find_all('li', class_='search-result')
                
                # Map border colors to content types
                color_to_type = {
                    '#c7aab9': 'News',
                    '#b0b34c': 'Patents',
                    '#56727d': 'Articles',
                    '#ce0880': 'Books'
                }
                
                for item in search_items:
                    # Get the left column with content
                    left_column = item.find('div', class_='elastic-result-left-column')
                    if not left_column:
                        continue
                    
                    # Extract title and link
                    title_span = left_column.find('span', class_='title')
                    if not title_span:
                        continue
                    
                    link = title_span.find('a')
                    if not link:
                        continue
                    
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # Convert relative URLs to absolute if needed
                    if href and not href.startswith('http'):
                        href = f"https://{INNAGUMA_SITE}.innguma.com/{href}"
                    
                    # Extract date and content type
                    date_span = left_column.find('span', class_='date')
                    date_text = date_span.get_text(strip=True) if date_span else ''
                    
                    # Extract snippet
                    snippet_span = left_column.find('span', class_='snippet')
                    snippet = snippet_span.get_text(strip=True) if snippet_span else ''
                    
                    # Determine content type from border color
                    style = item.get('style', '')
                    content_type = 'Unknown'
                    for color, ctype in color_to_type.items():
                        if color in style:
                            content_type = ctype
                            break
                    
                    # Extract tags if available (right column)
                    tags = []
                    right_column = item.find('div', class_='elastic-result-right-column')
                    if right_column:
                        tags_container = right_column.find('div', class_='elastic-result-tags-container')
                        if tags_container:
                            tag_spans = tags_container.find_all('span')
                            for tag_span in tag_spans:
                                tag_text = tag_span.get_text(strip=True)
                                # Skip the image span and empty tags
                                if tag_text and not tag_text.startswith('<img'):
                                    # Remove trailing commas
                                    tag_text = tag_text.rstrip(', ')
                                    if tag_text:
                                        tags.append(tag_text)
                    
                    # Extract image if available
                    image_url = None
                    if right_column:
                        image_div = right_column.find('div', class_='elastic-item-image')
                        if image_div:
                            image_url = image_div.get('data-img-src', '')
                            if image_url and not image_url.startswith('http'):
                                image_url = f"https://{INNAGUMA_SITE}.innguma.com/{image_url}"
                    
                    result = {
                        "title": title,
                        "url": href,
                        "type": content_type,
                        "date": date_text,
                        "snippet": snippet[:300] + '...' if len(snippet) > 300 else snippet  # Truncate long snippets
                    }
                    
                    # Add optional fields if present
                    if tags:
                        result["tags"] = tags
                    if image_url:
                        result["image"] = image_url
                    
                    results.append(result)
                
                logger.info(f"Found {len(results)} results for '{query}'")
                
                return {
                    "query": query,
                    "page": page,
                    "order": order,
                    "total_results": len(results),
                    "results": results
                }
    
    except aiohttp.ClientError as e:
        logger.error(f"Network error during search: {str(e)}")
        raise ToolError(f"Network error during search: {str(e)}")
    except Exception as e:
        if isinstance(e, ToolError):
            raise
        logger.error(f"Search failed: {str(e)}")
        raise ToolError(f"Search failed: {str(e)}")


# ============================================================================
# TOTALES ENDPOINTS
# ============================================================================

@mcp.tool(name="get_platform_totals", description="Get total platform statistics including accesses, news, readers, analysts, downloads, uploads and votes.")
async def get_platform_totals(ctx: Context) -> dict:
    """Get platform totals statistics."""
    return await make_request("/totals")


@mcp.tool(name="get_users_totals", description="Get total user statistics including number of users, users without access, users with/without votes, and downloads.")
async def get_users_totals(ctx: Context) -> dict:
    """Get users totals statistics."""
    return await make_request("/totals/users")


@mcp.tool(name="get_user_totals", description="Get total statistics for a specific user by user ID.")
async def get_user_totals(user_id: int, ctx: Context) -> dict:
    """Get specific user totals statistics."""
    return await make_request(f"/totals/users/{user_id}")


@mcp.tool(name="get_news_totals", description="Get total news statistics including published, voted, visited, and with attachments.")
async def get_news_totals(ctx: Context) -> dict:
    """Get news totals statistics."""
    return await make_request("/totals/news")


@mcp.tool(name="get_categories_totals", description="Get total categories statistics including total categories, items, and subscribers.")
async def get_categories_totals(ctx: Context) -> dict:
    """Get categories totals statistics."""
    return await make_request("/totals/categories")


@mcp.tool(name="get_most_searched_words", description="Get the most searched words within a date range. Dates must be in YYYY-MM-DD format.")
async def get_most_searched_words(from_date: str, to_date: str, ctx: Context) -> dict:
    """Get most searched words in a date range."""
    params = {"from": from_date, "to": to_date}
    return await make_request("/totals/words", params)


# ============================================================================
# LECTORES (READERS) ENDPOINTS
# ============================================================================

@mcp.tool(name="list_readers", description="Get a list of all registered readers on the platform.")
async def list_readers(ctx: Context) -> list:
    """Get list of readers."""
    return await make_request("/readers")


@mcp.tool(name="get_readers_overview", description="Get a complete overview of all readers including access data and activity information.")
async def get_readers_overview(ctx: Context) -> list:
    """Get overview of all readers."""
    return await make_request("/readers/overview")


@mcp.tool(name="get_reader_overview", description="Get detailed information for a specific reader by reader ID.")
async def get_reader_overview(reader_id: int, ctx: Context) -> dict:
    """Get specific reader overview."""
    return await make_request(f"/readers/{reader_id}/overview")


@mcp.tool(name="get_reader_viewed_news", description="Get a list of news articles that a specific reader has viewed.")
async def get_reader_viewed_news(reader_id: int, ctx: Context) -> list:
    """Get news items viewed by reader."""
    return await make_request(f"/readers/{reader_id}/items/viewed")


@mcp.tool(name="get_reader_voted_news", description="Get a list of news articles that a specific reader has voted on.")
async def get_reader_voted_news(reader_id: int, ctx: Context) -> list:
    """Get news items voted by reader."""
    return await make_request(f"/readers/{reader_id}/items/voted")


@mcp.tool(name="get_reader_downloads", description="Get a list of files that a specific reader has downloaded.")
async def get_reader_downloads(reader_id: int, ctx: Context) -> list:
    """Get files downloaded by reader."""
    return await make_request(f"/readers/{reader_id}/items/files/downloads")


# ============================================================================
# NOTICIAS (NEWS) ENDPOINTS
# ============================================================================

@mcp.tool(name="list_news_by_date", description="List news published within a date range. Dates must be in YYYY-MM-DD format.")
async def list_news_by_date(from_date: str, to_date: str, ctx: Context) -> list:
    """Get news within a date range."""
    params = {"from": from_date, "to": to_date}
    return await make_request("/news", params)


@mcp.tool(name="get_news_overview", description="Get a complete overview of all news articles.")
async def get_news_overview(ctx: Context) -> list:
    """Get overview of all news."""
    return await make_request("/news/overview")


@mcp.tool(name="get_news_details", description="Get complete details for a specific news article by news ID.")
async def get_news_details(news_id: int, ctx: Context) -> dict:
    """Get specific news overview."""
    return await make_request(f"/news/{news_id}/overview")


@mcp.tool(name="get_news_votes", description="Get a list of users who have voted on a specific news article.")
async def get_news_votes(news_id: int, ctx: Context) -> list:
    """Get votes for a news article."""
    return await make_request(f"/news/{news_id}/votes")


@mcp.tool(name="get_news_visits", description="Get a list of users who have visited a specific news article.")
async def get_news_visits(news_id: int, ctx: Context) -> list:
    """Get visits for a news article."""
    return await make_request(f"/news/{news_id}/visits")


# ============================================================================
# CATEGORIAS (CATEGORIES) ENDPOINTS
# ============================================================================

@mcp.tool(name="list_categories", description="Get a list of all available categories.")
async def list_categories(ctx: Context) -> list:
    """Get list of categories."""
    return await make_request("/categories")


@mcp.tool(name="get_categories_overview", description="Get a complete overview of all categories including items and subscribers.")
async def get_categories_overview(ctx: Context) -> list:
    """Get overview of all categories."""
    return await make_request("/categories/overview")


@mcp.tool(name="get_category_details", description="Get detailed information for a specific category by category ID.")
async def get_category_details(category_id: int, ctx: Context) -> dict:
    """Get specific category overview."""
    return await make_request(f"/categories/{category_id}/overview")


@mcp.tool(name="get_category_subscriptions", description="Get a list of users subscribed to a specific category.")
async def get_category_subscriptions(category_id: int, ctx: Context) -> list:
    """Get subscriptions for a category."""
    return await make_request(f"/categories/{category_id}/subscriptions")


# ============================================================================
# ANALISTAS (ANALYSTS) ENDPOINTS
# ============================================================================

@mcp.tool(name="list_analysts", description="Get a list of all registered analysts on the platform.")
async def list_analysts(ctx: Context) -> list:
    """Get list of analysts."""
    return await make_request("/analysts")


@mcp.tool(name="get_analysts_overview", description="Get a complete overview of all analysts including publications and votes received.")
async def get_analysts_overview(ctx: Context) -> list:
    """Get overview of all analysts."""
    return await make_request("/analysts/overview")


@mcp.tool(name="get_analyst_overview", description="Get detailed information for a specific analyst by analyst ID.")
async def get_analyst_overview(analyst_id: int, ctx: Context) -> dict:
    """Get specific analyst overview."""
    return await make_request(f"/analysts/{analyst_id}/overview")


@mcp.tool(name="get_analyst_publications", description="Get a list of news articles published by a specific analyst.")
async def get_analyst_publications(analyst_id: int, ctx: Context) -> list:
    """Get publications by analyst."""
    return await make_request(f"/analysts/{analyst_id}/items/published")


@mcp.tool(name="get_analyst_voted_publications", description="Get a list of news articles published by an analyst that have received votes.")
async def get_analyst_voted_publications(analyst_id: int, ctx: Context) -> list:
    """Get voted publications by analyst."""
    return await make_request(f"/analysts/{analyst_id}/items/published/votes")


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Innaguma MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
