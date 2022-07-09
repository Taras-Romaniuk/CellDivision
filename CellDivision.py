from tkinter import *
from tkinter import ttk
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo
from ttkthemes import ThemedTk  # Стиль вікна
import random
import matplotlib  # Графіки для статистики
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from belfrywidgets import ToolTip

matplotlib.use("TkAgg")


class Entity(object):
    """Істота"""

    def __init__(self, x, y, dir1):  # Створення істоти
        global colors, deathage, activeage, passiveage, deathprobability, children, usedcoords, amount
        global born, step, decsize
        amount += 1
        born += 1
        usedcoords.append(dir1)
        self.cll = len(colors)
        if bv4.get():
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
        if bv.get():  # Якщо ріст вкл.
            ds = (step / activeage) / 2
            self.sz = 0
            self.entity = c.create_oval((x + ds, y + ds), (x - ds, y - ds), fill=colors[0],
                                        outline=colors[0], activewidth=6, activedash=(5, 1))
        else:
            self.entity = c.create_oval((x - step / 2, y - step / 2), (x + step / 2, y + step / 2),
                                        fill=colors[0], outline=colors[0], activewidth=6, activedash=(5, 1))
        c.tag_bind(self.entity, "<Enter>", lambda e: PlaceInfo(e, self.age, self.chcount, self.suddendeathage))
        c.tag_bind(self.entity, "<Leave>", lambda e: UnplaceInfo())

    def MyTimeHasCome(self, msg=False):  # І тут приходить смерть істоти
        global usedcoords, amount, allamount, dead, entities, deathage, end
        amount -= 1
        dead += 1
        pb.config(value=amount / allamount * 100)
        usedcoords.remove(self.dir1)
        if infolabel.winfo_ismapped():
            UnplaceInfo()
        if msg:
            m = deathage if self.suddendeathage == None else self.suddendeathage
            lbr.insert(0, f"Істота померла у віці {m}")
        c.delete(self.entity)
        del entities[entities.index(self)]
        if amount == 0 and msg:
            end = True
            Stop()
            showinfo("Всі істоти вимерли!",
                     f"Час: {time}\nКількість народжених істот:{born}\nКількість померлих:{dead}")
            ShowStatistics()

    def IncreaseAge(self):  # Вік зростає на одну одиницю
        global amount, allamount, end, entities, deathage, activeage, colors
        self.age += 1
        if self.age == self.suddendeathage:  # Якщо наступила раптова смерть
            self.MyTimeHasCome(True)
        elif self.age == deathage:  # Якщо наступила смерть
            self.MyTimeHasCome(True)
        else:
            if self.showcolor:
                if self.s != self.cll and self.age == self.k * (self.s + 1):  # Змінити колір
                    c.itemconfig(self.entity, fill=colors[self.s], outline=colors[self.s])
                    self.s += 1
            if self.age <= activeage and self.showgrowing:  # Збільшити розмір істоти
                self.sz += 1
                ShowGrowing(self.entity, self.cx, self.cy, self.sz)
            elif self.age >= passiveage and self.showungrowing:  # Зменшити розмір істоти
                self.dsz -= 1
                ShowUngrowing(self.entity, self.cx, self.cy, self.dsz)
            if self.age in self.chbirth:
                end = False
                for i in range(self.chbirth.count(self.age)):
                    if amount != allamount:
                        entities += [CreateEntity(self.cx, self.cy, self.dir1)]
                        self.chcount += 1
                    else:
                        end = True
                        break
                if end:
                    Stop()
                    showinfo("Все зайнято!",
                             f"Час: {time}\nКількість народжених істот:{born}\nКількість померлих:{dead}")
                    ShowStatistics()


def PlaceInfo(event, *args):  # Показати інформацію істоти на Label
    infolabel.config(text=f"Вік:{args[0]}\nДіти:{args[1]}\nРаптова смерть:{args[2]}")
    infolabel.place(x=event.x + 10, y=event.y + 10)


