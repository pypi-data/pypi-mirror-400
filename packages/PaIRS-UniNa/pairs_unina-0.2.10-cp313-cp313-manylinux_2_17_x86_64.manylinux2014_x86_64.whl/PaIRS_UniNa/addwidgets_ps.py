from __future__ import annotations
from .PaIRS_pypacks import *
#from ui_Tree_Tab import Ui_TreeTab

QLocale.setDefault(QLocale.Language.English)
curr_locale = QLocale()

InitCheck=True   #False=Collap closed, True=opened
#fonts
font_italic=True
font_weight=QFont.DemiBold
backgroundcolor_none=" background-color: none;"
backgroundcolor_changing=" background-color: rgb(255,230,230);"
backgroundcolor_hover=" background-color: rgba(0, 116, 255, 0.1);"
border_hover = " "  #"border: 1px solid gray; "
color_changing="color: rgb(33,33,255); "+backgroundcolor_changing

#********************************************* Operating Widgets
def setSS(b,style):
    ss=f"{b.metaObject().className()}{'{'+style+'}'}\\nQToolTip{'{'+b.initialStyle+'}'}"
    return ss

class MyTabLabel(QLabel):
    def __init__(self,parent):
        super().__init__(parent)
        #self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.addfuncclick={}

    def mousePressEvent(self, event):
        for f in self.addfuncclick:
             self.addfuncclick[f]()
        return super().mousePressEvent(event)
    
    def setCustomCursor(self):
        if self.addfuncclick:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

#MyQLineEdit=QtWidgets.QLineEdit
class MyQLineEdit(QtWidgets.QLineEdit):
    def __init__(self,parent):
        super().__init__(parent)
        self.addlab=QtWidgets.QLabel()
        self.addwid=[]
        self.initFlag=False
        self.initFlag2=False
        self.styleFlag=False
        self.addfuncin={}
        self.addfuncout={}
        self.addfuncreturn={}
        self.FlagCompleter=False
        self.FunSetCompleterList=lambda: None

    def setup(self):
        if not self.initFlag:
            self.initFlag=True
            self.FlagFocusIn=False
            self.oldFont=None
            self.oldStyle=None
            font_changing = QtGui.QFont(self.font())
            font_changing.setItalic(font_italic)
            font_changing.setWeight(font_weight)
            children=self.parent().children()
            self.bros=children+self.addwid
            for b in self.bros:
                hasStyleFlag=hasattr(b,'styleFlag')
                if hasattr(b,'setStyleSheet'):
                    if hasStyleFlag:
                        if b.styleFlag: continue
                    b.initialStyle=b.styleSheet()+" "+backgroundcolor_none
                    b.setEnabled(False)
                    b.disabledStyle=b.styleSheet()
                    b.setEnabled(True)
                    b.setStyleSheet(setSS(b,b.initialStyle))
                if hasattr(b,'setFont'):
                    b.initialFont=b.font()
                    b.font_changing=font_changing
                if hasStyleFlag: b.styleFlag=True
            self.CElabs=[w for w in self.bros if isinstance(w, ClickableEditLabel)]
            self.CElabs_styles=[w.styleSheet() for w in self.CElabs]

    def setup2(self):
        if not self.initFlag2:
            self.initFlag2=True
            for b in self.bros:
                if hasattr(b,'bros'):
                    for c in b.bros:
                        if c not in self.bros:
                            self.bros.append(c)

    def setCompleterList(self):
        if not self.FlagCompleter:
            self.FunSetCompleterList()
            self.FlagCompleter=True
        self.showCompleter()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event) #to preserve classical behaviour before adding the below
        self.setCompleterList()

    def enterEvent(self, event):
        if not self.hasFocus() and self.isEnabled():
            self.oldFont=self.font()
            self.oldStyle=self.styleSheet()
            self.setFont(self.font_changing)
            self.setStyleSheet(setSS(self,self.initialStyle+" "+backgroundcolor_hover))
            for k,w in enumerate(self.CElabs): 
                self.CElabs_styles[k]=w.styleSheet()
                w.setStyleSheet(w.styleSheet()+" "+f"""
                ClickableEditLabel {{
                    {backgroundcolor_hover};
                }}
                """)
                w.repaint()
        super().enterEvent(event)
            
    def leaveEvent(self, event):
        if not self.hasFocus() and self.oldFont is not None:
            self.setFont(self.oldFont)
            self.setStyleSheet(self.oldStyle)
            for k,w in enumerate(self.CElabs): 
                w.setStyleSheet(self.CElabs_styles[k])
                w.repaint()
            self.oldFont=None
            self.oldStyle=None
        super().leaveEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        for f in self.addfuncin:
            self.addfuncin[f]()
        self.focusInFun()
               
    def setFocus(self):
        super().setFocus()
        self.focusInFun()

    def focusInFun(self):
        self.setStyleFont(color_changing,self.font_changing)

    def setStyleFont(self,color_changing,font):
        for b in self.bros:
            if hasattr(b,'setInitalStyle') and hasattr(b,'FlagFocusIn') and b.FlagFocusIn: 
                b.setInitalStyle()
                break
        if not self.FlagFocusIn:
            self.FlagFocusIn=True
            self.setFont(font)
            for b in self.bros:
                if hasattr(b,'initialStyle'): 
                    b.setStyleSheet(setSS(b,b.initialStyle+" "+color_changing))
                 
    def focusOutEvent(self, event):
        super().focusOutEvent(event) #to preserve classical behaviour before adding the below
        for f in self.addfuncout:
            self.addfuncout[f]()
        self.setInitalStyle()

    def clearFocus(self):
        super().clearFocus()
        self.setInitalStyle()

    def setInitalStyle(self):
        if self.FlagFocusIn:
            self.FlagFocusIn=False
            for b in self.bros:
                if hasattr(b,'default_stylesheet'):
                    b.setStyleSheet(b.default_stylesheet)
                elif hasattr(b,'initialStyle'):
                    b.setStyleSheet(b.initialStyle)
                if  hasattr(b,'initialFont'):
                    b.setFont(b.initialFont)
            for k,w in enumerate(self.CElabs): 
                self.CElabs_styles[k]=w.default_stylesheet
                w.setStyleSheet(self.CElabs_styles[k])
                w.repaint()
            self.oldFont=None
            self.oldStyle=None
            #self.addlab.clear()
            
    def showCompleter(self):
        if self.completer():
            self.completer().complete()

class MyQLineEditNumber(MyQLineEdit):
    def __init__(self,parent):
        super().__init__(parent)       
        self.addfuncreturn={}

    def keyPressEvent(self, event):
        #infoPrint.white(event.key())
        if event.key() in (Qt.Key.Key_Space, #space
            Qt.Key.Key_Comma, #comma 
            Qt.Key.Key_Delete, Qt.Key.Key_Backspace, #del, backspace
            Qt.Key.Key_Left,Qt.Key.Key_Right, #left, right
            Qt.Key.Key_Return, Qt.Key.Key_Enter #return
            ) \
            or (event.key()>=Qt.Key.Key_0 and event.key()<=Qt.Key.Key_9):
            super().keyPressEvent(event)
        if event.key()==16777220:
            for f in self.addfuncreturn:
                self.addfuncreturn[f]()
        
class MyQCombo(QtWidgets.QComboBox):
    def wheelEvent(self, event):
        event.ignore()

#MyQSpin=QtWidgets.QSpinBox
class MyQSpin(QtWidgets.QSpinBox):
    def __init__(self,parent):
        super().__init__(parent)
        self.addwid=[]
        self.initFlag=False
        self.styleFlag=False
        self.addfuncin={} 
        self.addfuncout={} 
        self.addfuncreturn={}
        
        self.setAccelerated(True)
        self.setGroupSeparatorShown(True)       

    def setup(self): 
        if not self.initFlag:
            self.initFlag=True
            self.FlagFocusIn=False
            self.oldFont=None
            self.oldStyle=None
            font_changing = QtGui.QFont(self.font())
            font_changing.setItalic(font_italic)
            font_changing.setWeight(font_weight)
            self.bros=[self]+self.addwid
            for b in self.bros:
                if b.styleFlag: continue
                b.initialStyle=b.styleSheet()+" "+backgroundcolor_none
                b.initialFont=b.font()
                b.font_changing=font_changing
                b.styleFlag=True
            #self.spinFontObj = self.findChildren(QtWidgets.QLineEdit)[0]
            #self.spinFontObj.initialStyle=self.spinFontObj.styleSheet()+" "+backgroundcolor_none
            #self.spinFontObj.font_changing=font_changing
                
    def setFocus(self):
        super().setFocus()
        self.focusInFun()
    
    def focusInEvent(self, event):
        super().focusInEvent(event) #to preserve classical behaviour before adding the below
        for f in self.addfuncin:
            self.addfuncin[f]()
        self.focusInFun()

    def focusInFun(self):
        if not self.FlagFocusIn:
            self.FlagFocusIn=True
            #self.spinFontObj.setStyleSheet(self.spinFontObj.initialStyle+" "+color_changing)
            for b in self.bros:
                b.setStyleSheet(setSS(b,b.initialStyle+" "+color_changing))
                b.setFont(self.font_changing)

    def clearFocus(self):
        super().clearFocus()
        self.setInitalStyle()

    def focusOutEvent(self, event):
        super().focusOutEvent(event) #to preserve classical behaviour before adding the below
        for f in self.addfuncout:
            self.addfuncout[f]()
        self.setInitalStyle()
    
    def setInitalStyle(self):
        if self.FlagFocusIn:
            self.FlagFocusIn=False
            #self.spinFontObj.setStyleSheet(self.spinFontObj.initialStyle)
            for b in self.bros:
                b.setStyleSheet(setSS(b,b.initialStyle))
                b.setFont(self.initialFont)
            self.findChildren(QtWidgets.QLineEdit)[0].setFont(self.initialFont)
            self.oldFont=None
            self.oldStyle=None

    def enterEvent(self, event):
        super().enterEvent(event)
        if not self.hasFocus() and self.isEnabled():
            self.oldFont=self.font()
            self.setFont(self.font_changing)
            b=self #b=self.spinFontObj
            self.oldStyle=b.styleSheet()
            b.setStyleSheet(setSS(b,b.initialStyle+" "+backgroundcolor_hover+" "+border_hover))
            
    def leaveEvent(self, event):
        super().leaveEvent(event)
        if not self.hasFocus() and self.oldFont is not None:
            self.setFont(self.oldFont)
            b=self #b=self.spinFontObj
            b.setStyleSheet(self.oldStyle)
            self.oldFont=None
            self.oldStyle=None

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter) and self.hasFocus():
            for f in self.addfuncreturn:
                self.addfuncreturn[f]()
    
    def wheelEvent(self, event):
        event.ignore()
    
    def textFromValue(self, value):
        return formatNumber(self,value)
    
def formatNumber(self:QWidget,value):
    if Flag_GROUPSEPARATOR:
        text=self.locale().toString(float(value), 'd')
    else:
        text=f"{value:f}"
    return (text).rstrip('0').rstrip(curr_locale.decimalPoint()) 
    #return ('%f' % value).rstrip('0').rstrip('.') 

class MyQSpinXW(MyQSpin):
    def __init__(self,parent):
        super().__init__(parent)
        self.Win=-1

    def focusInEvent(self, event):
        super().focusInEvent(event) #to preserve classical behaviour before adding the below
        if len(self.addwid)>0:
            self.Win=self.addwid[0].value()

class MyToolButton(QtWidgets.QToolButton):
    def __init__(self,parent):
        super().__init__(parent)

class MyQDoubleSpin(QtWidgets.QDoubleSpinBox):
    def __init__(self,parent):
        super().__init__(parent)
        self.addwid=[]
        self.initFlag=False
        self.styleFlag=False
        self.addfuncin={}
        self.addfuncout={}
        self.addfuncreturn={}

        self.setAccelerated(True)
        self.setGroupSeparatorShown(True)

    def setup(self): 
        if not self.initFlag:
            self.initFlag=True
            self.FlagFocusIn=False
            self.oldFont=None
            self.oldStyle=None
            font_changing = QtGui.QFont(self.font())
            font_changing.setItalic(font_italic)
            font_changing.setWeight(font_weight)
            self.bros=[self]+self.addwid
            for b in self.bros:
                if self.styleFlag: continue
                b.initialStyle=b.styleSheet()+" "+backgroundcolor_none
                b.initialFont=b.font()
                b.font_changing=font_changing
                b.styleFlag=True
            #self.spinFontObj = self.findChildren(QtWidgets.QLineEdit)[0]
            #self.spinFontObj.initialStyle=self.spinFontObj.styleSheet()+" "+backgroundcolor_none
            #self.spinFontObj.font_changing=font_changing

    def setFocus(self):
        super().setFocus()
        self.focusInFun()

    def focusInEvent(self, event):
        super().focusInEvent(event) #to preserve classical behaviour before adding the below
        for f in self.addfuncin:
            self.addfuncin[f]()
        self.focusInFun()

    def focusInFun(self):
        if not self.FlagFocusIn:
            self.FlagFocusIn=True
            #self.spinFontObj.setStyleSheet(self.spinFontObj.initialStyle+" "+color_changing)
            for b in self.bros:
                b.setStyleSheet(setSS(b,b.initialStyle+" "+color_changing))
                b.setFont(self.font_changing)

    def clearFocus(self):
        super().clearFocus()
        self.setInitalStyle()

    def focusOutEvent(self, event):
        super().focusOutEvent(event) #to preserve classical behaviour before adding the below
        for f in self.addfuncout:
            self.addfuncout[f]()
        self.setInitalStyle()
    
    def setInitalStyle(self):
        if self.FlagFocusIn:
            self.FlagFocusIn=False
            #self.spinFontObj.setStyleSheet(self.spinFontObj.initialStyle)
            for b in self.bros:
                b.setStyleSheet(setSS(b,b.initialStyle))
                b.setFont(self.initialFont)
            self.findChildren(QtWidgets.QLineEdit)[0].setFont(self.initialFont)
            self.oldFont=None
            self.oldStyle=None
      
    def enterEvent(self, event):
        super().enterEvent(event)
        if not self.hasFocus() and self.isEnabled():
            self.oldFont=self.font()
            self.setFont(self.font_changing)
            b=self #b=self.spinFontObj
            self.oldStyle=b.styleSheet()
            b.setStyleSheet(setSS(b,b.initialStyle+" "+backgroundcolor_hover+" "+border_hover))
            
    def leaveEvent(self, event):
        super().leaveEvent(event)
        if not self.hasFocus() and self.oldFont is not None:
            self.setFont(self.oldFont)
            b=self #b=self.spinFontObj
            b.setStyleSheet(self.oldStyle)
            self.oldFont=None
            self.oldStyle=None

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter) and self.hasFocus():
            for f in self.addfuncreturn:
                self.addfuncreturn[f]()
    
    def wheelEvent(self, event):
        event.ignore()
    
    def textFromValue(self, value):
        if Flag_GROUPSEPARATOR:
            text=self.locale().toString(float(value), 'f', self.decimals())
        else:
            text=f"{value:f}"
        return (text).rstrip('0').rstrip(curr_locale.decimalPoint()) 
        #return ('%f' % value).rstrip('0').rstrip('.') 

