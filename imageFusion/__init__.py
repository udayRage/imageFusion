# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ImageFusion
                                 A QGIS plugin
 Predict Images
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-11-28
        copyright            : (C) 2022 by Edula Raashika
        email                : edularaashika@gmail.com
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
    """Load ImageFusion class from file ImageFusion.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .imageFusion import ImageFusion
    return ImageFusion(iface)
