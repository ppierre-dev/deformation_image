# -------------------------------------------------------------------------------------
# projet IUT 1 info, Calais, 2021
# -------------------------------------------------------------------------------------
# author: Rémi Cozot (remi.cozot@univ-littoral.fr)
# date: 2021/03/24
# -------------------------------------------------------------------------------------

import skimage.io, sys, copy, math, time
import numpy as np
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QWidget, QHBoxLayout,  QAction, QFileDialog, QSizePolicy, QPushButton
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QRect

# -------------------------------------------------------------------------------------
class WarperController():
    """ Warper Controller class controls interactive definition of  translation vector"""
    # constructor
    def __init__(self, parent=None):
        """
            params:
                parent (imageWidget) - optionnal
        """
        # attributes
        self.parent = parent        # imageWidget
        self.translation = [0,0]    # translation vector

        # start and end point of translation vector
        self.x0 = 0
        self.y0 = 0
        # end point
        self.x1 = 0
        self.y1 = 0
        # flag: true if mouse button is pressed 
        self.flag = False

    # methods
    def setStartPoint(self, event):
        """
            this methods is called when user clicks on mouse button
            params:
                event (mouse event)
        """
        self.flag = True     
        # get mouse coordinate
        self.x0 = event.x()
        self.y0 = event.y()

    def movePoint(self,event):
        """
            this methods is called when user moves  mouse 
            params:
                event (mouse event)
        """
        if self.flag:
            # get mouse coordinate
            self.x1 = event.x()
            self.y1 = event.y()
            self.translation = [self.x1-self.x0, self.y1-self.y0]   # set translation vector
            # call of warp method of parent attribute
            #if self.parent: self.parent.warp(self.translation)           # comment this line if your computer is low

    def setStopPoint(self, event):
        """
            this methods is called when user releases  mouse 
            params:
                event (mouse event)
        """
        self.flag = False
        # call of warp method of parent attribute
        if self.parent: self.parent.warp(self.translation) #uncomment this line of your computer is low

    def draw(self, painter):
        # recover imageWidget size
        sizeLabel = self.parent.size()
        sizePixMap = self.parent.pixmap().size()
        labelWidth = int(sizeLabel.width())
        centerX = int(sizeLabel.width()/2)+self.translation[0]
        centerY = int(sizeLabel.height()/2)+self.translation[1]

        painter.setPen(QPen(Qt.green,2,Qt.SolidLine))
        painter.drawLine(0,int(sizeLabel.height()/2),centerX,centerY)
        painter.drawLine(centerX,centerY, sizeLabel.width(),int(sizeLabel.height()/2))
        
        painter.drawLine(labelWidth/2, (sizePixMap.height()+sizeLabel.height())//2, centerX,centerY)
        painter.drawLine(centerX,centerY, labelWidth/2, (sizeLabel.height()-sizePixMap.height())//2)
# -------------------------------------------------------------------------------------
class CenteredWarperForward():
    """ functor class for forward warp computation """
    # constructor
    def __init__(): pass

    # method (class method)
    def compute(inputColorData, centerTranslation):
        """ 
            compute forward warp on inputColorData according to centerTranslation
            parameters:
                inputColorData (np.ndarray): array of pixels        - required
                centerTranslation (np.ndarray): translation vector  - requiered
        """

        # image size
        height, width, _ = inputColorData.shape
        # output image
        outputColorData = np.ones(inputColorData.shape)*255
        # set to zeros GB channels: image background is set to red to see holes
        outputColorData[:,:,1] = 0
        outputColorData[:,:,2] = 0

        # holes
        holes = np.zeros((height, width))

        # for all pixel
        for i in range(width):
            for j in range(height):
                # find quadrangle
                # Haut gauche
                if (i <= width/2) and (j <= height/2):
                    # first quad: compute local coordinate
                    u  = i/width*2
                    v  = j/height*2
                    # compute quad vertices
                    ox, oy = 0, 0
                    ax, ay = 0, height/2
                    bx, by = width/2+centerTranslation[0], height/2+centerTranslation[1]
                    cx, cy = width/2, 0

                    # bilinear interpolation
                    ix, iy= ox+u*(cx-ox), oy+u*(cy-oy)
                    jx, jy= ax+u*(bx-ax), ay+u*(by-ay)
                    kx, ky = ix+v*(jx-ix), iy + v*(jy-iy)

                    # set pixel in output image
                    jj = min(max(0,int(ky)),height-1)
                    ii = min(max(0,int(kx)), width-1)
                    outputColorData[jj,ii,:] = inputColorData[j,i,:]
                    
                # Haut droite
                if (i >= width/2) and (j <= height/2):
                    # first quad: compute local coordinate
                    u  = (i-width/2)/width*2
                    v  = j/height*2
                    # compute quad vertices
                    ox, oy = width/2, 0
                    ax, ay = width/2+centerTranslation[0], height/2 +centerTranslation[1]
                    bx, by = width,height/2
                    cx, cy = width, 0

                    # bilinear interpolation
                    ix, iy= ox+u*(cx-ox), oy+u*(cy-oy)
                    jx, jy= ax+u*(bx-ax), ay+u*(by-ay)
                    kx, ky =ix+v*(jx-ix), iy + v*(jy-iy)
                                                                
                    # set pixel in output image
                    jj = min(max(0,int(ky)),height-1)
                    ii = min(max(0,int(kx)), width-1)
                    outputColorData[jj,ii,:] = inputColorData[j,i,:]
                    
                #Bas Gauche
                if (i <= width/2) and (j >= height/2):
                    # first quad: compute local coordinate
                    u  = i/width*2
                    v  = (j-height/2)/height*2
                    # compute quad vertices
                    ox, oy = 0, height/2
                    ax, ay = 0, height
                    bx, by = width/2, height
                    cx, cy = width/2+centerTranslation[0], height/2+centerTranslation[1]

                    # bilinear interpolation
                    ix, iy= ox+u*(cx-ox), oy+u*(cy-oy)
                    jx, jy= ax+u*(bx-ax), ay+u*(by-ay)
                    kx, ky =ix+v*(jx-ix), iy + v*(jy-iy)

                    # set pixel in output image
                    jj = min(max(0,int(ky)),height-1)
                    ii = min(max(0,int(kx)), width-1)
                    outputColorData[jj,ii,:] = inputColorData[j,i,:]
                    
                #Bas Droite
                if (i >= width/2) and (j >= height/2):
                    # first quad: compute local coordinate
                    u  = (i-width/2)/width*2
                    v  = (j-height/2)/height*2
                    # compute quad vertices
                    ox, oy = width/2+centerTranslation[0], height/2+centerTranslation[1]
                    ax, ay = width/2, height
                    bx, by = width, height
                    cx, cy = width, height/2

                    # bilinear interpolation
                    ix, iy= ox+u*(cx-ox), oy+u*(cy-oy)
                    jx, jy= ax+u*(bx-ax), ay+u*(by-ay)
                    kx, ky = ix+v*(jx-ix), iy + v*(jy-iy)

                    # set pixel in output image
                    jj = min(max(0,int(ky)),height-1)
                    ii = min(max(0,int(kx)), width-1)
                    outputColorData[jj,ii,:] = inputColorData[j,i,:]

        #PROBLEME PIXEL ROUGE
        for i in range(width):
            for j in range(height):
                if outputColorData[j,i][0] == 255 and outputColorData[j,i][1] == 0 and outputColorData[j,i][2] == 0 :
                    if holes[j-1,i] == 0:
                        holes[j,i] = 1
                        outputColorData[j,i][0] = outputColorData[j-1,i][0]
                        outputColorData[j,i][1] = outputColorData[j-1,i][1]
                        outputColorData[j,i][2] = outputColorData[j-1,i][2]
                    else: #Au cas ou le pixel précedent était déjà un pixel rouge on remplace par un autre.
                        outputColorData[j,i][0] = outputColorData[j,i-1][0]
                        outputColorData[j,i][1] = outputColorData[j,i-1][1]
                        outputColorData[j,i][2] = outputColorData[j,i-1][2]

        return outputColorData
# -------------------------------------------------------------------------------------
class ImageWidget(QLabel):
    """ ImageWidget class (inherits QLabel) embeds pixel array (colorData attributes), related QPixmap and optionnel warper controller (WarperController class)"""
    # constructor
    def __init__(self, parent=None,imgColorData=None, warperController=None):
        """
            params:
                parent: class that has a warp methods       - optionnal
                imgColorData: pixels array (np.ndarray)     - optionnal
                warperController: (WarperController)        - optionnal
        """
        super().__init__()   # call of super contructor

        # resizable widget
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored )

        # attributes
        self.parent = parent    # QLabel parent (QMainWindow)
        self.colorData = None   # image pixel array
        self.qpixmap = None     # QPixmap pixel array for Qt
        self.warperController = warperController
        
        # set image or default image
        if isinstance(imgColorData, np.ndarray):
            self.setImage(imgColorData)
        else:
            # create a default image: square motif
            colorData = np.ones((200,200,3))*180
            self.setImage(colorData)     # grey default image

    # methods
    def setImage(self, imgColorData):
        """ 
            set image color data (pixel array), create QPixmap and set it to QLabel
            params:
                imgColorData: array of pixel (np.ndarray)
        """
        
        height, width, channel = imgColorData.shape              # recover image size
        self.colorData = imgColorData                                           
        self.qpixmap = QPixmap.fromImage( QImage((imgColorData).astype(np.uint8),  width, height, channel * width, QImage.Format_RGB888)) # create QPixmap
        self.setPixmap(self.qpixmap.scaled(self.size(),Qt.KeepAspectRatio))                # setPixmap to QLabel

    def resize(self): self.setPixmap(self.qpixmap.scaled(self.size(),Qt.KeepAspectRatio))

    def resizeEvent(self,event):
        self.resize()
        super().resizeEvent(event)
    
    def mousePressEvent(self,event):
        if self.warperController: 
            self.warperController.setStartPoint(event)

    def mouseReleaseEvent(self,event):
        if self.warperController: 
            self.warperController.setStopPoint(event)

    def mouseMoveEvent(self,event):
        if self.warperController: 
            self.warperController.movePoint(event)
        self.update()   # call update (to force QLabel widget)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.warperController:
            self.warperController.draw(QPainter(self))

    def warp(self, translation): 
        self.parent.warp(translation)
# -------------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    """ MainWindow class(inherits QMainWindow) main GUI window and has warp method """

    # constructor
    def __init__(self):
        super().__init__() 
        self.setWindowTitle("projet IUT 1 2021")
        self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        # Qt part
        self.centralWidget = QWidget()                  # create simple widget for central widget           
        self.setCentralWidget(self.centralWidget)       # assign this widget to centralWideget
        self.layout  = QHBoxLayout()                    # create a layout manager
        self.centralWidget.setLayout(self.layout)       # assign this manager to central widget  
        self.image = None

        # warp and image widgets
        self.warperController = WarperController()      # warper controller
        self.inputImage = ImageWidget(parent=self,imgColorData=None, warperController=self.warperController) # image widget and associated warper controller
        self.warperController.parent = self.inputImage                                                       # dual link warper also required assosicted image
        self.warpImage = ImageWidget()  # image widget to display wrped image

        # first call of warp for jit init
        self.warp(np.asarray([0,0]))

        label1 = QLabel("Déformation d'une image", self)
        label1.setFont(QFont("Times", 12, QFont.Bold))
        label1.setFixedWidth(self.size().width())
        label1.move(275, 40)

        label2 = QLabel("Auteurs : PREVOST Pierre, DEDRIE Louis, DURIEZ Adrien", self)
        label2.setFont(QFont("Times", 8, QFont.Bold))
        label2.setFixedWidth(self.size().width())
        label2.move(25, 550)

        button = QPushButton('Importer une image', self)
        button.setToolTip('Séléctionner une image')
        button.setFixedWidth(self.size().width()/2)
        button.clicked.connect(self.callBackOpenImage)
        button.clicked.connect(button.deleteLater)
        button.move(250,200)

        self.resize(800,600)    # default size of main window
        self.show()             # force displaying window

    # methods
    def buildFileMenu(self):
        """ create file menu that enable to select input image (jpg only) """
        menubar = self.menuBar()                        # recover menubar 
        fileMenu = menubar.addMenu('&File')             # add file menu
        # OPEN IMAGE
        selectImage = QAction('&Open image', self)      # create item    
        selectImage.setShortcut('Ctrl+O')               # short cut
        selectImage.triggered.connect(self.callBackOpenImage) # define callback method
        fileMenu.addAction(selectImage)                 # add item to menu

    def buildSaveFile(self):
        menubar = self.menuBar()
        saveMenu = menubar.addMenu('&Save')
        #SAVE FILE
        saveImage = QAction("&Save image", self)
        saveImage.setShortcut("Ctrl+S")
        saveImage.triggered.connect(self.callbackSaveImage)
        saveMenu.addAction(saveImage)

    def callBackOpenImage(self):
        """ callback method to open file dialog and select image file """
        fileName, _ = QFileDialog.getOpenFileName(self, "Select image file...", ".", filter="Image Files (*.jpg)") # open file dialog 
        if fileName != "":                              # if file name is not empty
            colorData = skimage.io.imread(fileName)     # read image with skimage.io
            self.inputImage.setImage(colorData)         # set pixel array to input image widget
            self.warp(np.asarray([0,0]))                # call warp (not usefull but cool!)
            self.layout.addWidget(self.inputImage)  # add image widget to layout
            self.layout.addWidget(self.warpImage)   # add image widget to layout
            self.buildFileMenu()
            self.buildSaveFile()

    #ENREGISTRER IMAGE EN CHOISISSANT LA DESTINATION+NOM
    def callbackSaveImage(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save File', ".", filter="Image Files (*.jpg)")
        skimage.io.imsave(""+path+"", self.image)

    def resizeEvent(self, event): super().resizeEvent(event)

    def warp(self, translation):

        start = time.time()
        outputColorData = CenteredWarperForward.compute(self.inputImage.colorData, np.asarray(translation))
        end = time.time()
        # print("Elapsed time(warping) = %s" % (end - start))
        self.warpImage.setImage(outputColorData)
        self.image = outputColorData

# -------------------------------------------------------------------------------------
# main
# -------------------------------------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)    # create QT application
    mw = MainWindow()               # create MainWindow: our application
    sys.exit(app.exec_())           # run app (includes run our application)
# -------------------------------------------------------------------------------------


