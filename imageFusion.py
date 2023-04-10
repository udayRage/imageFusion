# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ImageFusion
                                 A QGIS plugin
 Predict Images
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-11-28
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Edula Raashika
        email                : edularaashika@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction,QFileDialog
from .histif.src.main_psf import main_psf
from .histif.src import evaluation
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .imageFusion_dialog import ImageFusionDialog
import os.path
import os
import numpy as np
from osgeo import gdal
from geotiff import GeoTiff

class ImageFusion:
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
            'ImageFusion_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Image Fusion')
        self.algoOptions = ['Standard HISTIF','Improved HISTIF']

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('ImageFusion', message)


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

        icon_path = ':/plugins/imageFusion/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Image Fusion'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Image Fusion'),
                action)
            self.iface.removeToolBarIcon(action)

    # Get layer names opened in QGIS
    def getLayerNames(self, comboBox):
        self.layerNames = []
        comboBox.clear()
        for layer in self.iface.mapCanvas().layers():
            self.layerNames.append(layer.name())
        comboBox.addItems(self.layerNames)

    # # open file dialog for image input files
    # def openFileDialog(self,lineEdit):
    #     self.outputFileName = QFileDialog.getOpenFileName(self.dlg,'Select File')
    #     lineEdit.setText(str(self.outputFileName[0]))

    # open file dialog to save output files
    def openSaveFileDialog(self):
        self.outputFileName = QFileDialog.getSaveFileName(self.dlg, 'Save File As')
        self.dlg.save.setText(str(self.outputFileName[0]))
    
    def clicked(self):
        self.outputFileName = QFileDialog.getSaveFileName(self.dlg, 'Save File As')
        self.dlg.lineEdit.setText(str(self.outputFileName[0]))

    def raster2array(self, layerName,metaData=0):
        for layer in self.iface.mapCanvas().layers():
            if layer.name() == layerName:
                # print(layerName)
                self.layer = layer
            if metaData ==1 :
                path = layer.dataProvider().dataSourceUri()
                self.dataset=gdal.Open(path)
                # print(self.dataset)

        self.finalArray = []
        provider = self.layer.dataProvider()
        self.bandCount = self.layer.bandCount()
        self.width = self.layer.width()
        self.height = self.layer.height()
        path = self.layer.dataProvider().dataSourceUri()
        self.dataset = gdal.Open(path)
        # print(path)
        for band in range(1, self.bandCount + 1):
            values = []
            block = provider.block(band, self.layer.extent(), self.layer.width(), self.layer.height())
            for i in range(self.layer.width()):
                for j in range(self.layer.height()):
                    values.append(block.value(i, j))
            # print(band)
            self.finalArray.append(values)
        # print(np.array(self.finalArray).shape)
        return np.reshape(np.round(np.array(self.finalArray), 5).T, (self.height, self.width, self.bandCount))

    def tifConvert(self,result,outputFileName):
        driver = gdal.GetDriverByName('GTiff')
        output_file = driver.Create(outputFileName,result.shape[2], result.shape[1],
                                    result.shape[0],
                                    gdal.GDT_Float32)
        for band_range in range(result.shape[0]):
            output_file.GetRasterBand(band_range + 1).WriteArray(result[band_range,:, :])
        output_file.SetGeoTransform(self.dataset.GetGeoTransform())
        output_file.SetProjection(self.dataset.GetProjection())
        # print('completed')

   
   
    #calling HISTIF program for prediction
    def HISTIF(self):
        version = self.dlg.algoComboBox.currentText()

        old_version = True
        if version == 'Improved HISTIF':
            old_version = False
        coarset0 = self.raster2array(self.dlg.coarset0ComboBox.currentText())
        coarset1 = self.raster2array(self.dlg.coarset1ComboBox.currentText())
        finet0 = self.raster2array(self.dlg.finet0ComboBox.currentText(),metaData=1)
        # print(coarset0.shape,coarset1.shape,finet0.shape)


        outputFile = self.dlg.save.text()
        neighbours = int(self.dlg.neighbours.text())
        params = np.array([[int(self.dlg.FWHM_xStart.text()), int(self.dlg.FWHM_xEnd.text())],[int(self.dlg.FWHM_yStart.text()), int(self.dlg.FWHM_yEnd.text())],[int(self.dlg.shift_xStart.text()), int(self.dlg.shift_xEnd.text())],
                                                                         [int(self.dlg.shift_yStart.text()), int(self.dlg.shift_yEnd.text())],
                                                                         [int(self.dlg.rotationAngleStart.text()), int(self.dlg.rotationAngleEnd.text())]])
        # print(params)
        iterations = int(self.dlg.iterations.text())
        # 
        results = main_psf(coarse_img_t0=coarset0,coarse_img_t1=coarset1,fine_img_t0=finet0,params=params,iter=iterations,neighbors=neighbours)
        # results = np.reshape(results,(results.shape[0],results.shape[1],results.shape[2]))
        
        # print('result',results.shape)
        self.tifConvert(results,outputFile)
        print("HISTIF Completed")
        

        # result = main_psf()
    
    #evaluation of HISTIF prediction 
    def evaluate(self):
        original =  self.raster2array(self.dlg.layerComboBox1.currentText())
        predicted = self.raster2array(self.dlg.layerComboBox2.currentText())
        # print(original.shape,predicted.shape)
        resultDf = evaluation.save_result(original,predicted)
        resultDf.to_csv(self.dlg.lineEdit.text(),sep='\t',index=None)
        print('evaluation done')
    
    # setting recommended values for HISTIF prediction 
    def setRecommendedValues(self):
        status = self.dlg.checkBox.isChecked()
        # print(status)
        if status:
            #set params
            self.dlg.scaleFactor.setText(str(1))
            self.dlg.iterations.setText(str(200))
            self.dlg.neighbours.setText(str(4))
            self.dlg.FWHM_xStart.setText(str(1))
            self.dlg.FWHM_yStart.setText(str(1))
            self.dlg.FWHM_xEnd.setText(str(3))
            self.dlg.FWHM_yEnd.setText(str(3))
            self.dlg.shift_xEnd.setText(str(1))
            self.dlg.shift_yEnd.setText(str(1))
            self.dlg.shift_yStart.setText(str(-1))
            self.dlg.shift_xStart.setText(str(-1))
            self.dlg.rotationAngleStart.setText(str(35))
            self.dlg.rotationAngleEnd.setText(str(65))

        else:
            #set params
            self.dlg.scaleFactor.setText(str(0))
            self.dlg.iterations.setText(str(0))
            self.dlg.neighbours.setText(str(0))
            self.dlg.FWHM_xStart.setText(str(0))
            self.dlg.FWHM_yStart.setText(str(0))
            self.dlg.FWHM_xEnd.setText(str(0))
            self.dlg.FWHM_yEnd.setText(str(0))
            self.dlg.shift_xEnd.setText(str(0))
            self.dlg.shift_yEnd.setText(str(0))
            self.dlg.shift_yStart.setText(str(0))
            self.dlg.shift_xStart.setText(str(0))
            self.dlg.rotationAngleStart.setText(str(0))
            self.dlg.rotationAngleEnd.setText(str(0))


    
    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = ImageFusionDialog()

        # show the dialog
        self.dlg.show()

        #predict

        #adding algorithms to algo combo box
        self.dlg.algoComboBox.clear()
        self.dlg.algoComboBox.addItems(self.algoOptions)

        # set filename
        self.dlg.coarset0Button.clicked.connect(lambda:self.getLayerNames(self.dlg.coarset0ComboBox))
        self.dlg.coarset1Button.clicked.connect(lambda: self.getLayerNames(self.dlg.coarset1ComboBox))
        self.dlg.finet0Button.clicked.connect(lambda: self.getLayerNames(self.dlg.finet0ComboBox))
        self.dlg.saveButton.clicked.connect(self.openSaveFileDialog)

        # get layers into combo box(evaluate)
        # self.dlg.layerButton.clicked.connect(lambda: self.getLayerNames(self.dlg.layerComboBox))
        self.dlg.getLayerButton1.clicked.connect(lambda: self.getLayerNames(self.dlg.layerComboBox1))
        self.dlg.getLayerButton2.clicked.connect(lambda: self.getLayerNames(self.dlg.layerComboBox2))

        
        # submit button(predict)
        self.dlg.predictButton.clicked.connect(self.HISTIF)

        #evaluate button
        self.dlg.evaluateButton.clicked.connect(self.evaluate)

        #save evaluated fiel 
        self.dlg.pushButton.clicked.connect(self.clicked)

        #check box status for setting recommended values
        self.dlg.checkBox.stateChanged.connect(self.setRecommendedValues)

        self.setRecommendedValues()


        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass