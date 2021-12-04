import tkinter as tk
import xml.etree.ElementTree as ET

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(
            fill=tk.Y,
            side=tk.RIGHT, 
            expand=tk.FALSE
            )
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class LabelSource(tk.Label):
    instances=[]
    slaves=[]
    def __init__(self, parent=None, source='None', frame_words_content=None, dic={}, myapp=None, *args, **kw):
        tk.Label.__init__(self, parent, *args, **kw)            
        self.__class__.instances.append(self)
        self.bind('<Button-1>', self.click)
        self.source=source
        self.frame_words_content=frame_words_content
        self.dic=dic
        self.myapp=myapp
        
    def click(self, event):
        self.config(bg='red')
        for other in self.__class__.instances:
            if id(self) != id(other):
                other.config(bg='#f0f0ed')
        
        for sl in self.slaves:
            sl.destroy()
        
        self.__class__.slaves=[]
        for w in self.dic[str(self.source)]:
                news=LabelWord(self.frame_words_content.interior, text=w, myapp=self.myapp, anchor='w')
                news.pack(fill='both')
                self.slaves.append(news)
                
        self.myapp.activesource=self.source
        
        
class LabelWord(tk.Label):
    def __init__(self, parent=None, source='None', frame_words_content=None, dic={}, text='', myapp=None, *args, **kw):
        tk.Label.__init__(self, parent, text=text, *args, **kw)            
        self.bind('<Button-2>', self.rightclick)
        self.bind('<Button-3>', self.rightclick)
        self.source = source
        self.word = text
        self.dic = dic
        self.myapp=myapp
        
    def rightclick(self, event):
        popup = DialogWord(self)
        
class DialogWord:
    exists=0
    def __init__(self, parent=None):
        if self.exists:
            return
        DialogWord.exists = 1
        
        self.parent = parent
        
        self.popup=tk.Toplevel(parent)
        self.popup.overrideredirect(True)
        x, y = parent.winfo_rootx(), parent.winfo_rooty()
        self.popup.geometry("+%d+%d"% (x, y + 20))

        
        button_delete=tk.Button(self.popup, text='Delete')
        button_edit=tk.Button(self.popup, text='Edit')
        button_nothing=tk.Button(self.popup, text='Nothing')
        button_delete.pack(side='right')
        button_edit.pack(side='right')
        button_nothing.pack(side='right')
        
        self.popup.grab_set()                 
        self.popup.bind("<Button-1>", self.clickoutside)
        self.popup.bind("<Button-2>", self.clickoutside)
        self.popup.bind("<Button-3>", self.clickoutside)
        
        button_delete.bind("<Button-1>", self.delete )
        button_nothing.bind("<Button-1>", self.close)
        
    def clickoutside(self, event):
        if event.widget == self.popup:
            if (event.x < 0 or event.x > self.popup.winfo_width() or
                event.y < 0 or event.y > self.popup.winfo_height()):
                self.close()

        
    def delete(self, event=None):
        self.parent.myapp.delword(self.parent.word)
        self.parent.destroy()
        self.close()
        print('deldel')
    def close(self, event=None):
        self.popup.destroy()
        DialogWord.exists=0