def UnplaceInfo(event=None):  # Приховати Label з інформацією
    infolabel.place_forget()


def ShowGrowing(ent, x, y, d):  # Змінюється розмір істоти
    global incsize
    ds = (d * incsize) / 2
    c.coords(ent, x + ds, y + ds, x - ds, y - ds)


def ShowUngrowing(ent, x, y, d):
    global decsize
    ds = (d * decsize) / 2
    c.coords(ent, x + ds, y + ds, x - ds, y - ds)


class CreateEntity(Entity):
    """Створити істоту"""

    def __init__(self, cx, cy, dir1):
        global usedcoords, activeage, entities, allamount, amount, a, time, step
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


def CanvasBG():  # Змінює колір канвасу
    cl = askcolor()[1]
    if cl.__ne__(None):
        c.config(bg=cl)


def Remove():
    global acting, time, entities, usedcoords, amount, birthrate, built, born, dead
    birthrate = ()
    amount, born, dead, time = 0, 0, 0, 0
    pb.config(value=0)
    acting, built = False, False
    while entities.__ne__([]):
        entities[0].MyTimeHasCome()
    timer.config(text=f"Час: {time}")
    lbr.delete(0, END)
    if bv2.get():
        Grid(False)
        Grid(True)


def ShowStatistics():
    global time, birthrate, end, img1
    stat = Toplevel(highlightthickness=8, highlightcolor="black")
    root.call('wm', 'iconphoto', stat, img1)
    stat.config(bg="#424242")
    stat.transient(root)
    stat.title("Статистика")
    stat.grab_set()
    figure = Figure()
    figure.patch.set_facecolor("#424242")
    plot = figure.add_subplot(facecolor="silver")
    plot.grid()
    plot.set_xlabel("Час")
    plot.set_ylabel("Кількість народжених істот")
    plot.set_title("Стат 1")
    x = list(i for i in range(0, time))
    y = birthrate
    if end:
        del x[-1]
    plot.plot(x, y)
    fig1 = FigureCanvasTkAgg(figure, stat)
    fig1.get_tk_widget().grid(row=0, column=0)
    figure2 = Figure()
    figure2.patch.set_facecolor("#424242")
    plot2 = figure2.add_subplot(facecolor="silver")
    plot2.set_xlabel("Час")
    plot2.set_ylabel("Народжуваність")
    plot2.set_title("Стат 2")
    br = y
    if time > 1:
        br = (0,)
        for i in range(1, len(y)):
            br += (y[i] - y[i - 1],)
    plot2.plot(x, br)
    plot2.grid()
    fig2 = FigureCanvasTkAgg(figure2, stat)
    fig2.get_tk_widget().grid(row=0, column=1)
    stat.mainloop()


def Build():
    global a, wd, ht, step, deathage, speed, cx, cy, deathprobability, entities, amount
    global activeage, passiveage, children, time, wdconst, htconst, usedcoords, allamount
    global birthrate, built, born, dead, end, firstentities, incsize, decsize
    while entities.__ne__([]):
        entities[0].MyTimeHasCome()
    built, end = True, False
    birthrate = ()
    amount, born, dead, time = 0, 0, 0, 0
    pb.config(value=0)
    timer.config(text=f"Час: {time}")
    lbr.delete(0, END)
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
    global acting, speed, built, end
    if not acting:
        if built and not end:
            acting = True
            root.after(speed, AutoStep)
        else:
            showinfo("Початок", "Для початку створіть першу істоту!")
    else:
        showinfo("Початок", "Процес вже почато!")


def Stop():
    global acting
    acting = False


def AutoStep():
    global step, speed, acting, time, entities, birthrate, amount
    if acting:
        time += 1
        timer.config(text=f"Час:{time}")
        for ent in entities:
            ent.IncreaseAge()
        birthrate += (amount,)
        root.after(speed, AutoStep)


