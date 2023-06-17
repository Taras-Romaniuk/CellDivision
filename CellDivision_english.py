from tkinter import *
from tkinter import ttk
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo
from ttkthemes import ThemedTk  # Window theme
import random
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from belfrywidgets import ToolTip

matplotlib.use("TkAgg")


class Entity(object):

    def __init__(self, x, y, dir1):
        global colors, amount
        global born, step, decsize
        amount += 1
        born += 1
        usedcoords.append(dir1)
        self.cll = len(colors)
        if randomness:
            self.children = random.randint(0, children)
        else:
            self.children = children
        self.chcount, self.age, self.s = 0, 0, 0
        self.chbirth = []
        chl = list(range(activeage, passiveage))
        if passiveage != activeage:
            for i in range(self.children):
                self.chbirth.append(random.choice(chl))
        self.deathprobability = deathprobability
        n = self.deathprobability / 100
        m = random.choices((True, False), [n, 1 - n])[0]
        self.suddendeathage = None if not m else random.randint(0, deathage)
        self.cx, self.cy = x, y
        self.dir1 = dir1
        self.step = step
        self.showcolor = bv5.get()
        self.showgrowing = bv.get()
        self.showungrowing = bv3.get()
        self.k = deathage // self.cll
        if bv3.get():
            self.dsz = deathage - passiveage
        if bv.get():
            ds = (step / activeage) / 2
            self.sz = 0
            self.entity = c.create_oval((x + ds, y + ds), (x - ds, y - ds), fill=colors[0],
                                        outline=colors[0], activewidth=6, activedash=(5, 1))
        else:
            self.entity = c.create_oval((x - step / 2, y - step / 2), (x + step / 2, y + step / 2),
                                        fill=colors[0], outline=colors[0], activewidth=6, activedash=(5, 1))
        c.tag_bind(self.entity, "<Enter>", lambda e: PlaceInfo(e, self.age, self.chcount, self.suddendeathage))
        c.tag_bind(self.entity, "<Leave>", lambda e: UnplaceInfo())


    def RemoveFromCanvas(self):
        if infolabel.winfo_ismapped():
            UnplaceInfo()
        c.delete(self.entity)


    def MyTimeHasCome(self):
        global amount, dead, end
        amount -= 1
        dead += 1
        pb.config(value=amount / allamount * 100)
        usedcoords.remove(self.dir1)
        self.RemoveFromCanvas()
        del entities[entities.index(self)]
        if amount == 0:
            end = True
            End("All entities became extinct!",
                     f"Time: {time}\nThe number of entities born:{born}\nThe number of dead:{dead}")

    def IncreaseAge(self):  # The age increases by one unit
        global end, entities
        self.age += 1
        if self.age == self.suddendeathage or self.age == deathage:  # If sudden death occurs or death occurs
            self.MyTimeHasCome()
        else: # If there was no death
            if self.showcolor: # If parameter CheckBox "Change colour" is clicked
                if self.s != self.cll and self.age == self.k * (self.s + 1):  # Change the colour
                    c.itemconfig(self.entity, fill=colors[self.s], outline=colors[self.s])
                    self.s += 1
            if self.age <= activeage and self.showgrowing:  # Increase entity size
                self.sz += 1
                ShowGrowing(self.entity, self.cx, self.cy, self.sz)
            elif self.age >= passiveage and self.showungrowing:  # Decrease entity size
                self.dsz -= 1
                ShowUngrowing(self.entity, self.cx, self.cy, self.dsz)
            if self.age in self.chbirth: # If entity produces offspring in this age
                end = False
                for i in range(self.chbirth.count(self.age)): # Possibly several children in this age
                    if amount != allamount:
                        entities += [CreateEntity(self.cx, self.cy, self.dir1)]
                        self.chcount += 1
                    else:
                        end = True
                        break
                if end:
                    End("There is no place!",
                             f"Time: {time}\nThe number of entities born:{born}\nThe number of dead:{dead}")


def End(title, msg):
    AddPopulation()
    lbr.insert(0, f"Population_{population_key}")
    Stop()
    showinfo(title, msg)
    ShowStatistics()


