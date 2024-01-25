# -*- coding: utf-8 -*-
"""
/***************************************************************************
 iDAIFieldLink
                                 A QGIS plugin
 This Plugin synchs and displays geodata from idai.field 2 / Field Desktop in QGIS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-01-25
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Lisa Steinmann
        email                : lisa.steinmann@rub.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, Qgis, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFields
from osgeo import ogr
import couchdb
import json

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .idaifield_link_dialog import iDAIFieldLinkDialog
import os.path


class iDAIFieldLink:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'iDAIFieldLink_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&iDAIFieldLink')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        # maybe this works
        self.fieldConnection = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('iDAIFieldLink', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/idaifield_link/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Link Field Desktop'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&iDAIFieldLink'),
                action)
            self.iface.removeToolBarIcon(action)
    
    def connect_couchdb(self):
        adr = self.dlg.serverAddress.text()
        adr = adr.replace("http://", "")
        adr = adr.replace("https://", "")
        pwd = self.dlg.password.text()
        fieldConnection = couchdb.Server('http://qgis:' + pwd + '@' + adr)
        projects = []
        if "idai-field" in fieldConnection.config()['log']['file']:
            self.fieldConnection = fieldConnection
            for prj in fieldConnection:
                if str(prj) != "_replicator":
                    projects.append(str(prj))
        self.dlg.projectDropdown.clear()
        self.dlg.projectDropdown.addItems(projects)




    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = iDAIFieldLinkDialog()
            self.dlg.connectButton.clicked.connect(self.connect_couchdb)





        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # 
            project = self.dlg.projectDropdown.currentText()
            geomType = self.dlg.geomTypeDropdown.currentText()
            layername = "idai.field_" + project + "_" + geomType

            # assign the geometry to be queried
            if geomType == "Point":
                geomType = ["Point", "MultiPoint"]
            elif geomType == "Polygon":
                geomType = ["Polygon", "MultiPolygon"]
            elif geomType == "LineString":
                geomType = ["LineString", "MultiLineString"]


            # build the query
            qryFields = [
                'resource.id', 
                'resource.identifier', 
                'resource.category', 'resource.type', 
                'resource.relations.isRecordedIn', 
                'resource.relations.liesWithin', 
                'resource.geometry'
            ]
            sel = {'selector': {"resource.geometry.type": {"$in": geomType }}, 'fields': qryFields}
            
            fields = QgsFields()
            fields.append(QgsField("id", QVariant.String, "char", 200))
            fields.append(QgsField("identifier", QVariant.String, "char", 200))
            fields.append(QgsField("category", QVariant.String, "char", 200))
            fields.append(QgsField("relations", QVariant.String, "char", 1000))
            fields.append(QgsField("geomType", QVariant.String, "char", 50))

            features = []
            db = self.fieldConnection[project]
            for item in db.find(sel):
                # only need info inside resource
                resource = item['resource']
                # since we query for geometry, geometry always exists.
                # we make it into a string and weirdly reformat it for qgis
                geom = resource['geometry']
                geom = json.dumps(geom)
                geom = ogr.CreateGeometryFromJson(geom)
                geom = QgsGeometry.fromWkt(geom.ExportToWkt())
                # and we add the fields
                feature = QgsFeature(fields)
                # these entries also always exist, because of reasons
                feature.setAttribute('id', str(resource['id']))
                feature.setAttribute('identifier', str(resource['identifier']))
                feature.setAttribute('geomType', str(resource['geometry']['type']))
                # compensate for entries that may still be 'type' instead of 'category'
                if 'category' in resource:
                    feature.setAttribute('category', str(resource['category']))
                else:
                    feature.setAttribute('category', str(resource['type']))
                # can only add relations if they exist.
                if 'relations' in resource: 
                    feature.setAttribute('relations', json.dumps(resource['relations']))
                feature.setGeometry(geom)
                features.append(feature)
            
            # take second element from geomType as geometrytype, because that will be multi and should
            # make everything work
            uri = geomType[1] + "?crs=epsg:" + self.dlg.epsg.text()
            layer = QgsVectorLayer(uri, layername, 'memory')
            layer.dataProvider().addAttributes(fields)
            layer.updateFields()
            layer.dataProvider().addFeatures(features)
            layer.updateExtents()
            QgsProject.instance().addMapLayers([layer])