def Step():
    global built, time, birthrate, entities, end
    if built and not end:
        time += 1
        timer.config(text=f"Час:{time}")
        for ent in entities:
            ent.IncreaseAge()
        birthrate += (amount,)
    else:
        showinfo("Початок", "Для початку створіть першу істоту!")


def SetLines():
    sc8.config(to=sc1.get())
    if sc8.get() < sc1.get():
        lab1.config(text=str(int(sc1.get())))
    else:
        lab1.config(text=str(int(sc1.get())))
        sc8.set(sc1.get())
        lab8.config(text="Початкова кількість")


def SetLifeDuration():
    lab2.config(text=str(int(sc2.get())))
    sc4.config(to=sc2.get())
    sc5.config(to=sc2.get(), from_=sc4.get())
    if sc4.get() > sc2.get():
        sc4.set(sc2.get())
        lab4.config(text="Активний вік")
    if sc5.get() > sc2.get():
        sc5.set(sc2.get())
        lab5.config(text="Пасивний вік")


def SetActiveAge():
    lab4.config(text=str(int(sc4.get())))
    if sc4.get() > sc5.get():
        sc5.config(from_=sc4.get())
        sc5.set(sc4.get())
        lab5.config(text="Пасивний вік")
    else:
        sc5.config(from_=sc4.get())


def Grid(mode=True):
    global gridlines, step, a, wd, ht, wdconst, htconst
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
    global entities
    while entities.__ne__([]):
        entities[0].MyTimeHasCome()
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
        global gridlines, wd
        c.delete("moving")
        c.config(cursor="arrow")
        k = len(set(c.find_overlapping(xb, yb, c.canvasx(event.x), c.canvasy(event.y))) - set(gridlines))
        if k != 0:
            amountlabel.config(text=f"Кількість істот: {k}")
            amountlabel.place(x=wd / 2 - amountlabel.winfo_width() / 2, y=10)
            amountlabel.bind("<Enter>", lambda e: amountlabel.place_forget(), amountlabel.unbind("<Leave>"))

    c.bind("<ButtonPress-1>", lambda e: SetFirst(e))
    c.bind("<B1-Motion>", lambda e: c.coords("moving", xb, yb, c.canvasx(e.x), c.canvasy(e.y)))
    c.bind("<ButtonRelease-1>", lambda e: PlaceInfo(e))


def ScaleMotion(scale, label):
    label.config(text=str(int(scale.get())))


def AddTooltips():
    ToolTip(lab1, "Кількість рядків\n(і стовпців)").waittime = 350
    ToolTip(lab2, "Тривалість життя\nоднієї істоти").waittime = 350
    ToolTip(lab3, "З якою швидкістю буде\nзмінюватись вік істот при старті\n(в мс)").waittime = 350
    ToolTip(lab4, "Початок активного віку.\nЗакінчується перед початком пасивного віку").waittime = 350
    ToolTip(lab5, "Початок пасивного віку.\nЗакінчується вже коли настає смерть").waittime = 350
    ToolTip(lab6, "Вірогідність смерті(в відсотках).\nЯкщо вірогідність смерті існує тоді істота може загинути\n в "
                  "будь-якому віці").waittime = 350
    ToolTip(lab7, "Кількість нащадків однієї істоти.\nМоже змінюватись в залежності "
                  "чи увімкнена рандомність").waittime = 350
    ToolTip(lab8, "Кількість істот при старті").waittime = 350


icon = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAIGNIUk0AAHomAACAhAAA+gAAAIDoAAB1MAAA6mAAAD" \
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