class MyApp():
    sources=set()
    dic={}
    sources_graphical=[]
    
    
    def __init__(self):
        window = tk.Tk()
        window.title('Wordlist')
        greeting = tk.Label(text="My dict")
        greeting.pack()

        self.activesource=None

        self.frame_sources=tk.Frame(window)
        self.frame_sources_content=VerticalScrolledFrame(self.frame_sources)
        self.entry_sources = tk.Entry(self.frame_sources, fg="black", bg="white", width=50)
        
        button_sources = tk.Button(self.frame_sources,text="Add source")
        button_sources.bind('<Button-1>', self.addsource)
        self.entry_sources.bind('<Return>', self.addsource)
        self.entry_sources.bind('<Button-2>', lambda x: self.entry_sources.insert(0,window.clipboard_get()) )
        self.entry_sources.bind('<Button-3>', lambda x: self.entry_sources.insert(0,window.clipboard_get()) )

        
        self.frame_words=tk.Frame(window)
        self.frame_words_content=VerticalScrolledFrame(self.frame_words)
        self.entry_words = tk.Entry(self.frame_words, fg="black", bg="white", width=50)
        button_words = tk.Button(self.frame_words, text="Add word")
        button_words.bind('<Button-1>' ,self.addword)
        self.entry_words.bind('<Return>', self.addword)
        self.entry_words.bind('<Button-2>', lambda x: self.entry_words.insert(0,window.clipboard_get()) )
        self.entry_words.bind('<Button-3>', lambda x: self.entry_words.insert(0,window.clipboard_get()) )
        self.loaddata()
        
        #self.scroll_sources.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame_sources.pack(side=tk.LEFT)
        self.frame_sources_content.pack(fill=tk.X)
        self.entry_sources.pack(side=tk.BOTTOM)
        button_sources.pack(side=tk.BOTTOM)
        


        self.frame_words.pack(side=tk.RIGHT,fill=tk.X)
        self.frame_words_content.pack(fill='both')
        
        button_words.pack()
        self.entry_words.pack()
        window.mainloop()
    def loaddata(self):
        tree=ET.parse('dic.xml')
        root=tree.getroot()
        for child in root:
            if child.attrib['data']:
                s=child.attrib['data']
                self.sources.add(s)
                self.addgraphsource(s)
                if not child:
                    self.dic[s]=[' ']
                for gc in child:
                    if s in self.dic.keys():
                        self.dic[s].append(gc.text)
                            
                    else:
                        self.dic[s]=[gc.text]
                        
    def addwordtoxml(self, w):
        tree=ET.parse('dic.xml')
        root=tree.getroot()
        for snode in root.findall('source'):
            if snode.attrib['data'] == self.activesource:
                wordnode=ET.Element('word')
                wordnode.text=w
                snode.append(wordnode)
        tree.write('dic.xml')

    def delwordfromxml(self,s,w):
        tree=ET.parse('dic.xml')
        root=tree.getroot()
        for snode in root.findall('source'):
            if snode.attrib['data'] == self.activesource:
                for wnode in snode:
                    if wnode.text == w:
                        snode.remove(wnode)
                        break #deletes first occurrence of a word
        tree.write('dic.xml')
                
    def addsource(self, event):
        s = self.entry_sources.get()
        if s and s not in self.sources:
            tree=ET.parse('dic.xml')
            root=tree.getroot()
            newnode=ET.Element('source')
            newnode.set('data', s)
            root.append(newnode)
            tree.write('dic.xml')
            self.addgraphsource(s)
            self.sources.add(s)
            self.dic[s]=[' ']
        self.entry_sources.delete(0, tk.END)
            
    def addword(self, event):
        s = self.activesource
        w = self.entry_words.get()
        if s==None or w =='':
            pass
            #tk.messagebox.showinfo('No source or no word', 'Select a source or type in a word')
        else:
            if self.dic[s]==[' ']:
                    self.dic[s]=[w]
                    for sl in LabelSource.slaves:
                        sl.destroy()
            else:
                    self.dic[s]+=[w]
            self.addgraphword(s,w)
            self.addwordtoxml(w)
        self.entry_words.delete(0, tk.END)
    

    def delword(self, w):
        s=self.activesource
        w=w
        if s==None or w=='':
            pass
        else:
            self.dic[s].remove(w)
            self.delwordfromxml(s,w)
            
    def addgraphsource(self,s):
        newst=LabelSource(self.frame_sources_content.interior, text=s[:64], source=s, frame_words_content=self.frame_words_content, dic=self.dic, myapp=self)    
        newst.pack(fill='x', expand=tk.TRUE)
    def addgraphword(self, s, w):
        news=LabelWord(self.frame_words_content.interior, text=w, myapp=self, anchor='w')
        LabelSource.slaves.append(news)
        news.pack(fill='both')

                            
MyApp()