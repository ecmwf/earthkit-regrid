import earthkit.regrid

# Access one of the config options
cache_path = earthkit.regrid.config.get("user-cache-directory")
print(cache_path)

# If this is the last line of a Notebook cell, this
# will display a table with all the current configuration
earthkit.regrid.config
