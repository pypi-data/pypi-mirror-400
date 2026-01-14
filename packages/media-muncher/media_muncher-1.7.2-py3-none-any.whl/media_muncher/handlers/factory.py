import importlib
import pkgutil

import requests
from loguru import logger

from media_muncher.exceptions import MediaHandlerError
from media_muncher.format import MediaFormat

from .generic import ContentHandler, ContentHandlerMeta

USER_AGENT_FOR_HANDLERS = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"

# Timeout for HEAD
TIMEOUT = 2


def _import_all_handlers():
    """
    Dynamically imports all submodules in the handlers package to ensure that all handler classes are registered.
    """
    import media_muncher.handlers  # Adjust the import path based on your project structure

    handlers_package = media_muncher.handlers

    for _, module_name, is_pkg in pkgutil.iter_modules(handlers_package.__path__):
        if not is_pkg:
            importlib.import_module(f"{handlers_package.__name__}.{module_name}")
            logger.debug(f"Imported handler module: {module_name}")


# Registry for subclasses
_direct_registry = {}


def _populate_registry():
    # Rebuild each time so lazy-imported handlers are included.
    global _direct_registry
    _direct_registry = {}

    # Populate registry for supported handlers
    for handler_cls in ContentHandlerMeta.registry:
        if hasattr(handler_cls, "media_format"):
            _direct_registry[handler_cls.media_format] = handler_cls
        if hasattr(handler_cls, "content_types"):
            for content_type in handler_cls.content_types:
                _direct_registry[content_type] = handler_cls
        if hasattr(handler_cls, "file_extensions"):
            for extension in handler_cls.file_extensions:
                _direct_registry[extension] = handler_cls


def _ensure_handler_modules_for_hints(
    content_type: str | None, media_format: MediaFormat | None
):
    """
    Import the minimal handler modules needed for the given hints (content-type / format).
    This avoids importing *all* handlers (and their heavy deps) for common cases.
    """
    modules: set[str] = set()
    if media_format == MediaFormat.HLS:
        modules.add("media_muncher.handlers.hls")
    elif media_format == MediaFormat.DASH:
        modules.add("media_muncher.handlers.dash")
    elif media_format == MediaFormat.JPEG:
        modules.add("media_muncher.handlers.jpeg")
    elif media_format == MediaFormat.PNG:
        modules.add("media_muncher.handlers.png")
    elif media_format == MediaFormat.MP4:
        modules.add("media_muncher.handlers.mp4")

    if content_type:
        ct = content_type.split(";", 1)[0].strip().lower()
        if ct in ("application/x-mpegurl", "application/vnd.apple.mpegurl"):
            modules.add("media_muncher.handlers.hls")
        if ct in ("application/dash+xml",):
            modules.add("media_muncher.handlers.dash")
        if ct in ("image/jpeg",):
            modules.add("media_muncher.handlers.jpeg")
        if ct in ("image/png",):
            modules.add("media_muncher.handlers.png")
        if ct in ("video/mp4",):
            modules.add("media_muncher.handlers.mp4")
        if ct.endswith("xml"):
            # XML-ish: VAST/VMAP are XML-based, but require lxml; only load base XML handler.
            modules.add("media_muncher.handlers.xml")

    for m in modules:
        try:
            importlib.import_module(m)
        except Exception as e:
            logger.debug(f"Failed to import handler module {m}: {e}")


def create_handler(
    url,
    get_full_content=False,
    from_url_only=False,
    user_agent=None,
    explicit_headers=[],
    content_type=None,
    content=None,
):
    url = str(url).strip()
    headers = {"User-Agent": user_agent or USER_AGENT_FOR_HANDLERS}

    if explicit_headers:
        for additional_header in explicit_headers:
            try:
                key, value = additional_header.split("=", 1)
            except ValueError:
                key, value = additional_header.split(":", 1)
            headers[key] = value.strip()

    try:
        # Extract content-type if not provided
        if content_type is None:
            content_type = ""
            if not from_url_only:
                try:
                    response = requests.head(
                        url,
                        allow_redirects=True,
                        headers=headers,
                        timeout=TIMEOUT,
                        verify=ContentHandler.verify_ssl,
                    )
                    content_type = response.headers.get("content-type", "")
                except requests.exceptions.Timeout:
                    logger.debug(
                        f"HTTP HEAD takes more than {TIMEOUT} seconds, skipping."
                    )
                    content_type = "Unknown"

        # Extract extension
        media_format = MediaFormat.guess_from_url(url)

        # Import the minimal set of handler modules for these hints, then build registry.
        _ensure_handler_modules_for_hints(content_type, media_format)
        _populate_registry()

        # Determine appropriate handler from content-type or media-format
        handler_cls = _direct_registry.get(content_type) or _direct_registry.get(
            media_format
        )

        # Otherwise, fallback to content analysis
        if handler_cls is None:
            if content is None:
                if from_url_only:
                    raise ValueError(
                        "No information available in the URL to determine content type: "
                        f"{content_type} / {media_format}"
                    )

                content = ContentHandler.fetch_content_with_size_limit(
                    url=url,
                    size_limit=200 * 1024,
                    headers=headers,
                    enforce_limit=(not get_full_content),
                    timeout=TIMEOUT,
                )

            # Fallback: analyze content if handler is not found by content-type
            # or file extension
            candidate_handlers = []
            if content:
                # As a last resort, import all handlers to allow content sniffing.
                _import_all_handlers()
                _populate_registry()
                for handler in ContentHandlerMeta.registry:
                    if handler.is_supported_content(content):
                        candidate_handlers.append(handler)

            # Choose the most specific one (based on inheritance)
            if candidate_handlers:
                handler_cls = max(
                    candidate_handlers, key=lambda x: x.__mro__.index(ContentHandler)
                )

        if handler_cls is None:
            raise ValueError(
                "Could not determine content type from content-type, file extension, or content of URL: "
                f"- TYPE: {content_type} \n- FORMAT: {media_format} \n- CONTENT: {content}"
            )

        return handler_cls(url, content, headers=headers)

    except Exception as e:
        raise MediaHandlerError(
            message=f"Unable to determine a usable handler for url {url}",
            original_message=(
                e.args[0] if len(e.args) else getattr(e, "description", None)
            ),
        )
