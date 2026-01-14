from enum import StrEnum


class CDPDomain(StrEnum):
    PAGE = "Page"
    DOM = "DOM"
    INPUT = "Input"
    NETWORK = "Network"
    TARGET = "Target"
    RUNTIME = "Runtime"
    CONSOLE = "Console"

    DEBUGGER = "Debugger"
    PROFILER = "Profiler"
    HEAP_PROFILER = "HeapProfiler"
    PERFORMANCE = "Performance"

    CSS = "CSS"
    OVERLAY = "Overlay"
    ANIMATION = "Animation"
    LAYER_TREE = "LayerTree"

    STORAGE = "Storage"
    DATABASE = "Database"
    INDEXED_DB = "IndexedDB"
    CACHE_STORAGE = "CacheStorage"
    DOM_STORAGE = "DOMStorage"
    APPLICATION_CACHE = "ApplicationCache"

    FETCH = "Fetch"
    WEB_AUDIO = "WebAudio"
    WEB_AUTHN = "WebAuthn"
    MEDIA = "Media"
    SERVICE_WORKER = "ServiceWorker"
    BACKGROUND_SERVICE = "BackgroundService"

    EMULATION = "Emulation"
    DEVICE_ORIENTATION = "DeviceOrientation"

    BROWSER = "Browser"
    SYSTEM_INFO = "SystemInfo"
    SECURITY = "Security"
    LOG = "Log"
    TETHERING = "Tethering"

    ACCESSIBILITY = "Accessibility"
    AUDITS = "Audits"

    TRACING = "Tracing"
    SCHEMA = "Schema"
    CAST = "Cast"
    DOM_SNAPSHOT = "DOMSnapshot"
    DOM_DEBUGGER = "DOMDebugger"
    EVENT_BREAKPOINTS = "EventBreakpoints"
    IO = "IO"
    MEMORY = "Memory"


DOMAINS_TO_GENERATE: set[CDPDomain] = {
    CDPDomain.PAGE,
    CDPDomain.DOM,
    CDPDomain.INPUT,
    CDPDomain.NETWORK,
    CDPDomain.TARGET,
    CDPDomain.RUNTIME,
    CDPDomain.CONSOLE,
    CDPDomain.DEBUGGER,
    CDPDomain.PROFILER,
    CDPDomain.HEAP_PROFILER,
    CDPDomain.PERFORMANCE,
    CDPDomain.CSS,
    CDPDomain.OVERLAY,
    CDPDomain.ANIMATION,
    CDPDomain.LAYER_TREE,
    CDPDomain.STORAGE,
    CDPDomain.DATABASE,
    CDPDomain.INDEXED_DB,
    CDPDomain.CACHE_STORAGE,
    CDPDomain.DOM_STORAGE,
    CDPDomain.APPLICATION_CACHE,
    CDPDomain.FETCH,
    CDPDomain.WEB_AUDIO,
    CDPDomain.WEB_AUTHN,
    CDPDomain.MEDIA,
    CDPDomain.SERVICE_WORKER,
    CDPDomain.BACKGROUND_SERVICE,
    CDPDomain.EMULATION,
    CDPDomain.DEVICE_ORIENTATION,
    CDPDomain.BROWSER,
    CDPDomain.SYSTEM_INFO,
    CDPDomain.SECURITY,
    CDPDomain.LOG,
    CDPDomain.TETHERING,
    CDPDomain.ACCESSIBILITY,
    CDPDomain.AUDITS,
    CDPDomain.TRACING,
    CDPDomain.SCHEMA,
    CDPDomain.CAST,
    CDPDomain.DOM_SNAPSHOT,
    CDPDomain.DOM_DEBUGGER,
    CDPDomain.EVENT_BREAKPOINTS,
    CDPDomain.IO,
    CDPDomain.MEMORY,
}
