## -*- mode: conf; -*-

<%text>############################################################</%text>
#
# ${app_title} - terminal installed alongside the server
#
<%text>############################################################</%text>

[wutta.config]
require = %(here)s/wutta.conf

[wuttapos]
store_id = ${store_id}
terminal_id = ${terminal_id}

[wutta_continuum]
enable_versioning = false