class CollapsibleBox(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initFlag=False
        self.FlagPush=False
        self.dpix=5
        self.toolMinimumWidth=400
        self.toolHeight=20
        self.content_area:QGroupBox=None
        self.toggle_button:QPushButton=None
        self.push_button:MyToolButton=None
        
    def setup(self,*args):
        if not self.initFlag:
            if len(args):
                self.ind=args[0]
                self.stretch=args[1]
            else:
                self.ind=-1
                self.stretch=0
            self.initFlag=True

            if self.content_area is None:
                self.content_area=self.findChild(QtWidgets.QGroupBox)
            self.content_area.setStyleSheet("QGroupBox{border: 1px solid gray; border-radius: 6px;}")

            if self.toggle_button is None:
                self.toggle_button=self.findChild(QtWidgets.QToolButton)
                self.toggle_button.setObjectName("CollapsibleBox_toggle")
                self.toggle_button.setChecked(InitCheck)
                self.toggle_button.clicked.connect(self.on_click)    
            self.toggle_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            self.toggle_button.setMinimumWidth(self.toolMinimumWidth)

            if self.push_button is None:
                self.push_button=self.findChild(MyToolButton)

            self.OpenStyle=\
            "QToolButton { border: none; }\n"+\
            "QToolButton::hover{color: rgba(0,0,255,200);}"+\
            "QToolButton::focus{color: rgba(0,0,255,200);}"
            #"QToolButton::hover{border: none; border-radius: 6px; background-color: rgba(0, 0,128,32); }"
            self.ClosedStyle=\
            "QToolButton { border: 1px solid lightgray; border-radius: 6px }\n"+\
            "QToolButton::hover{ border: 1px solid rgba(0,0,255,200); border-radius: 6px; color: rgba(0,0,255,200);}"+\
            "QToolButton::focus{ border: 1px solid rgba(0,0,255,200); border-radius: 6px; color: rgba(0,0,255,200);}" #background-color: rgba(0, 0,128,32); }" 

            self.heightToogle=self.toggle_button.minimumHeight()
            self.heightOpened=self.minimumHeight()
            self.heightArea=self.heightOpened-self.toolHeight
            
            self.on_click()

    #@QtCore.pyqtSlot()
    def on_click(self):
        checked = self.toggle_button.isChecked()
        pri.Coding.yellow(f'>>>>> {self.objectName()} {"opening" if checked else "closing"}')
        if self.objectName()=='CollapBox_ImSet' and checked:
            pass
        if self.FlagPush: 
            self.push_button.show()
        else:
            self.push_button.hide()
        if checked:
            self.content_area.show()
            self.toggle_button.setArrowType(QtCore.Qt.ArrowType.DownArrow)
           
            self.toggle_button.setMinimumHeight(self.heightToogle)
            self.toggle_button.setMaximumHeight(self.heightToogle)
            self.setMinimumHeight(self.heightOpened)
            self.setMaximumHeight(int(self.heightOpened*1.5))
            self.content_area.setMinimumHeight(self.heightArea)
            self.content_area.setMaximumHeight(int(self.heightArea*1.5))

            self.toggle_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Maximum)
            self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

            self.toggle_button.setStyleSheet(self.OpenStyle)
            if self.ind>0:
                self.parent().layout().setStretch(self.ind,self.stretch)
        else:
            self.content_area.hide()
            self.toggle_button.setArrowType(QtCore.Qt.ArrowType.RightArrow)
            
            self.toggle_button.setMinimumHeight(self.heightToogle+self.dpix)
            self.toggle_button.setMaximumHeight(self.heightToogle+self.dpix)
            self.setMinimumHeight(self.heightToogle+self.dpix*2)
            self.setMaximumHeight(self.heightToogle+self.dpix*2)
            self.content_area.setMinimumHeight(0)
            self.content_area.setMaximumHeight(0)

            self.toggle_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
            self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
            self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
            
            self.toggle_button.setStyleSheet(self.ClosedStyle)
            
            if self.ind>0:
                self.parent().layout().setStretch(self.ind,0)
        
        # Forza l'aggiornamento dei layout
        self.updateGeometry()
        self.parentWidget().updateGeometry()
        self.parentWidget().adjustSize()

    def openBox(self):
        self.toggle_button.setChecked(True)
        self.on_click()

    def closeBox(self):
        self.toggle_button.setChecked(False)
        self.on_click()

class myQTreeWidget(QTreeWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.FlagArrowKeysNormal=False
        self.addfuncin={}
        self.addfuncout={}
        self.addfuncreturn={}
        self.addfuncshift_pressed={}
        self.addfuncshift_released={}
        self.addfuncdel_pressed={}
        self.addfuncarrows_pressed={}
        self.addfuncarrows_released={}
        self.addfunckey_pressed={}
        #self.ui:Ui_TreeTab=None
        self.ui=None

    def focusInEvent(self, event):
        super().focusInEvent(event) #to preserve classical behaviour before adding the below
        for f in self.addfuncin:
            self.addfuncin[f]()

    def focusOutEvent(self, event):
        super().focusOutEvent(event) #to preserve classical behaviour before adding the below
        for f in self.addfuncout:
            self.addfuncout[f]()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            super().keyPressEvent(event) 
            for f in self.addfuncshift_pressed:
                self.addfuncshift_pressed[f]()
        elif  event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            super().keyPressEvent(event) 
            for f in self.addfuncdel_pressed:
                self.addfuncdel_pressed[f]()
        elif event.key() == Qt.Key.Key_Up or event.key() == Qt.Key.Key_Down:
            if self.FlagArrowKeysNormal:
                return super().keyPressEvent(event) 
            else:
                Flag=True
                for f in self.addfuncarrows_pressed:
                    Flag=Flag and self.addfuncarrows_pressed[f](event.key())
                #if Flag: super().keyPressEvent(event) 
        else:
            super().keyPressEvent(event) 
            for f in self.addfunckey_pressed:
                self.addfunckey_pressed[f](event.key())

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event) 
        if event.key() == QtCore.Qt.Key_Shift:
            for f in self.addfuncshift_released:
                self.addfuncshift_released[f]()
        elif event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down:
            if self.FlagArrowKeysNormal:
                return super().keyReleaseEvent(event)
            else:
                Flag=True
                for f in self.addfuncarrows_released:
                    Flag=Flag and self.addfuncarrows_released[f](event.key())
                #if Flag: super().keyPressEvent(event)
                
class ToggleSplitterHandle(QtWidgets.QSplitterHandle):
    def mousePressEvent(self, event):
        super().mousePressEvent(event) 
        for f in self.parent().addfuncin:
            self.parent().addfuncin[f]()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event) 
        for f in self.parent().addfuncout:
            self.parent().addfuncout[f]()

class myQSplitter(QSplitter):
    def __init__(self,parent):
        super().__init__(parent)
        self.OpWidth=0
        self.OpMaxWidth=0
        self.addfuncin={}
        self.addfuncout={}
        self.addfuncreturn={}

    def createHandle(self):
        return ToggleSplitterHandle(self.orientation(), self)

class RichTextPushButton(QPushButton):
    margin=0
    spacing=0

    def __init__(self, parent=None, text=None):
        if parent is not None:
            super().__init__(parent)
        else:
            super().__init__()
        
        self.__lyt = QHBoxLayout()
        self.__lyt.setContentsMargins(self.margin, 0, self.margin, 0)
        self.__lyt.setSpacing(self.spacing)
        self.setLayout(self.__lyt)

        self.__icon= QLabel(self)
        self.__icon.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding,
        )
        self.__icon.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        self.__lbl = QLabel(self)
        if text is not None:
            self.__lbl.setText(text)
        else:
            self.__lbl.hide()
        self.__lbl.setAttribute(Qt.WA_TranslucentBackground)
        self.__lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.__lbl.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding,
        )
        self.__lbl.setTextFormat(Qt.RichText)
        self.__lbl.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.__lyt.addWidget(self.__icon)     
        self.__lyt.addWidget(self.__lbl)  
        self.__lyt.setStretch(0,1)
        self.__lyt.setStretch(1,2)

        self.lyt=self.__lyt
        self.lbl=self.__lbl
        self.icnWidget=self.__icon
        self.icn=None
        return

    def setText(self, text):
        if text:
            self.__lbl.show()
            self.__lbl.setText(text)
        else: self.__lbl.hide()
        self.updateGeometry()
        return
    
    def setIcon(self, icon):
        h=int(self.size().height()/2)
        pixmap = icon.pixmap(QSize(h,h))
        self.__icon.setPixmap(pixmap) 
        self.icn=icon
        self.updateGeometry()
        return
    
    def setIconSize(self, size:QSize):
        if self.icn: self.__icon.setPixmap(self.icn.pixmap(size)) 
        self.updateGeometry()
        return

    def sizeHint(self):
        s = QPushButton.sizeHint(self)
        w_lbl = self.__lbl.sizeHint()
        w_icon = self.__icon.sizeHint()
        s.setWidth(w_lbl.width()+w_icon.width()
                   +self.margin*2+self.spacing)
        s.setHeight(w_lbl.height())
        return s

class myQTableWidget(QtWidgets.QTableWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.RowInfo=[]
        self.InfoLabel:QLabel=None
        self.DeleteButton:QPushButton=None
        self.addwid=[]
        self.addfuncreturn={}
        self.addfuncout={}
        #self.itemSelectionChanged.connect(self.resizeInfoLabel)

    def keyPressEvent(self, event):
        #infoPrint.white(event.key())
        super().keyPressEvent(event) 
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter):  #return
            for f in self.addfuncreturn:
                self.addfuncreturn[f]()
    
    def focusInEvent(self, event):
        super().focusInEvent(event) 
        #if self.DeleteButton: #and self.currentItem():
        #    self.DeleteButton.setEnabled(True)

    def focusOutEvent(self, event):
        super().focusOutEvent(event) 
        for f in self.addfuncout:
            self.addfuncout[f]()
        #if self.InfoLabel:
        #    self.InfoLabel.hide()
        #    self.InfoLabel.setText('') 
        #if self.DeleteButton:
        #    self.DeleteButton.setEnabled(False)

    def resizeEvent(self, event):
        super().resizeEvent(event) 
        self.resizeInfoLabel()

    def resizeInfoLabel(self):
        if self.InfoLabel and (True if not self.addwid else not self.addwid[0].hasFocus()):
            item=self.currentItem()
            if item:
                self.InfoLabel.show()
                if self.RowInfo: rowInfo=self.RowInfo[self.currentRow()]
                else: rowInfo=''
                tip=item.toolTip()
                if not "<br>" in tip:
                    fw=lambda t: QtGui.QFontMetrics(self.InfoLabel.font()).size(QtCore.Qt.TextSingleLine,t).width()
                    if fw(tip)>self.InfoLabel.width():
                        k=0
                        while fw(tip[:k])<self.InfoLabel.width():
                            k+=1
                        tip="<br>".join([tip[:k-1], tip[k-1:2*k]])
                if rowInfo: tip="<br>".join([tip,rowInfo])
                self.InfoLabel.setText(tip)
            else:
                self.InfoLabel.hide()
                self.InfoLabel.setText('') 

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
    
class ClickableLabel(QLabel):
    pixmap_size=25
    def __init__(self, *args):
        super().__init__(*args)
        
        self.default_stylesheet = self.styleSheet() 
        self.highlight_stylesheet = "background-color: rgba(0, 116, 255, 0.1); border-radius: 3px;"
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.resetHighlight)
        self.timer.setSingleShot(True)

        self.moviePixmap=None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.toolTip():
            self.highlight()
            self.showMessageBox()
            self.resetHighlight()
            
    def showMessageBox(self):
        if self.moviePixmap: pixmap=self.moviePixmap
        else: pixmap=self.pixmap()
        warningDialog(self.window(),Message=self.toolTip(),pixmap=pixmap,title='Info')

    def highlight(self):
        self.default_stylesheet = self.styleSheet()  # <-- capture current style
        self.setStyleSheet(self.highlight_stylesheet)
        self.repaint()

    def resetHighlight(self):
        self.setStyleSheet(self.default_stylesheet)

    def setToolTip(self,arg__1):
        QLabel.setToolTip(self,arg__1)
        QLabel.setStatusTip(self,arg__1)
        if arg__1:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

class ClickableEditLabel(ClickableLabel):
    def setup(self):
        le = QLineEdit()
        bg = le.palette().color(QPalette.Base)
        bg_rgba = f"rgba({bg.red()}, {bg.green()}, {bg.blue()}, {bg.alpha()})"

        self.default_stylesheet = self.styleSheet() + f"""
        ClickableEditLabel {{
            background-color: {bg_rgba};
        }}
        """
        self.setStyleSheet(self.default_stylesheet)
        le.setParent(None)

class CustomLineEdit(QLineEdit):
    cancelEditing = Signal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.originalText = text

    def focusOutEvent(self, event):
        self.cancelEditing.emit()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelEditing.emit()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelEditing.emit()
        else:
            super().keyReleaseEvent(event)

class ResizingLabel(QLabel):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.complete_text=self.text()
        
    def setText(self,text):
        self.complete_text=text
        self.resizeText(text)
        return 
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.resizeText(self.text())
        return 
    
    def resizeText(self,text):
        text=self.complete_text
        metrics = QFontMetrics(self.font())
        if self.alignment() & Qt.AlignmentFlag.AlignRight:
            FlagRight=True
            textElideMode=Qt.TextElideMode.ElideLeft
        else:
            FlagRight=False
            textElideMode=Qt.TextElideMode.ElideRight
        if "<span" in text:
            match = re.search(r"<span(.*?)</span>", text)
            html_part = "<span"+match.group(1)+"</span>"
            index = match.start(1)-5
            text_without_bullet=text.replace(html_part,'')
            truncated_text=metrics.elidedText(text_without_bullet, textElideMode, self.width()-5)
            if FlagRight:
                index=len(truncated_text)-3*(int('...' in truncated_text))-len(text_without_bullet[index:])
                if index>0:
                    truncated_text=truncated_text[:index]+html_part+truncated_text[index:]
            elif index>len(truncated_text)-3:
                truncated_text=truncated_text[:index]+html_part+truncated_text[index:]
        else:
            truncated_text = metrics.elidedText(text, textElideMode, self.width())
        super().setText(truncated_text)

class EditableLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        self.label = ResizingLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label.mouseDoubleClickEvent = self.enable_editing

        self.edit = CustomLineEdit(self)
        self.edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.edit.hide()
        self.edit.editingFinished.connect(self.disable_editing)
        self.edit.cancelEditing.connect(self.disable_editing)
        self.updateLabel=lambda: None
        self.bullet=''

        self.installEventFilter(self)  # Installare il filtro eventi

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.edit)

    def setText(self,text):
        self.label.setText(text)
        self.edit.setText(text)

    def setFont(self,font:QFont):
        self.label.setFont(font)
        self.edit.setFont(font)

    def enable_editing(self, event):
        self.label.hide()
        self.edit.setGeometry(self.label.geometry())  # Assicurati che l'editor prenda la posizione della label
        self.edit.setText(self.label.text().replace(self.bullet,''))  # Assicurati che il testo corrente venga impostato nell'editor
        self.edit.selectAll()
        self.edit.show()
        self.window().setFocus()
        self.edit.setFocus()

    def disable_editing(self):
        self.edit.hide()
        self.label.setText(self.edit.text())
        self.label.show()
        self.updateLabel()

def setButtonHoverStyle(w:QWidget,FlagBorder=True,borderRadius=6,FlagCls=True):
    if FlagCls:
        cls = w.metaObject().className()
        base = w.styleSheet() or ""
        if cls not in base: base=f"{cls} {{" +f"{base}"+"}"
        if base and not base.endswith("\n"):
            base += "\n"
    else: cls=base=''
    
    """"
    style = (
        f"{cls}:hover {{"
        "background: qlineargradient("
        "x1:0, y1:0, x2:0, y2:1, "
        "stop:0 rgba(0, 116, 255, 0.05), "
        "stop:0.2 rgba(0, 116, 255, 0.15), "
        "stop:0.8 rgba(0, 116, 255, 0.15), "
        "stop:1 rgba(0, 116, 255, 0.05));"
        f"border-radius: {borderRadius}px;"
        f"{'border: 1px solid gray;' if FlagBorder else ''}"
        "padding: 2px 2px;"
        "}"
    )
    """

    style = (
        f"{cls}:hover {{"
        f"border-radius: {borderRadius}px;"
        f"background-color: none;"
        f"{'border: 1px solid gray;' if FlagBorder else ''}"
        "padding: 2px 2px;"
        "}"
    )
    
    w.setStyleSheet(base + style)

def apply_hover_glow_label(
    w: QLabel,
    *,
    color="#0051FF",
    blur=18,
    max_alpha=170,
    duration_ms=160,
):
    if getattr(w, "_hoverGlowInstalled", False):
        w._hoverGlowColor = QColor(color)
        w._hoverGlowBlur = float(blur)
        w._hoverGlowMaxAlpha = int(max_alpha)
        w._hoverGlowDuration = int(duration_ms)
        w._hoverGlowEffect.setBlurRadius(w._hoverGlowBlur)
        return

    w._hoverGlowInstalled = True
    w._hoverGlowColor = QColor(color)
    w._hoverGlowBlur = float(blur)
    w._hoverGlowMaxAlpha = int(max_alpha)
    w._hoverGlowDuration = int(duration_ms)

    eff = QGraphicsDropShadowEffect(w)
    eff.setOffset(0, 0)
    eff.setBlurRadius(w._hoverGlowBlur)

    c = QColor(w._hoverGlowColor)
    c.setAlpha(0)
    eff.setColor(c)

    w.setGraphicsEffect(eff)
    w._hoverGlowEffect = eff

    def _set_alpha(val):
        col = QColor(w._hoverGlowColor)
        col.setAlpha(int(val))
        w._hoverGlowEffect.setColor(col)

    # ✅ Animate a plain value (no Qt property needed)
    w._hoverGlowAnimAlpha = QVariantAnimation(w)
    w._hoverGlowAnimAlpha.setEasingCurve(QEasingCurve.OutCubic)
    w._hoverGlowAnimAlpha.valueChanged.connect(_set_alpha)

    class _GlowFilter(QObject):
        def eventFilter(self, obj, ev):
            if obj is not w:
                return False

            t = ev.type()
            if t in (QEvent.Enter, QEvent.HoverEnter):
                w._hoverGlowAnimAlpha.stop()
                w._hoverGlowAnimAlpha.setDuration(w._hoverGlowDuration)
                w._hoverGlowAnimAlpha.setStartValue(w._hoverGlowEffect.color().alpha())
                w._hoverGlowAnimAlpha.setEndValue(w._hoverGlowMaxAlpha)
                w._hoverGlowAnimAlpha.start()

            elif t in (QEvent.Leave, QEvent.HoverLeave):
                w._hoverGlowAnimAlpha.stop()
                w._hoverGlowAnimAlpha.setDuration(w._hoverGlowDuration)
                w._hoverGlowAnimAlpha.setStartValue(w._hoverGlowEffect.color().alpha())
                w._hoverGlowAnimAlpha.setEndValue(0)
                w._hoverGlowAnimAlpha.start()

            return False

    w._hoverGlowFilter = _GlowFilter(w)
    w.installEventFilter(w._hoverGlowFilter)

    w.setAttribute(Qt.WA_Hover, True)
    w.setMouseTracking(True)

def remove_hover_glow_label(w: QLabel):
    """Removes the hover glow behavior and restores a clean state."""
    if not getattr(w, "_hoverGlowInstalled", False):
        return

    # Stop animation cleanly
    anim = getattr(w, "_hoverGlowAnimAlpha", None)
    if anim is not None:
        anim.stop()

    # Remove event filter
    filt = getattr(w, "_hoverGlowFilter", None)
    if filt is not None:
        try:
            w.removeEventFilter(filt)
        except RuntimeError:
            pass

    # Remove graphics effect
    w.setGraphicsEffect(None)

    # Restore hover-related flags (safe defaults)
    w.setAttribute(Qt.WA_Hover, False)
    w.setMouseTracking(False)

    # Cleanup attributes
    for attr in (
        "_hoverGlowInstalled",
        "_hoverGlowColor",
        "_hoverGlowBlur",
        "_hoverGlowMaxAlpha",
        "_hoverGlowDuration",
        "_hoverGlowEffect",
        "_hoverGlowAnimAlpha",
        "_hoverGlowFilter",
    ):
        if hasattr(w, attr):
            delattr(w, attr)

class SliderHandleCursorFilter(QObject):
    def eventFilter(self, obj, event):
        if isinstance(obj, QSlider) and event.type() == QEvent.MouseMove:

            opt = QStyleOptionSlider()
            obj.initStyleOption(opt)

            handle_rect = obj.style().subControlRect(
                QStyle.CC_Slider,
                opt,
                QStyle.SC_SliderHandle,
                obj
            )

            if handle_rect.contains(event.position().toPoint()):
                obj.setCursor(QCursor(Qt.OpenHandCursor))
            else:
                obj.unsetCursor()

        return False


def changes(self,TabType,filename,title=" Changes"):
    FlagShow=False
    if self.logChanges:
        if self.logChanges.isVisible():
            FlagShow=True
    if FlagShow:
        self.logChanges.hide()
        self.logChanges.show()
    else:
        self.logChanges=TabType(self,True)
        self.logChanges.resize(720,720)
        self.logChanges.show()
        self.logChanges.ui.progress_Proc.hide()
        self.logChanges.ui.button_close_tab.hide()
        icon=QPixmap(''+ icons_path +'news.png')
        self.logChanges.ui.icon.setPixmap(icon)
        apply_hover_glow_label(self.logChanges.ui.icon)
        self.logChanges.setWindowIcon(self.windowIcon())
        self.logChanges.setWindowTitle(title)
        self.logChanges.ui.name_tab.setText(title)
    
        self.logChanges.ui.log.setLineWrapColumnOrWidth(self.logChanges.ui.log.width()-20)
        base="""
            QTextEdit {
                border: 1px solid #2a2a2a;
                border-radius: 6px;

                padding: 2px;

                selection-background-color: #0051FF;
                selection-color: #FFFFFF;
            }
            """
        self.logChanges.ui.log.setStyleSheet(base+"\n"+gPaIRS_QMenu_style)

        def setFontPixelSize(logChanges:type(self.logChanges),fPixSize):
            logfont=self.font()
            logfont.setFamily(fontName)
            logfont.setPixelSize(fPixSize+2)
            logChanges.ui.log.setFont(logfont)
            fPixSize_TabNames=min([fPixSize*2,30])
            lab=logChanges.ui.name_tab
            font=lab.font()
            font.setPixelSize(fPixSize_TabNames)
            lab.setFont(font)
        self.logChanges.setFontPixelSize=lambda fS: setFontPixelSize(self.logChanges,fS)
        self.logChanges.setFontPixelSize(self.TABpar.fontPixelSize)
        def logResizeEvent(logChanges:type(self.logChanges),e):
            super(type(logChanges),logChanges).resizeEvent(e) 
            logChanges.ui.log.setLineWrapColumnOrWidth(logChanges.ui.log.width()-20)
        self.logChanges.ui.log.resizeEvent=lambda e: logResizeEvent(self.logChanges,e)

        self.logChanges.ui.icon.addfuncclick['whatsnew']=self.whatsNew
        self.logChanges.ui.icon.setCustomCursor()

        try:
            file = open(filename, "rb")
            content = file.read().decode("utf-8")
            self.logChanges.ui.log.setText(content)
            file.close()
        except Exception as inst:
            pri.Error.red(f'There was a problem while reading the file {filename}:\n{inst}')
            self.logChanges.ui.log.setText(f'No information about PaIRS-UniNa updates available!\n\nSorry for this, try to reinstall PaIRS-UniNa or alternatively contact the authors at {__mail__}.')
    return

#********************************************* Matplotlib
import io
import matplotlib as mpl
mpl.use('Qt5Agg')
import matplotlib.pyplot as pyplt
import matplotlib.image as mplimage
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure as mplFigure
from mpl_toolkits.axes_grid1 import make_axes_locatable

