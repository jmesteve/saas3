# Añadir al final de /etc/sudoers:  openerp ALL = NOPASSWD : /usr/bin/service apache2 *
# Modificar permisos de la carpeta de apache sites-available.
# Modificar permisos de la carpeta de apache sites-enabled.
# Modificar permisos de la carpeta de openerp
# Modificar permisos de la carpeta /var/log/
# Añadir en apache ports.conf: NameVirtualHost *:443

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

Modificar todo el archivo /etc/apache2/ports.conf con:

# If you just change the port or add more ports here, you will likely also
# have to change the VirtualHost statement in
# /etc/apache2/sites-enabled/000-default
# This is also true if you have upgraded from before 2.2.9-3 (i.e. from
# Debian etch). See /usr/share/doc/apache2.2-common/NEWS.Debian.gz and
# README.Debian.gz

NameVirtualHost *:80
Listen 80

<IfModule mod_ssl.c>
    # If you add NameVirtualHost *:443 here, you will also have to change
    # the VirtualHost statement in /etc/apache2/sites-available/default-ssl
    # to <VirtualHost *:443>
    # Server Name Indication for SSL named virtual hosts is currently not
    # supported by MSIE on Windows XP.
    NameVirtualHost *:443
    Listen 443
</IfModule>

<IfModule mod_gnutls.c>
    Listen 443
</IfModule>