Version 0.5 Updates
/////////////////////////


Version 0.5.1
===============

Changes
++++++++++++++++

- Use the ``order`` key as the preferred way to specify HEALPix ordering ("ring" or "nested"). The ``ordering``
 key is still accepted for backward compatibility (:pr:`111`).


Version 0.5.0
===============

Changes
++++++++++++++++

- Use new remote download host for matrices (:pr:`110`). Cached matrices (from the previous host) will be downloaded automatically from the new host on next use.