def PlaceInfo(event, *args):  # Show entity info on Label
    infolabel.config(text=f"Age:{args[0]}\nChildren:{args[1]}\nSudden death:{args[2]}")
    lw, lh = infolabel.winfo_width(), infolabel.winfo_height()
    if event.x + lw/2 > wd and event.y + lh/2 > ht:
        infolabel.place(x=event.x - lw, y=event.y - lh - 4)
    elif event.x - lw/2 < 0 and event.y - lh/2 < 0:
        infolabel.place(x=event.x + 10, y=event.y + 10)
    elif event.x + lw/2 > wd:
        infolabel.place(x=event.x - lw, y=event.y + 10)
    elif event.x - lw/2 < 0:
        infolabel.place(x=event.x + 10, y=event.y + 10)
    elif event.y - lh/2 < 0:
        infolabel.place(x=event.x - lw/2, y=event.y + 10)
    else:
        infolabel.place(x=event.x - lw/2, y=event.y + 10)


def UnplaceInfo(event=None):  # Hide Label
    infolabel.place_forget()


def ShowGrowing(ent, x, y, d):  # Entity size changes
    ds = (d * incsize) / 2
    c.coords(ent, x + ds, y + ds, x - ds, y - ds)


def ShowUngrowing(ent, x, y, d):
    ds = (d * decsize) / 2
    c.coords(ent, x + ds, y + ds, x - ds, y - ds)


class CreateEntity(Entity):

    """Creates entity in the nearest place"""

    def __init__(self, cx, cy, dir1): # !!!!!!!!!
        w1 = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (-1, -1), (1, 1)]
        while len(w1) != 0:
            i = random.randint(0, len(w1) - 1)
            if (dir1[0] + w1[i][0], dir1[1] + w1[i][1],) not in usedcoords:
                if all((dir1[0] + w1[i][0] > 0, dir1[0] + w1[i][0] < a,
                        dir1[1] + w1[i][1] > 0, dir1[1] + w1[i][1] < a)):
                    g = (cx + step * w1[i][0], cy + step * w1[i][1])
                    d = (dir1[0] + w1[i][0], dir1[1] + w1[i][1])
                    Entity.__init__(self, g[0], g[1], d)
                    pb.config(value=amount / allamount * 100)
                    break
                else:
                    del w1[i]
            else:
                del w1[i]
        else:
            f = False
            s = 2.5
            while not f:
                for i in range(int(s * 2)):
                    w1 += ((i - s + 0.5, -s + 0.5), (i - s + 0.5, s - 0.5),)
                for i in range(1, int(s * 2) - 1):
                    w1 += ((-s + 0.5, i - s + 0.5), (s - 0.5, i - s + 0.5),)
                while len(w1) != 0:
                    i = random.randint(0, len(w1) - 1)
                    if (dir1[0] + w1[i][0], dir1[1] + w1[i][1],) not in usedcoords:
                        if all((dir1[0] + w1[i][0] > 0, dir1[0] + w1[i][0] < a,
                                dir1[1] + w1[i][1] > 0, dir1[1] + w1[i][1] < a)):
                            g = (cx + step * w1[i][0], cy + step * w1[i][1])
                            d = (dir1[0] + w1[i][0], dir1[1] + w1[i][1])
                            Entity.__init__(self, g[0], g[1], d)
                            pb.config(value=amount / allamount * 100)
                            f = True
                            break
                        else:
                            del w1[i]
                    else:
                        del w1[i]
                else:
                    s += 1


def CanvasBG():  # Changes canvas colour
    cl = askcolor()[1]
    if cl.__ne__(None):
        c.config(bg=cl)


def Remove():
    global acting, time, amount, birthrate, built, born, dead, usedcoords, entities
    for entity in entities:
        entity.RemoveFromCanvas()
    entities, usedcoords = [], []
    birthrate = ()
    amount, born, dead, time = 0, 0, 0, 0
    pb.config(value=0)
    acting, built = False, False
    timer.config(text=f"Time: {time}")
    if bv2.get():
        # Grid(False)
        Grid(True)


def ShowStatistics():
    Stop()
    stats_window.deiconify()
    stats_window.grab_set()
    x = list(range(0, time))
    y = birthrate
    plot1.clear()
    plot1.set_xlabel("Time")
    plot1.set_ylabel("Population")
    plot1.set_title("Dynamic of population")
    plot1.grid()
    plot1.plot(x, y)
    canvas.draw()


def AddPopulationParameterToText(kword:str, value:str):
    population_text.insert(END, kword+": ", "keyword")
    population_text.insert(END, value+"\n")


def ShowPopulationInfo(event):
    population_selection = lbr.curselection()
    if population_selection: # If there is a selected population in listbox
        key = int(lbr.get(population_selection[0]).split("_")[1])
        Stop()
        population_window.title(f"Population_{key} stats")
        population_window.deiconify()
        population_window.grab_set()
        population_parameters = populations[key]
        _time = population_parameters["time"]
        _amount = population_parameters["amount"]
        _allamount = population_parameters["allamount"]
        _birthrate = population_parameters["birthrate"]
        _deathage = population_parameters["deathage"]
        _activeage = population_parameters["activeage"]
        _passiveage = population_parameters["passiveage"]
        _deathprobability = population_parameters["deathprobability"]
        _firstentities = population_parameters["firstentities"]
        _children = population_parameters["children"]
        _born = population_parameters["born"]
        _dead = population_parameters["dead"]
        _randomness = population_parameters["randomness"]
        population_text.config(state=NORMAL)
        population_text.delete("1.0", END)
        AddPopulationParameterToText("Time", str(_time))
        AddPopulationParameterToText("Entities", str(_amount))
        AddPopulationParameterToText("Max places", str(_allamount))
        AddPopulationParameterToText("Death age", str(_deathage))
        AddPopulationParameterToText("Active age", str(_activeage))
        AddPopulationParameterToText("Passive age", str(_passiveage))
        AddPopulationParameterToText("Sudden death(%)", str(_deathprobability))
        AddPopulationParameterToText("Entities on start", str(_firstentities))
        AddPopulationParameterToText("Children", str(_children))
        AddPopulationParameterToText("Born", str(_born))
        AddPopulationParameterToText("Dead", str(_dead))
        AddPopulationParameterToText("Random max children", str(_randomness))
        population_text.config(state=DISABLED)

        x = list(range(0, _time))
        y = _birthrate
        population_plot.clear()
        population_plot.set_xlabel("Time")
        population_plot.set_ylabel("Population")
        population_plot.set_title("Dynamic of population")
        population_plot.grid()
        population_plot.plot(x, y)
        population_canvas.draw()
    else:
        pass


def AddPopulation():
    global population_key
    population_key += 1
    populations[population_key] = {
        "time": time,
        "amount": amount,
        "allamount": allamount,
        "birthrate": birthrate,
        "deathage": deathage,
        "activeage": activeage,
        "passiveage": passiveage,
        "deathprobability": deathprobability,
        "firstentities": firstentities,
        "children": children,
        "born": born,
        "dead": dead,
        "randomness": randomness,
    }


