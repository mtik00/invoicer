from flask_cache import Cache

app_cache = Cache(config={'CACHE_TYPE': 'simple'})
