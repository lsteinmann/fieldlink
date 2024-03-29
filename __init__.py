# -*- coding: utf-8 -*-
"""
/***************************************************************************
 iDAIFieldLink
                                 A QGIS plugin
 This Plugin synchs and displays geodata from idai.field 2 / Field Desktop in QGIS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-01-25
        copyright            : (C) 2024 by Lisa Steinmann
        email                : lisa.steinmann@rub.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load iDAIFieldLink class from file iDAIFieldLink.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .idaifield_link import iDAIFieldLink
    return iDAIFieldLink(iface)