def Build():
    global a, wd, ht, step, deathage, speed, cx, cy, deathprobability, entities, amount
    global activeage, passiveage, children, time, wdconst, htconst, allamount, usedcoords
    global birthrate, built, born, dead, end, firstentities, incsize, decsize, randomness
    for entity in entities:
        entity.RemoveFromCanvas()
    entities, usedcoords = [], []
    built, end = True, False
    birthrate = ()
    amount, born, dead, time = 0, 0, 0, 0
    pb.config(value=0)
    timer.config(text=f"Time: {time}")
    wd, ht = int(scwd.get()), int(scht.get())
    c.config(width=wd, height=ht)
    a = int(sc1.get())
    allamount = a ** 2
    deathage = int(sc2.get())
    sc4.config(to=deathage)
    sc5.config(to=deathage, from_=sc4.get())
    sc5.config(from_=sc4.get())
    deathprobability = int(sc6.get())
    speed = int(sc3.get())
    activeage, passiveage = int(sc4.get()), int(sc5.get())
    children, firstentities = int(sc7.get()), int(sc8.get())
    randomness = bv4.get()
    step = ht / a if wd > ht else wd / a
    incsize = step / activeage
    decsize = step / (deathage - passiveage) if deathage.__ne__(passiveage) else step
    wdconst, htconst = (wd - ht) / 2, (ht - wd) / 2
    if wd >= ht:
        htconst = 0
    else:
        wdconst = 0
    cx, cy = wdconst + step * (a // 2) + step / 2, htconst + step * (a // 2) + step / 2
    c1, c2 = a / 2 if a % 2 != 0 else a / 2 + 0.5, a / 2 if a % 2 != 0 else a / 2 + 0.5
    entities += [Entity(cx, cy, (c1, c1))]
    cx, cy, c1, c2 = entities[0].cx, entities[0].cy, entities[0].dir1[0], entities[0].dir1[1]
    for i in range(firstentities - 1):
        entities += [CreateEntity(cx, cy, (c1, c2))]
        cx, cy, c1, c2 = entities[-2].cx, entities[-2].cy, entities[-2].dir1[0], entities[-2].dir1[1]
    if bv2.get():
        Grid(False)
        Grid(True)


def Start():
    global acting
    if not acting:
        if built and not end:
            acting = True
            root.after(speed, AutoStep)
        else:
            showinfo("Start", "To begin, create the first entity!")
    else:
        showinfo("Start", "The process has already started!")


def Stop():
    global acting
    acting = False


def IncreaseAgeForEntities():
    for ent in entities:
            if not end: # Some entity can randomly produce the offspring and take the last place in this age so we need to check
                ent.IncreaseAge()
            else: # If all the places are taken there is no need to continue loop
                break


def AutoStep():
    global time, birthrate
    if acting:
        IncreaseAgeForEntities()
        time += 1
        timer.config(text=f"Time:{time}")
        birthrate += (amount,)
        root.after(speed, AutoStep)


def Step():
    global time, birthrate
    if built and not end:
        IncreaseAgeForEntities()
        time += 1
        timer.config(text=f"Time:{time}")
        birthrate += (amount,)
    else:
        showinfo("Start", "To begin, create the first entity!")


def SetLines():
    sc8.config(to=sc1.get())
    if sc8.get() < sc1.get():
        lab1.config(text=str(int(sc1.get())))
    else:
        lab1.config(text=str(int(sc1.get())))
        sc8.set(sc1.get())
        lab8.config(text="Initial amount")


def SetLifeDuration():
    lab2.config(text=str(int(sc2.get())))
    sc4.config(to=sc2.get())
    sc5.config(to=sc2.get(), from_=sc4.get())
    if sc4.get() > sc2.get():
        sc4.set(sc2.get())
        lab4.config(text="Active age")
    if sc5.get() > sc2.get():
        sc5.set(sc2.get())
        lab5.config(text="Passive age")


def SetActiveAge():
    lab4.config(text=str(int(sc4.get())))
    if sc4.get() > sc5.get():
        sc5.config(from_=sc4.get())
        sc5.set(sc4.get())
        lab5.config(text="Passive age")
    else:
        sc5.config(from_=sc4.get())


def Grid(mode=True):
    global gridlines, wdconst, htconst
    if mode:
        Grid(False)
        wdconst, htconst = (wd - ht) / 2, (ht - wd) / 2
        if wd >= ht:
            htconst = 0
        else:
            wdconst = 0
        for i in range(0, a + 1):
            gridline = c.create_line((wdconst + step * i, htconst), (wdconst + step * i, ht - htconst))
            c.tag_lower(gridline)
            gridlines.insert(-1, gridline)
        for i in range(0, a + 1):
            gridline = c.create_line((wdconst, htconst + step * i), (wd - wdconst, step * i + htconst))
            c.tag_lower(gridline)
            gridlines.insert(-1, gridline)
    else:
        for i in gridlines:
            c.delete(i)


def DelAndQuit():
    root.destroy()


def MouseWheel(event):
    c.yview_scroll(-1 * int(event.delta / 120), UNITS)


def BindB1Down():
    global xb, yb
    xb, yb = 0, 0

    def SetFirst(e):
        global xb, yb
        xb, yb = c.canvasx(e.x), c.canvasy(e.y)
        c.config(cursor="sizing")
        c.create_rectangle((xb + 1, yb + 1), (xb - 1, yb - 1), outline="black",
                           dash=(5, 1), tag="moving", width=2)

    def PlaceInfo(event):
        c.delete("moving")
        c.config(cursor="arrow")
        k = len(set(c.find_overlapping(xb, yb, c.canvasx(event.x), c.canvasy(event.y))) - set(gridlines))
        if k != 0:
            amountlabel.config(text=f"The number of entities: {k}")
            amountlabel.place(x=wd / 2 - amountlabel.winfo_width() / 2, y=10)
            amountlabel.bind("<Enter>", lambda e: amountlabel.place_forget(), amountlabel.unbind("<Leave>"))

    c.bind("<ButtonPress-1>", lambda e: SetFirst(e))
    c.bind("<B1-Motion>", lambda e: c.coords("moving", xb, yb, c.canvasx(e.x), c.canvasy(e.y)))
    c.bind("<ButtonRelease-1>", lambda e: PlaceInfo(e))


def ScaleMotion(scale, label):
    label.config(text=str(int(scale.get())))


def SetDefaultCanvasSize():
    wd, ht = 500, 500
    c.config(width=500, height=500)
    scwd.set(wd)
    scht.set(ht)


def AddTooltips():
    ToolTip(lab1, "Number of lines\n(and columns)").waittime = 350
    ToolTip(lab2, "Lifetime").waittime = 350
    ToolTip(lab3, "At what speed will the\nage of entities change at the start\n(in mc)").waittime = 350
    ToolTip(lab4, "The beginning of the active age.\nEnds before passive age").waittime = 350
    ToolTip(lab5, "The beginning of passive age.\nEnds when death comes").waittime = 350
    ToolTip(lab6, "Probability of sudden death(%).\nIf the probability of sudden death exist, enity can die\n in "
                  "any age").waittime = 350
    ToolTip(lab7, "The number of offspring.\nMay vary depending on whether randomness is enabled").waittime = 350
    ToolTip(lab8, "The number of entities in the beginning").waittime = 350

# Defining global variables

ICON_BYTES = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAIGNIUk0AAHomAACAhAAA+gAAAIDoAAB1MAAA6mAAAD" \
       b"qYAAAXcJy6UTwAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAABYktHRFoDu6WiAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE0" \
       b"LTAxLTI2VDIwOjU5OjM3KzAyOjAw+5oHdwAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxNC0wMS0yNlQyMDo1OTowMCswMj" \
       b"owMMHvhqYAAAHRSURBVDhPjZO/S1tRFMe/7+V3mgRMkCRDC0kIFDoYB80kVLIUNI6l+AcUq+BSqIUudfIfUAdHF9FB" \
       b"xMUfFOKaqS22Lh1aDPnRhlokmPde3o+Yc3MwjU80n+Xc77nn3HPvufdK7Q74j5X979g7PGHV4+XzEcxNjcLr9cLhcL" \
       b"AXkNneQMnF9QVWPXZOvqJUKkFVVfZ0sS1AZOfXeNRPtVpFs9lk1UUcYbtYQvXiCobRgtFqQVOb0DUVlmGgcHoOyzRF" \
       b"8PJMCplMBrFYTGjC+XH3DAefCiwfJqYvwvqpox3IQ3v0CvKgydn0MFwuF/D3M+TLb5AutlCpVO7uwW0oOZf0IBeZY0" \
       b"+necov0RNp/M1q3zUSS9NP4bYUOJ1OSJIEt9uNyaHXPNvj+M+afYEPLx5j5slbVvdz9Hu1/wjv888GTiZoZ/K72RzL" \
       b"jsO64tFgBINBSIqitKkZ5XIZHo8HY65Znr6fwr8NJBIJSKZptjVNEy+MGhY+z3KIHUoKBALw+XwIhUKIRCKQOwgHiX" \
       b"A4zKG3yPwQhgrE43GkUilh/X6//R0YyU0YwQlWzJe0MPSQKIkK0pgWtH1n+m31eh21Wg2NRgO6rtM2RcOoajQaFV+6" \
       b"C3ANyd+fcOghqNIAAAAASUVORK5CYII="
entities, usedcoords, gridlines = [], [], [],
birthrate = ()
colors = ("lime", "#AEFF00", "#D4FF00", "#EAFF00", "#FFFF00", "#FFDD00", "#FFBF00", "#FFA500", "#FF5E00", "red")
amount, born, dead, time, allamount, step, xb, yb, wdconst, htconst = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
deathprobability, incsize, decsize = 0, 0, 0
speed = 1000
wd, ht = 500, 500
cx, cy = wd // 2, ht // 2
a = 11
deathage = 45
activeage = 15
passiveage = 35
children = 2
built, acting, end = False, False, False
firstentities = 1
randomness = False
populations = {}
population_key = 0

root = ThemedTk(theme="black")
img1 = PhotoImage(data=ICON_BYTES)
root.call('wm', 'iconphoto', root._w, img1)
root.geometry("+0+0")
root.config(bg="#424242")
root.title("OOP.Entities")
root.protocol("WM_DELETE_WINDOW", DelAndQuit)
mf = ttk.LabelFrame(root, text="Main window", relief=RIDGE)
ft = ttk.LabelFrame(mf, text="Parameters", relief=RIDGE, labelanchor=N)
sc1 = ttk.Scale(ft, from_=3, to=50, orient=HORIZONTAL)
sc1.set(a)
sc1.grid(row=0, column=1, padx=10, pady=4)
lab1 = ttk.Label(ft, text="Lines", width=16)
lab1.grid(row=1, column=1, padx=10, pady=4)
sc1.bind("<Enter>", lambda e: ScaleMotion(sc1, lab1))
sc1.bind("<Leave>", lambda e: lab1.config(text="Lines"))
sc1.config(command=lambda e: SetLines())
sc2 = ttk.Scale(ft, from_=1, to=500, orient=HORIZONTAL)
sc2.set(deathage)
sc2.grid(row=0, column=2, padx=10, pady=4)
lab2 = ttk.Label(ft, text="Lifetime", width=16)
lab2.grid(row=1, column=2, padx=10, pady=4)
sc2.bind("<Enter>", lambda e: ScaleMotion(sc2, lab2))
sc2.bind("<Leave>", lambda e: lab2.config(text="Lifetime"))
sc3 = ttk.Scale(ft, from_=100, to=5000, orient=HORIZONTAL)
sc3.set(speed)
sc3.grid(row=0, column=3, padx=10, pady=4)
lab3 = ttk.Label(ft, text="Time speed(ms)", width=18)
lab3.grid(row=1, column=3, padx=10, pady=4)
sc3.bind("<Enter>", lambda e: ScaleMotion(sc3, lab3))
sc3.bind("<Leave>", lambda e: lab3.config(text="Time speed(ms)"))
sc3.config(command=lambda e: ScaleMotion(sc3, lab3))
sc4 = ttk.Scale(ft, from_=1, to=deathage, orient=HORIZONTAL)
sc4.set(activeage)
sc4.grid(row=0, column=4, padx=10, pady=4)
lab4 = ttk.Label(ft, text="Active age", width=16)
lab4.grid(row=1, column=4, padx=10, pady=4)
sc4.bind("<Enter>", lambda e: ScaleMotion(sc4, lab4))
sc4.bind("<Leave>", lambda e: lab4.config(text="Active age"))
sc5 = ttk.Scale(ft, from_=activeage, to=deathage, orient=HORIZONTAL)
sc5.set(passiveage)
sc5.grid(row=0, column=5, padx=10, pady=4)
sc2.config(command=lambda e: SetLifeDuration())
sc4.config(command=lambda e: SetActiveAge())
lab5 = ttk.Label(ft, text="Passive age", width=16)
lab5.grid(row=1, column=5, padx=10, pady=4)
sc5.bind("<Enter>", lambda e: ScaleMotion(sc5, lab5))
sc5.bind("<Leave>", lambda e: lab5.config(text="Passive age"))
sc5.config(command=lambda e: ScaleMotion(sc5, lab5))
sc6 = ttk.Scale(ft, from_=0, to=100, orient=HORIZONTAL)
sc6.set(deathprobability)
sc6.grid(row=0, column=6, padx=10, pady=4)
lab6 = ttk.Label(ft, text="Sudden death probability", width=18)
lab6.grid(row=1, column=6, padx=10, pady=4)
sc6.bind("<Enter>", lambda e: ScaleMotion(sc6, lab6))
sc6.bind("<Leave>", lambda e: lab6.config(text="Sudden death probability"))
sc6.config(command=lambda e: ScaleMotion(sc6, lab6))
sc7 = ttk.Scale(ft, from_=1, to=20, orient=HORIZONTAL)
sc7.set(children)
sc7.grid(row=0, column=7, padx=10, pady=4)
infoscale = ttk.Label(ft)
lab7 = ttk.Label(ft, text="The number of offspring", width=18)
lab7.grid(row=1, column=7, padx=10, pady=4)
sc7.bind("<Enter>", lambda e: ScaleMotion(sc7, lab7))
sc7.bind("<Leave>", lambda e: lab7.config(text="The number of offspring"))
sc7.config(command=lambda e: ScaleMotion(sc7, lab7))
sc8 = ttk.Scale(ft, from_=1, to=11, orient=HORIZONTAL)
sc8.set(firstentities)
sc8.grid(row=0, column=8, padx=10, pady=4)
lab8 = ttk.Label(ft, text="Initial number", width=19)
lab8.grid(row=1, column=8, padx=10, pady=4)
sc8.bind("<Enter>", lambda e: ScaleMotion(sc8, lab8))
sc8.bind("<Leave>", lambda e: lab8.config(text="Initial number"))
sc8.config(command=lambda e: ScaleMotion(sc8, lab8))
ft.pack(side=TOP, fill=X, padx=6, pady=6)
fc = ttk.LabelFrame(mf, relief=RIDGE)
fcc = ttk.LabelFrame(fc, relief=RIDGE)
c = Canvas(fcc, width=wd, height=ht,
           bg="silver", scrollregion=(0, 0, root.winfo_screenwidth(), root.winfo_screenheight()))
c.bind("<MouseWheel>", MouseWheel)
csbx = ttk.Scrollbar(fcc, orient=HORIZONTAL)
csby = ttk.Scrollbar(fcc, orient=VERTICAL)
csbx.pack(side=BOTTOM, fill=X)
csbx.config(command=c.xview)
csby.config(command=c.yview)
csby.pack(side=RIGHT, fill=Y)
c.pack(side=LEFT, padx=4, pady=4)
infolabel = ttk.Label(c, text="")
amountlabel = ttk.Label(c, text="", font=("", 12))
c.config(xscrollcommand=csbx.set, yscrollcommand=csby.set)
BindB1Down()
fcc.pack(side=LEFT)
sb1 = ttk.Scrollbar(fc, orient=VERTICAL)
lbr = Listbox(fc, yscrollcommand=sb1.set, bg="silver", width=25)
lbr.bind('<Double-1>', lambda e: ShowPopulationInfo(e))
lbr.config(yscrollcommand=sb1.set)
lbr.pack(side=LEFT, fill=Y, padx=10)
sb1.pack(side=LEFT, fill=Y)
sb1.config(command=lbr.yview)
fcb = ttk.LabelFrame(fc, text="Canvas size(width and height)", relief=RIDGE, labelanchor=N)
labsize = ttk.Label(fcb, text=f"{wd}x{ht}")
labsize.grid(row=0, column=0, columnspan=2)
scwd = ttk.Scale(fcb, from_=100, to=root.winfo_screenwidth(), orient=HORIZONTAL)
scwd.set(wd)
scwd.grid(row=1, column=0, padx=10, pady=6)
scht = ttk.Scale(fcb, from_=100, to=root.winfo_screenheight(), orient=HORIZONTAL,
                 command=lambda e: labsize.config(text=f"{int(scwd.get())}x{int(scht.get())}"))
scwd.config(command=lambda e: labsize.config(text=f"{int(scwd.get())}x{int(scht.get())}"))
scht.set(ht)
scht.grid(row=1, column=1, padx=10, pady=6)
fcb.pack(side=TOP, anchor=W, pady=4, padx=4)
bv = BooleanVar()
bv.set(False)
btn4 = ttk.Button(fc, text="Default canvas size", width=25, command=SetDefaultCanvasSize)
btn4.pack(side=TOP, anchor=W, pady=4, padx=4)
bv5 = BooleanVar()
bv5.set(False)
cb5 = ttk.Checkbutton(fc, text="Change colour", variable=bv5, onvalue=True,
                      offvalue=False)
cb5.pack(side=TOP, anchor=W, pady=4, padx=4)
cb1 = ttk.Checkbutton(fc, text="Ability to grow", variable=bv, onvalue=True,
                      offvalue=False)
cb1.pack(side=TOP, anchor=W, pady=4, padx=4)
bv3 = BooleanVar()
bv3.set(False)
cb3 = ttk.Checkbutton(fc, text="Ability to decrease", variable=bv3, onvalue=True,
                      offvalue=False)
cb3.pack(side=TOP, anchor=W, pady=4, padx=4)
bv2 = BooleanVar()
bv2.set(False)
cb2 = ttk.Checkbutton(fc, text="Grid", variable=bv2, onvalue=True, offvalue=False,
                      command=lambda: Grid(bv2.get()))
cb2.pack(side=TOP, anchor=W, pady=4, padx=4)
bv4 = BooleanVar()
bv4.set(randomness)
cb4 = ttk.Checkbutton(fc, text="Randeomness", variable=bv4, onvalue=True, offvalue=False)
cb4.pack(side=TOP, anchor=W, pady=4, padx=4)
pb = ttk.Progressbar(fc, value=0, length=200)
pb.pack(side=BOTTOM, pady=10)
fc.pack(fill=X, padx=6, pady=6)
fb = ttk.LabelFrame(mf, relief=FLAT)
btn2 = ttk.Button(fb, text="Start", width=10, command=Start)
btn2.pack(side=LEFT, padx=10, pady=10)
btn3 = ttk.Button(fb, text="Stop", width=10, command=Stop)
btn3.pack(side=LEFT, padx=10, pady=10)
btnstep = ttk.Button(fb, text="Step", width=10, command=Step)
btnstep.pack(side=LEFT, padx=10, pady=10)
btn1 = ttk.Button(fb, text="Build", width=10, command=Build)
btn1.pack(side=LEFT, padx=10, pady=10)
btnclear = ttk.Button(fb, text="Remove", width=10, command=Remove)
btnclear.pack(side=LEFT, padx=10, pady=10)
btnstat = ttk.Button(fb, text="Stats", width=10, command=ShowStatistics)
btnstat.pack(side=LEFT, padx=10, pady=10)
btn4 = ttk.Button(fb, text="BG", command=CanvasBG)
btn4.pack(side=LEFT, padx=10, pady=10)
timer = ttk.Label(fb, text=f"Time: {time}", font=("", 14), width=12)
timer.pack(side=LEFT, padx=10, pady=10)
fb.pack(side=BOTTOM, fill="x")
mf.pack(padx=8, pady=8)

AddTooltips()

# Defining Toplevel Population stat

FIGURE_SIZE = (4, 3)


population_window = Toplevel(root, highlightthickness=8, highlightcolor="black")
root.call('wm', 'iconphoto', population_window, img1)
population_window.config(bg="#424242")
population_window.transient(root)
population_window.withdraw()
population_window.protocol("WM_DELETE_WINDOW", lambda: (population_window.withdraw(), population_window.grab_release()))

population_text = Text(population_window, width=30, font=("Arial", 11, "normal"), bg="#424242", fg="silver", wrap=WORD, relief=FLAT)
population_text.tag_config('keyword', foreground="yellow", font=("Arial", 11, "bold"))
population_text.grid(row=0, column=0)

population_figure = Figure(figsize=FIGURE_SIZE, constrained_layout=True)
population_figure.patch.set_facecolor("#424242")
population_plot = population_figure.add_subplot(facecolor="silver")
population_canvas = FigureCanvasTkAgg(population_figure, population_window)
population_canvas.get_tk_widget().grid(row=0, column=1)

# End defining

# Defining TopLevel Statictics

stats_window = Toplevel(root, highlightthickness=8, highlightcolor="black")
root.call('wm', 'iconphoto', stats_window, img1)
stats_window.config(bg="#424242")
stats_window.transient(root)
stats_window.title("Stats")
stats_window.withdraw()
stats_window.protocol("WM_DELETE_WINDOW", lambda: (stats_window.withdraw(), stats_window.grab_release()))

figure = Figure(figsize=FIGURE_SIZE, constrained_layout=True)
figure.patch.set_facecolor("#424242")
plot1 = figure.add_subplot(facecolor="silver")
canvas = FigureCanvasTkAgg(figure, stats_window)
canvas.get_tk_widget().grid(row=0, column=0)

# End defining

root.mainloop()

# End defining