root = ThemedTk(theme="black")
img1 = PhotoImage(data=icon)
root.call('wm', 'iconphoto', root.w, img1)
root.geometry("+0+0")
root.config(bg="#424242")
root.title("ООП.Істоти")
root.protocol("WM_DELETE_WINDOW", DelAndQuit)
mf = ttk.LabelFrame(root, text="Головне вікно", relief=RIDGE)
ft = ttk.LabelFrame(mf, text="Параметри", relief=RIDGE, labelanchor=N)
sc1 = ttk.Scale(ft, from_=3, to=50, orient=HORIZONTAL)
sc1.set(a)
sc1.grid(row=0, column=1, padx=10, pady=4)
lab1 = ttk.Label(ft, text="Рядки", width=16)
lab1.grid(row=1, column=1, padx=10, pady=4)
sc1.bind("<Enter>", lambda e: ScaleMotion(sc1, lab1))
sc1.bind("<Leave>", lambda e: lab1.config(text="Рядки"))
sc1.config(command=lambda e: SetLines())
sc2 = ttk.Scale(ft, from_=1, to=500, orient=HORIZONTAL)
sc2.set(deathage)
sc2.grid(row=0, column=2, padx=10, pady=4)
lab2 = ttk.Label(ft, text="Тривалість життя", width=16)
lab2.grid(row=1, column=2, padx=10, pady=4)
sc2.bind("<Enter>", lambda e: ScaleMotion(sc2, lab2))
sc2.bind("<Leave>", lambda e: lab2.config(text="Тривалість життя"))
sc3 = ttk.Scale(ft, from_=100, to=5000, orient=HORIZONTAL)
sc3.set(speed)
sc3.grid(row=0, column=3, padx=10, pady=4)
lab3 = ttk.Label(ft, text="Швидкість часу(мс)", width=18)
lab3.grid(row=1, column=3, padx=10, pady=4)
sc3.bind("<Enter>", lambda e: ScaleMotion(sc3, lab3))
sc3.bind("<Leave>", lambda e: lab3.config(text="Швидкість часу(мс)"))
sc3.config(command=lambda e: ScaleMotion(sc3, lab3))
sc4 = ttk.Scale(ft, from_=1, to=deathage, orient=HORIZONTAL)
sc4.set(activeage)
sc4.grid(row=0, column=4, padx=10, pady=4)
lab4 = ttk.Label(ft, text="Активний вік", width=16)
lab4.grid(row=1, column=4, padx=10, pady=4)
sc4.bind("<Enter>", lambda e: ScaleMotion(sc4, lab4))
sc4.bind("<Leave>", lambda e: lab4.config(text="Активний вік"))
sc5 = ttk.Scale(ft, from_=activeage, to=deathage, orient=HORIZONTAL)
sc5.set(passiveage)
sc5.grid(row=0, column=5, padx=10, pady=4)
sc2.config(command=lambda e: SetLifeDuration())
sc4.config(command=lambda e: SetActiveAge())
lab5 = ttk.Label(ft, text="Пасивний вік", width=16)
lab5.grid(row=1, column=5, padx=10, pady=4)
sc5.bind("<Enter>", lambda e: ScaleMotion(sc5, lab5))
sc5.bind("<Leave>", lambda e: lab5.config(text="Пасивний вік"))
sc5.config(command=lambda e: ScaleMotion(sc5, lab5))
sc6 = ttk.Scale(ft, from_=0, to=100, orient=HORIZONTAL)
sc6.set(deathprobability)
sc6.grid(row=0, column=6, padx=10, pady=4)
lab6 = ttk.Label(ft, text="Вірогідність смерті", width=18)
lab6.grid(row=1, column=6, padx=10, pady=4)
sc6.bind("<Enter>", lambda e: ScaleMotion(sc6, lab6))
sc6.bind("<Leave>", lambda e: lab6.config(text="Вірогідність смерті"))
sc6.config(command=lambda e: ScaleMotion(sc6, lab6))
sc7 = ttk.Scale(ft, from_=1, to=20, orient=HORIZONTAL)
sc7.set(children)
sc7.grid(row=0, column=7, padx=10, pady=4)
infoscale = ttk.Label(ft)
lab7 = ttk.Label(ft, text="Кількість нащадків", width=18)
lab7.grid(row=1, column=7, padx=10, pady=4)
sc7.bind("<Enter>", lambda e: ScaleMotion(sc7, lab7))
sc7.bind("<Leave>", lambda e: lab7.config(text="Кількість нащадків"))
sc7.config(command=lambda e: ScaleMotion(sc7, lab7))
sc8 = ttk.Scale(ft, from_=1, to=11, orient=HORIZONTAL)
sc8.set(firstentities)
sc8.grid(row=0, column=8, padx=10, pady=4)
lab8 = ttk.Label(ft, text="Початкова кількість", width=19)
lab8.grid(row=1, column=8, padx=10, pady=4)
sc8.bind("<Enter>", lambda e: ScaleMotion(sc8, lab8))
sc8.bind("<Leave>", lambda e: lab8.config(text="Початкова кількість"))
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
lbr.config(yscrollcommand=sb1.set)
lbr.pack(side=LEFT, fill=Y, padx=10)
sb1.pack(side=LEFT, fill=Y)
sb1.config(command=lbr.yview)
fcb = ttk.LabelFrame(fc, text="Розмір канвасу(ширина та висота)", relief=RIDGE, labelanchor=N)
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
btn4 = ttk.Button(fc, text="Звичайний розмір канвасу", width=25, command=lambda: c.config(width=500, height=500))
btn4.pack(side=TOP, anchor=W, pady=4, padx=4)
bv5 = BooleanVar()
bv5.set(False)
cb5 = ttk.Checkbutton(fc, text="Зміна кольору", variable=bv5, onvalue=True,
                      offvalue=False)