import matplotlib.style as mplstyle
mplstyle.use('fast')
#mplstyle.use(['dark_background', 'ggplot', 'fast'])
 
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=8, height=8, dpi=100):
        self.inp_width=width
        self.inp_height=height
        self.inp_dpi=dpi
        self.fig = mplFigure(figsize=(width, height), dpi=dpi)
        self.fig2=[]
        self.axes = self.fig.gca() #self.fig.add_subplot(111)
        self.addfuncrelease={}
        mpl.rcParams["font.family"]=fontName
        #mpl.rcParams["font.size"]=12
        color_tuple=(0.95,0.95,0.95,0)
        #clrgb=[int(i*255) for i in color_tuple]
        self.fig.set_facecolor(color_tuple)

        self.copyIcon=QIcon(icons_path+"copy.png")
        self.openNewWindowIcon=QIcon(icons_path+"open_new_window.png")
        self.scaleDownIcon=QIcon(icons_path+"scale_down.png")
        self.scaleUpIcon=QIcon(icons_path+"scale_up.png")
        self.scaleAllIcon=QIcon(icons_path+"scale_all.png")
        self.showAllIcon=QIcon(icons_path+"show_all.png")
        self.alignAllIcon=QIcon(icons_path+"align_all.png")        
        self.closeAllIcon=QIcon(icons_path+"close_all.png")
        self.loadImageIcon=QIcon(icons_path+"open_image.png")
        self.loadResultIcon=QIcon(icons_path+"open_result.png")

        super(MplCanvas, self).__init__(self.fig)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            for f in self.addfuncrelease:
                self.addfuncrelease[f]()

    def copy2clipboard(self):
        with io.BytesIO() as buffer:
            self.fig.savefig(buffer)
            QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))
            self.showTip(self,'Image copied to clipboard!')
    
    def copy2newfig(self,text='Vis'):
        fig2=QMainWindow()
        fig2.setPalette(self.palette())
        fig2.setWindowTitle(text)
        fig2.setStyleSheet("background-color: white;")

        wid=QWidget(fig2)
        fig2.setCentralWidget(wid)
        lay=QVBoxLayout(wid)

        lbl=QLabel(fig2)
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        with io.BytesIO() as buffer:
            self.fig.savefig(buffer)
            pixmap = QPixmap(QImage.fromData(buffer.getvalue()))
        lbl.setPixmap(pixmap)
        lbl.setScaledContents(False)
        lbl2=QLabel(text,fig2)
        lbl2.setWordWrap(True)
        lbl2.setStyleSheet("color: black;")

        lay.setSpacing(0)
        lay.addWidget(lbl)
        lay.addWidget(lbl2)

        self.fig2.append(fig2) 

        def closeFig2(event):
            type(fig2).closeEvent(fig2,event)
            self.fig2.pop(self.fig2.index(fig2))
            return 
        fig2.closeEvent=lambda event: closeFig2(event)


        def fCopy2clipboard():
            QApplication.clipboard().setImage(lbl.pixmap().toImage())
            self.showTip(fig2,'Image copied to clipboard!')
            return
        
        fig2.scaleFactor=1
        def resizeFig2(scale):
            fig2.scaleFactor=fig2.scaleFactor*scale
            fig2.scaleFactor=min([fig2.scaleFactor,1.5])
            fig2.scaleFactor=max([fig2.scaleFactor,0.5])
            fig2.setFixedSize(s0*fig2.scaleFactor)
            lbl.setPixmap(pixmap.scaled(pixmap.size()*fig2.scaleFactor,mode=Qt.TransformationMode.SmoothTransformation))
            return
        fig2.resizeFig2=resizeFig2

        sc0=QGuiApplication.primaryScreen().geometry()         
        def shiftFig2(dir):
            dpix=10
            geo=fig2.geometry()
            if dir=='u':
                geo.setY(max([geo.y()-dpix,sc0.y()]))
            elif dir=='d':
                geo.setY(min([geo.y()+dpix,sc0.y()+sc0.height()-fig2.height()]))
            elif dir=='l':
                geo.setX(max([geo.x()-dpix,sc0.x()]))
            elif dir=='r':
                geo.setX(min([geo.x()+dpix,sc0.x()+sc0.width()-fig2.width()]))
            fig2.setGeometry(geo)
            return

        QS_down=QShortcut(QKeySequence('Down'), fig2)
        QS_down.activated.connect(lambda: shiftFig2('d'))
        QS_up=QShortcut(QKeySequence('Up'), fig2)
        QS_up.activated.connect(lambda: shiftFig2('u'))
        QS_right=QShortcut(QKeySequence('Right'), fig2)
        QS_right.activated.connect(lambda: shiftFig2('r'))
        QS_left=QShortcut(QKeySequence('Left'), fig2)
        QS_left.activated.connect(lambda: shiftFig2('l'))

        QS_copy2clipboard=QShortcut(QKeySequence('Ctrl+C'), fig2)
        QS_copy2clipboard.activated.connect(fCopy2clipboard)

        fScaleDown=lambda: resizeFig2(0.9)
        QS_scaleDown=QShortcut(QKeySequence('Ctrl+Down'), fig2)
        QS_scaleDown.activated.connect(fScaleDown)
        fScaleUp=lambda: resizeFig2(1.1)
        QS_scaleUp=QShortcut(QKeySequence('Ctrl+Up'), fig2)
        QS_scaleUp.activated.connect(fScaleUp)
        fScaleAll=lambda: self.scaleAll(fig2.scaleFactor)
        QS_scaleAll=QShortcut(QKeySequence('Ctrl+Return'), fig2)
        QS_scaleAll.activated.connect(fScaleAll)

        QS_showAll=QShortcut(QKeySequence('Ctrl+S'), fig2)
        QS_showAll.activated.connect(self.showAll)
        QS_alignAll=QShortcut(QKeySequence('Ctrl+A'), fig2)
        QS_alignAll.activated.connect(self.alignAll)
        QS_closeAll=QShortcut(QKeySequence('Ctrl+X'), fig2)
        QS_closeAll.activated.connect(self.closeAll)
        
        fig2.lbl:QLabel=lbl
        def contextMenuEventFig2(event):
            contextMenu = QMenu()
            contextMenu.setStyleSheet(self.parent().parent().gui.ui.menu.styleSheet())
            copy2clipboard = contextMenu.addAction("Copy to clipboard ("+QS_copy2clipboard.key().toString(QKeySequence.NativeText)+")")
            contextMenu.addSeparator()
            scaleDown = contextMenu.addAction("Scale down ("+QS_scaleDown.key().toString(QKeySequence.NativeText)+")")
            scaleUp = contextMenu.addAction("Scale up ("+QS_scaleUp.key().toString(QKeySequence.NativeText)+")")
            scaleAll = contextMenu.addAction("Scale all ("+QS_scaleAll.key().toString(QKeySequence.NativeText)+")")
            contextMenu.addSeparator()
            showAll = contextMenu.addAction("Show all ("+QS_showAll.key().toString(QKeySequence.NativeText)+")")
            alignAll = contextMenu.addAction("Align all ("+QS_alignAll.key().toString(QKeySequence.NativeText)+")")
            closeAll = contextMenu.addAction("Close all ("+QS_closeAll.key().toString(QKeySequence.NativeText)+")")
            
            copy2clipboard.setIcon(self.copyIcon)
            scaleDown.setIcon(self.scaleDownIcon)
            scaleUp.setIcon(self.scaleUpIcon)
            scaleAll.setIcon(self.scaleAllIcon)
            showAll.setIcon(self.showAllIcon)
            alignAll.setIcon(self.alignAllIcon)
            closeAll.setIcon(self.closeAllIcon)

            action = contextMenu.exec(fig2.mapToGlobal(event.pos()))

            if action == copy2clipboard:
                fCopy2clipboard()
            elif action == scaleDown:
                fScaleDown()
            elif action == scaleUp:
                fScaleUp()
            elif action == scaleAll:
                self.scaleAll(fig2.scaleFactor)
            elif action == showAll:
                self.showAll()
            elif action == alignAll:
                self.alignAll()
            elif action == closeAll:
                self.closeAll()
            
        
        fig2.contextMenuEvent=lambda event: contextMenuEventFig2(event)

        fig2.show()
        fig2.setFixedSize(fig2.width(), fig2.height())
        s0=fig2.size()

        self.posWindow(len(self.fig2)-1)
        """
        fgeo = fig2.frameGeometry()
        centerPoint = QGuiApplication.primaryScreen().availableGeometry().center()
        fgeo.moveCenter(centerPoint)
        fig2.move(fgeo.topLeft())
        """
    
    def showTip(self,obj,message):
        show_mouse_tooltip(obj,message)

    def posWindow(self,ind):
        w=h=0
        for f in self.fig2:
            f:QMainWindow
            w=max([w,f.frameGeometry().width()])
            h=max([h,f.frameGeometry().height()])
        geoS=QGuiApplication.primaryScreen().availableGeometry()
        ncol=int(geoS.width()/w)
        nrow=int(geoS.height()/h)
        ntot=ncol*nrow
        if ind<0: ind=range(len(self.fig2))
        else: ind=[ind]
        for kk in ind:
            k=kk%ntot
            k=kk
            i=int(k/ncol)
            j=k-i*ncol
            f=self.fig2[kk]
            fg=f.frameGeometry()
            fg.moveTopLeft(QPoint(j*w,i*h))
            f.move(fg.topLeft())

    def scaleAll(self,scale):
        for f in self.fig2:
            f:QMainWindow
            f.scaleFactor=scale
            f.resizeFig2(1.0)

    def showAll(self):
        for f in self.fig2:
            f:QMainWindow
            f.hide()
            f.show()
    
    def closeAll(self):
        for f in range(len(self.fig2)):
            f:QMainWindow
            f=self.fig2[0]
            f.close()
        self.fig2=[]
    
    def alignAll(self):
        self.posWindow(-1)
        self.showAll()


