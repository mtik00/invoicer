from flask_caching import Cache

app_cache = Cache(config={'CACHE_TYPE': 'simple'})