cb5.pack(side=TOP, anchor=W, pady=4, padx=4)
cb1 = ttk.Checkbutton(fc, text="Здатність росту", variable=bv, onvalue=True,
                      offvalue=False)
cb1.pack(side=TOP, anchor=W, pady=4, padx=4)
bv3 = BooleanVar()
bv3.set(False)
cb3 = ttk.Checkbutton(fc, text="Здатність зменшуватись", variable=bv3, onvalue=True,
                      offvalue=False)
cb3.pack(side=TOP, anchor=W, pady=4, padx=4)
bv2 = BooleanVar()
bv2.set(False)
cb2 = ttk.Checkbutton(fc, text="Сітка", variable=bv2, onvalue=True, offvalue=False,
                      command=lambda: Grid(bv2.get()))
cb2.pack(side=TOP, anchor=W, pady=4, padx=4)
bv4 = BooleanVar()
bv4.set(False)
cb4 = ttk.Checkbutton(fc, text="Рандомність", variable=bv4, onvalue=True, offvalue=False)
cb4.pack(side=TOP, anchor=W, pady=4, padx=4)
pb = ttk.Progressbar(fc, value=0, length=200)
pb.pack(side=BOTTOM, pady=10)
fc.pack(fill=X, padx=6, pady=6)
fb = ttk.LabelFrame(mf, relief=FLAT)
btn2 = ttk.Button(fb, text="Старт", width=10, command=Start)
btn2.pack(side=LEFT, padx=10, pady=10)
btn3 = ttk.Button(fb, text="Стоп", width=10, command=Stop)
btn3.pack(side=LEFT, padx=10, pady=10)
btnstep = ttk.Button(fb, text="Крок", width=10, command=Step)
btnstep.pack(side=LEFT, padx=10, pady=10)
btn1 = ttk.Button(fb, text="Створити", width=10, command=Build)
btn1.pack(side=LEFT, padx=10, pady=10)
btnclear = ttk.Button(fb, text="Видалити", width=10, command=Remove)
btnclear.pack(side=LEFT, padx=10, pady=10)
btnstat = ttk.Button(fb, text="Статистика", width=10, command=ShowStatistics)
btnstat.pack(side=LEFT, padx=10, pady=10)
btn4 = ttk.Button(fb, text="Фон", command=CanvasBG)
btn4.pack(side=LEFT, padx=10, pady=10)
timer = ttk.Label(fb, text=f"Час: {time}", font=("", 14), width=12)
timer.pack(side=LEFT, padx=10, pady=10)
fb.pack(side=BOTTOM, fill="x")
mf.pack(padx=8, pady=8)
AddTooltips()
root.mainloop()
