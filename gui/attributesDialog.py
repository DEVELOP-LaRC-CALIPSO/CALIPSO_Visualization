'''
Created on Jun 15, 2015

@author: Grant Mercer

'''

from Tkconstants import TOP, X, BOTH, BOTTOM, END, EXTENDED
from Tkinter import Toplevel, Frame, StringVar, Label, Text, Button, Listbox
from gui import Constants


class AttributesDialog(Toplevel):
    '''
    Dialog window for creating and assigning attributes to objects
    '''
    
    def __init__(self, root, master, event):
        '''
        Initialize root tkinter window and master GUI window
        '''
        Toplevel.__init__(self, root, width=200, height=200)
        self.__master = master
        self.__event = event
        # TODO: read the selected attributes from the database
        self.__selectedAttributes = []
        self.title("Edit Attributes")
        
        # copies TAGS to avoid aliasing
        self.__availableAttributes = Constants.TAGS[:]
        
        self.container = Frame(self)
        self.container.pack(side=TOP, fill=BOTH, expand=True) 
            
        self.createTopFrame()
        self.createBottomFrame()
        
    def createTopFrame(self):
        self.topFrame = Frame(self.container)                       
        self.topFrame.pack(side=TOP, fill=X, expand=False)
        
        attributeString = StringVar()
        attributeString.set("Attributes:")
        attributeLabel = Label(self.topFrame, textvariable=attributeString)
        attributeLabel.grid(row=0, column=0)
        
        selectedString = StringVar()
        selectedString.set("Selected:")
        selectedLabel = Label(self.topFrame, textvariable=selectedString)
        selectedLabel.grid(row=0, column=3)
        
        self.attributeList = Listbox(self.topFrame, width=30, height=30, selectmode=EXTENDED)
        self.attributeList.grid(row=1, column=0)
        for tag in self.__availableAttributes:
            self.attributeList.insert(END, tag)
        
        removeButton = Button(self.topFrame, width=3, height=2, text="<--", command=self.removeAttribute)
        removeButton.grid(row=1, column=1)
        
        moveButton = Button(self.topFrame, width=3, height=2, text="-->", command=self.moveAttribute)
        moveButton.grid(row=1, column=2)
        
        self.selectedList = Listbox(self.topFrame, width=30, height=30, selectmode=EXTENDED)
        self.selectedList.grid(row=1, column=3)
        
    def createBottomFrame(self):
        self.bottomFrame = Frame(self.container)                       
        self.bottomFrame.pack(side=BOTTOM, fill=X, expand=False)
        
        noteString = StringVar()
        noteString.set("Notes:")
        noteLabel = Label(self.bottomFrame, textvariable=noteString)
        noteLabel.grid(row=0, column=0)
        
        self.noteText = Text(self.bottomFrame, width=10, height=10)
        self.noteText.grid(row=1, column=0)
        
        acceptButton = Button(self.bottomFrame, text="Accept", command=self.accept)
        acceptButton.grid(row=2, column=0)
        
        cancelButton = Button(self.bottomFrame, text="Cancel", command=self.cancel)
        cancelButton.grid(row=2, column=1)
        
        closeButton = Button(self.bottomFrame, text="Close", command=self.close)
        closeButton.grid(row=2, column=2)
        
    def moveAttribute(self):
        selection = self.attributeList.curselection()
        if len(selection) == 0:
            return
        print "Moving tag"
        for item in selection:
            string = self.attributeList.get(item)
            self.__selectedAttributes.append(string)
            self.selectedList.insert(END, string)
        self.attributeList.delete(selection[0], selection[-1])
    
    def removeAttribute(self):
        selection = self.selectedList.curselection()
        if len(selection) == 0:
            return
        print "Removing tag"
        for item in selection:
            string = self.selectedList.get(item)
            self.__selectedAttributes.remove(string)
            self.attributeList.insert(END, string)
        self.selectedList.delete(selection[0], selection[-1])
    
    def accept(self):
        pass
    
    def cancel(self):
        pass
    
    def close(self):
        self.destroy()