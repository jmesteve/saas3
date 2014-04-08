# Añadir al final de /etc/sudoers:  openerp ALL = NOPASSWD : /usr/bin/service apache2 *
# Modificar permisos de la carpeta de apache sites-available.
# Modificar permisos de la carpeta de apache sites-enabled.
# Modificar permisos de la carpeta de openerp
# Modificar permisos de la carpeta /var/log/

# Ejecutar:

echo "openerp ALL = NOPASSWD : /usr/bin/service apache2 *" >> /etc/sudoers
chown openerp /etc/apache2/sites-available
chgrp openerp /etc/apache2/sites-available
chown openerp /etc/apache2/sites-enabled
chgrp openerp /etc/apache2/sites-enabled
chown openerp /etc/openerp
chgrp openerp /etc/openerp
chown openerp /var/log/
chgrp openerp /var/log/

