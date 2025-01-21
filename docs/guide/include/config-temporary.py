import earthkit.regrid

print(earthkit.regrid.config.get("url-download-timeout"))

with earthkit.regrid.config.temporary():
    earthkit.regrid.config.set("url-download-timeout", 5)
    print(earthkit.regrid.config.get("url-download-timeout"))

# Temporary config can also be created with arguments:
with earthkit.regrid.config.temporary("url-download-timeout", 11):
    print(earthkit.regrid.config.get("url-download-timeout"))