def setAppGuiPalette(self:QWidget,palette:QPalette=None):
    applic:QApplication
    if hasattr(self,'app'): 
        applic=self.app
    else: 
        return
    if palette==None: 
        palette=applic.style().standardPalette()
    else:
        applic.setPalette(palette)

    try:
        if self.focusWidget():
            self.focusWidget().clearFocus()
        widgets=[self]
        if hasattr(self,'FloatingTabs'):    widgets+=self.FloatingTabs
        if hasattr(self,'FloatingWindows'): widgets+=self.FloatingWindows
        if hasattr(self,'aboutDialog'):     widgets.append(self.aboutDialog)
        if hasattr(self,'logChanges'):      widgets.append(self.logChanges)
        widgets+=self.findChildren(QDialog)
        for f in  widgets:
            if f and isinstance(f, QWidget):
                f.setPalette(palette)
                for c in f.findChildren(QObject):
                    if hasattr(c,'setPalette') and not isinstance(c, (MplCanvas, mplFigure, QStatusBar)):
                        c.setPalette(palette)
                    if hasattr(c,'initialStyle') and hasattr(c, 'setStyleSheet'):
                        c.setStyleSheet(c.initialStyle)
                for c in f.findChildren(MyQLineEdit):
                    c.initFlag=False
                    c.styleFlag=False
                    c.setup()
                for c in f.findChildren(ClickableEditLabel):
                    c.setup()
                for c in f.findChildren(QObject):
                    if hasattr(c,'setup2'):
                        c.initFlag2=False
                        c.setup2()
        if hasattr(self,'ResizePopup'): 
            if self.ResizePopup is not None:
                self.ResizePopup=type(self.ResizePopup)(self.buttonSizeCallbacks) #non riesco a farlo come gli altri
        if hasattr(self,'w_Vis'): self.w_Vis.addPlotToolBar()
    except:
        pri.Error.red("***** Error while setting the application palette! *****")


class Toast(QFrame):
    """
    Tooltip-like custom toast that appears at the current mouse cursor position.
    Non-native, does not steal focus. Auto-hides after timeout_ms.
    """

    def __init__(
        self,
        parent: QWidget,
        msg: str,
        *,
        timeout_ms: int = 2500,
        offset: QPoint = QPoint(10, 15),   # offset from cursor
        min_width: int = 0,
        max_width: int = 460,
        fade_in_ms: int = 80,
        fade_out_ms: int = 130,
    ):
        super().__init__(parent)

        self.setObjectName("PaIRSToast")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        self._label = QLabel(msg, self)
        self._label.setObjectName("PaIRSToastLabel")
        self._label.setWordWrap(True)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(4,3,4,3)
        lay.addWidget(self._label)

        # Classic tooltip-like styling
        self.setStyleSheet("""
        QFrame#PaIRSToast {
            background-color: #ffffdc;            /* classic tooltip-ish */
            color: #000000;
            border: 1px solid rgba(0, 0, 0, 0.45);
            border-radius: 4px;
        }
        QLabel#PaIRSToastLabel {
            color: #000000;
        }
        """)

        # Width clamp + nice wrapping
        # Reset any previous constraints (important if a previous tooltip was wider)
        self.setMinimumSize(min_width, 0)
        self.setMaximumSize(max_width, 16777215)

        self._label.setMinimumSize(min_width, 0)
        self._label.setMaximumSize(max_width, 16777215)

        # Make sure the label doesn't "expand"
        self._label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        font=self.window().font()
        self._label.setFont(font)
        self._apply_size(msg)

        # Position at cursor (global)
        self._move_to_cursor(offset)

        # Opacity animation
        self.setWindowOpacity(0.0)
        self._anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        # Auto hide
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(lambda: self.fade_out(duration_ms=fade_out_ms))

        self.show()
        self.raise_()
        self.fade_in(duration_ms=fade_in_ms)
        self._timer.start(timeout_ms)

    def _apply_size(self, msg: str):
        self._label.setText(msg)

        # Let QLabel compute the correct wrapped size
        self._label.adjustSize()
        sh = self._label.sizeHint()

        # Lock label to its real hint size
        self._label.setFixedSize(sh)

        # Now shrink the frame to content + margins
        self.adjustSize()

        # Lock the whole toaster too (prevents extra blank area)
        self.setFixedSize(self.sizeHint())

    def _move_to_cursor(self, offset: QPoint):
        parent = self.parent()
        if hasattr(parent, "cursorRect"):
            rect = parent.cursorRect()                 # QRect in coordinate del widget
            p = parent.mapToGlobal(rect.bottomRight())
        else:
            p = QCursor.pos() + offset
                
        # Keep inside the current screen geometry
        screen = self.screen()
        if screen is None:
            self.move(p)
            return

        geo = screen.availableGeometry()
        self.adjustSize()
        w, h = self.width(), self.height()

        x = p.x()
        y = p.y()

        if x + w > geo.right():
            x = geo.right() - w
        if y + h > geo.bottom():
            y = geo.bottom() - h
        if x < geo.left():
            x = geo.left()
        if y < geo.top():
            y = geo.top()

        self.move(QPoint(x, y))

    def fade_in(self, *, duration_ms: int = 80):
        self._anim.stop()
        self._anim.setDuration(duration_ms)
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(1.0)
        self._anim.start()

    def fade_out(self, *, duration_ms: int = 130):
        self._anim.stop()
        self._anim.setDuration(duration_ms)
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(0.0)
        self._anim.finished.connect(self.close)
        self._anim.start()

def show_mouse_tooltip(parent: QWidget, msg: str, *, timeout_ms: int = 2500):
    """
    Convenience function: show a tooltip-like toaster at the mouse cursor.
    Keeps a reference on parent to avoid garbage collection.
    """
    old = getattr(parent, "_pairs_mouse_toaster", None)
    if old is not None and old.isVisible():
        old.close()

    if msg:
        t = Toast(parent, msg, timeout_ms=timeout_ms)
    else: t=None
    parent._pairs_mouse_toaster = t
    return t
   