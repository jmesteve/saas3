# -*- coding: utf-8 -*-
from openerp.addons.point_of_sale.controllers.main import html_template
# he añadido en point_of_sale.controllers.main la linea del css. No hay manera de extenderlo
html_template = """<!DOCTYPE html>
<html>
    <head>
        <title>OpenERP POS</title>

        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
        <meta http-equiv="content-type" content="text/html, charset=utf-8" />

        <meta name="viewport" content=" width=1024, user-scalable=no">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="mobile-web-app-capable" content="yes">

        <link rel="shortcut icon"    sizes="196x196" href="/point_of_sale/static/src/img/touch-icon-196.png">
        <link rel="shortcut icon"    sizes="128x128" href="/point_of_sale/static/src/img/touch-icon-128.png">
        <link rel="apple-touch-icon"                 href="/point_of_sale/static/src/img/touch-icon-iphone.png">
        <link rel="apple-touch-icon" sizes="76x76"   href="/point_of_sale/static/src/img/touch-icon-ipad.png">
        <link rel="apple-touch-icon" sizes="120x120" href="/point_of_sale/static/src/img/touch-icon-iphone-retina.png">
        <link rel="apple-touch-icon" sizes="152x152" href="/point_of_sale/static/src/img/touch-icon-ipad-retina.png">

        <link rel="shortcut icon" href="/web/static/src/img/favicon.ico" type="image/x-icon"/>
        <link rel="stylesheet" href="/point_of_sale/static/src/fonts/lato/stylesheet.css" /> 
        <link rel="stylesheet" href="/point_of_sale/static/src/fonts/font-awesome-4.0.3/css/font-awesome.min.css" /> 
        <link rel="stylesheet" href="/point_of_sale/static/src/css/pos.css" />
        <link rel="stylesheet" href="/point_of_sale_extend/static/src/css/pos.css" />
        <link rel="stylesheet" href="/point_of_sale/static/src/css/keyboard.css" />
        %(js)s
        <script type="text/javascript">
            $(function() {
                var s = new openerp.init(%(modules)s);
                %(init)s
            });
        </script>
    </head>
    <body>
        <!--[if lte IE 8]>
        <script src="//ajax.googleapis.com/ajax/libs/chrome-frame/1/CFInstall.min.js"></script>
        <script>CFInstall.check({mode: "overlay"});</script>
        <![endif]-->
    </body>
</html>
"""
