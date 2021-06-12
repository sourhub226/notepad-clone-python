from tkinter.constants import (
    BOTH,
    BOTTOM,
    END,
    HORIZONTAL,
    LEFT,
    NONE,
    RIGHT,
    TOP,
    VERTICAL,
    W,
    WORD,
    X,
    Y,
)
import tkinter.font as tkFont
from tkinter import (
    Frame,
    IntVar,
    Label,
    Menu,
    PhotoImage,
    Scrollbar,
    Toplevel,
    scrolledtext,
    filedialog,
    ttk,
)
import os
from tkfontchooser import askfont
import webbrowser
from hdpitkinter import HdpiTk

status_color = "#f7f7f7"


class Global:
    def __init__(self):
        self.save_req = False
        self.warning_window = None
        self.about_window = None
        self.zoom = 100
        self.window_title = "Untitled - Notepad"


Global = Global()

# root=Tk()
root = HdpiTk()
root.title(Global.window_title)
root.geometry("800x500")
root.config(bg="#d3d3d3")
root.iconbitmap("notepad.ico")
root.minsize(285, 100)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()


def font_box():
    font = askfont(root)
    if font:
        font["family"] = font["family"].replace(" ", "\ ")
        font_str = "%(family)s %(size)i %(weight)s %(slant)s" % font
        if font["underline"]:
            font_str += " underline"
        if font["overstrike"]:
            font_str += " overstrike"
        print(font_str)
        text_area.configure(font=font_str)


def calc_lnWdCh():
    text = text_area.get("1.0", "end")
    text = text[:-1]

    lines = text.count("\n")
    chars = len(text.replace("\n", ""))
    words = len(text.split())

    label4.config(text=f"Lines {lines+1}, Words {words}, Chars {chars}")


# Improve this funtion
def edit(event):
    # global save_req, window_title
    text_area.after(1, func=calc_lnWdCh)

    command = None
    c = event.keysym
    s = event.state
    n = event.keysym_num
    ctrl = (s & 0x4) != 0
    # alt   = (s & 0x8) != 0 or (s & 0x80) != 0
    # shift = (s & 0x1) != 0
    # if shift:
    #     c = 'shift+' + c
    # if alt:
    #     command='alt+'
    if ctrl:
        command = "ctrl+"
        c = "ctrl+" + c

    print(c)
    print(n)
    if ((n > 0 and n < 60000) or n == 65293 or n == 65289) and (
        command != "ctrl+" or c == "ctrl+v"
    ):
        root.title(f"*{Global.window_title}")
        Global.save_req = True
        print(Global.save_req)


def check_wordwrap():
    if wordwrap_toggle.get():
        print("wr on")
        text_area.config(wrap=WORD)
        xscrollbar.pack_forget()
    else:
        print("wr off")
        text_area.config(wrap=NONE)
        text_area.pack_forget()
        xscrollbar.pack(fill=BOTH, side=BOTTOM)
        text_area.pack(fill=BOTH, expand=True, side=TOP)


def check_statusbar():
    if statusbar_toggle.get():
        print("sb on")
        text_frame.pack_forget()
        status_frame.pack(fill=X, side=BOTTOM, pady=1)
        text_frame.pack(fill=BOTH, expand=True, side=TOP)
    else:
        print("sb off")
        status_frame.pack_forget()


def destroy_about():
    # global about_window
    Global.about_window.destroy()
    Global.about_window = None


def help_box():
    # global about_window
    if Global.about_window is None:
        Global.about_window = Toplevel(root, bg=status_color)
        Global.about_window.transient(root)
        aw_width = 500
        aw_height = 350
        Global.about_window.geometry(
            "%dx%d+%d+%d"
            % (
                aw_width,
                aw_height,
                (screen_width - aw_width) / 2,
                (screen_height - aw_height) / 2 - 100,
            )
        )
        Global.about_window.resizable(0, 0)
        Global.about_window.iconbitmap("info.ico")
        Global.about_window.title("About")
        Global.about_window.focus()
        Global.about_window.protocol("WM_DELETE_WINDOW", destroy_about)
        ok_button = ttk.Button(Global.about_window, text="OK", command=destroy_about)
        img = PhotoImage(file="notepad.png").subsample(3)
        image_label = Label(Global.about_window, image=img, bg=status_color)
        image_label.image = img
        text_label = Label(
            Global.about_window,
            text="Made by Sourabh Sathe.\nCheck out my other projects on Github!",
            bg=status_color,
        )
        link_label = Label(
            Global.about_window,
            text="sourhub226\n(github.com/sourhub226)",
            fg="blue",
            cursor="hand2",
            bg=status_color,
        )
        link_label.bind(
            "<Button-1>", lambda _: webbrowser.open_new("https://github.com/sourhub226")
        )
        image_label.pack()
        ttk.Separator(Global.about_window, orient=HORIZONTAL).pack(
            fill=X, padx=20, pady=20
        )
        text_label.pack()
        link_label.pack()
        ok_button.pack(side=BOTTOM, pady=10)
    else:
        Global.about_window.focus()


def cut():
    text_area.event_generate("<<Cut>>")
    calc_lnWdCh()


def copy():
    text_area.event_generate("<<Copy>>")


def paste():
    text_area.event_generate("<<Paste>>")
    calc_lnWdCh()


def undo():
    text_area.event_generate("<<Undo>>")
    calc_lnWdCh()


def redo():
    text_area.event_generate("<<Redo>>")
    calc_lnWdCh()


def select_all():
    text_area.tag_add("sel", "1.0", "end")


def destory_warning():
    # global warning_window
    Global.warning_window.destroy()
    Global.warning_window = None


def clear_textarea():
    text_area.delete("1.0", END)
    root.title("Untitled - Notepad")


def destory_warning_clr(fopen):
    # global save_req
    destory_warning()
    clear_textarea()
    if fopen:
        open_box()
        Global.save_req = False


def prompt_save(new, fopen):
    destory_warning()
    save_file()
    if new:
        clear_textarea()
    if fopen:
        open_box()


def open_save_box(destroy, new, fopen):
    # global warning_window
    if Global.warning_window is None:
        Global.warning_window = Toplevel(root, bg="white")
        Global.warning_window.transient(root)
        ww_width = 350
        ww_height = 100
        Global.warning_window.geometry(
            "%dx%d+%d+%d"
            % (
                ww_width,
                ww_height,
                (screen_width - ww_width) / 2,
                (screen_height - ww_height) / 2 - 50,
            )
        )
        Global.warning_window.resizable(0, 0)
        Global.warning_window.iconbitmap("warning.ico")
        Global.warning_window.title("Save")
        Global.warning_window.focus()
        Global.warning_window.protocol("WM_DELETE_WINDOW", destory_warning)

        top_frame = Frame(Global.warning_window, bg="white")
        bottom_frame = Frame(Global.warning_window, bg=status_color)
        save_btn = ttk.Button(
            bottom_frame, text="Save", command=lambda: prompt_save(new, fopen)
        )
        dontsave_btn = ttk.Button(bottom_frame, text="Don't Save")
        cancel_btn = ttk.Button(bottom_frame, text="Cancel", command=destory_warning)
        save_label = Label(
            top_frame,
            text=f'Do you want to save changes to {Global.window_title.split(" ",1)[0]}?',
            font=("Segoe UI", 12),
            bg="white",
            fg="#003399",
        )

        bottom_frame.pack(fill=BOTH, side=BOTTOM, ipady=10)
        top_frame.pack(fill=BOTH)
        save_label.pack(side=LEFT, padx=5, pady=5)
        cancel_btn.pack(side=RIGHT, padx=(0, 12))
        dontsave_btn.pack(side=RIGHT, padx=(0, 12))
        save_btn.pack(side=RIGHT, padx=(0, 12))
        save_btn.focus()

        if destroy:
            dontsave_btn.config(command=root.destroy)
        else:
            dontsave_btn.config(command=lambda: destory_warning_clr(fopen))

    else:
        Global.warning_window.focus()


def exit_app():
    # global save_req
    if Global.save_req and text_area.get("1.0", "end") != "\n":
        open_save_box(True, False, False)
    else:
        root.destroy()


def zoomin():
    # global zoom
    if Global.zoom >= 500:
        return
    print("zoom")
    fontsize = fontStyle["size"]
    fontStyle.configure(size=fontsize + 1)
    Global.zoom += 10
    label3.config(text=f"{Global.zoom}%")


def zoomout():
    # global zoom
    if Global.zoom <= 10:
        return
    print("zoom down")
    fontsize = fontStyle["size"]
    fontStyle.configure(size=fontsize - 1)
    Global.zoom -= 10
    label3.config(text=f"{Global.zoom}%")


def default_zoom():
    # global zoom
    print("default zoom")
    fontsize = 11
    fontStyle.configure(size=fontsize)
    Global.zoom = 100
    label3.config(text=f"{Global.zoom}%")


def new_file():
    # global save_req
    if Global.save_req or text_area.get("1.0", "end") != "\n":
        open_save_box(False, True, False)


def save_file():
    # global save_req, window_title
    file_name = None
    if Global.save_req:
        if file_name is None:
            file_name = filedialog.asksaveasfilename(
                initialfile="*.txt",
                defaultextension=".txt",
                filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")],
            )

            if file_name == "":
                file_name = None
            else:
                with open(file_name, "w") as file:
                    file.write(text_area.get(1.0, END))
                Global.window_title = os.path.basename(file_name) + " - Notepad"
                root.title(Global.window_title)
                Global.save_req = False
        else:
            with open(file_name, "w") as file:
                file.write(text_area.get(1.0, END))
            Global.save_req = False


def open_box():
    # global window_title, save_req
    file = filedialog.askopenfilename(
        defaultextension=".txt",
        filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")],
    )
    if file == "":
        file = None
    else:
        Global.window_title = os.path.basename(file) + " - Notepad"
        root.title(Global.window_title)
        text_area.delete(1.0, END)
        with open(file, "r") as file:
            text_area.insert(1.0, file.read())
        Global.save_req = False


def open_file():
    # global save_req
    if Global.save_req and text_area.get("1.0", "end") != "\n":
        open_save_box(False, False, True)
    else:
        open_box()


menubar = Menu(root)
file_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open...", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_app)

edit_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Undo", command=undo)
edit_menu.add_command(label="Redo", command=redo)
edit_menu.add_separator()
edit_menu.add_command(label="Cut", command=cut)
edit_menu.add_command(label="Copy", command=copy)
edit_menu.add_command(label="Paste", command=paste)
edit_menu.add_separator()
edit_menu.add_command(label="Select All", command=select_all)

format_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Format", menu=format_menu)
wordwrap_toggle = IntVar()
wordwrap_toggle.set(1)
format_menu.add_checkbutton(
    label="Word Wrap", var=wordwrap_toggle, command=check_wordwrap
)
format_menu.add_command(label="Font", command=font_box)

view_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="View", menu=view_menu)
statusbar_toggle = IntVar()
statusbar_toggle.set(1)
zoom_menu = Menu(view_menu, tearoff=0)
view_menu.add_cascade(label="Zoom", menu=zoom_menu)
zoom_menu.add_command(label="{:39}".format("Zoom In") + "Ctrl+Plus", command=zoomin)
zoom_menu.add_command(label="{:37}".format("Zoom Out") + "Ctrl+Minus", command=zoomout)
zoom_menu.add_command(
    label="{:29}".format("Restore Default Zoom") + "Ctrl+0", command=default_zoom
)
view_menu.add_checkbutton(
    label="Status Bar", var=statusbar_toggle, command=check_statusbar
)

help_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About Notepad", command=help_box)

fontStyle = tkFont.Font(family="consolas", size=11)

text_frame = Frame(root, bg="white")
xscrollbar = Scrollbar(text_frame, orient=HORIZONTAL)
text_area = scrolledtext.ScrolledText(
    text_frame,
    relief="solid",
    bd=0,
    font=fontStyle,
    wrap=WORD,
    xscrollcommand=xscrollbar.set,
    undo=True,
)
text_area.focus()
xscrollbar.config(command=text_area.xview)


status_frame = Frame(root, bg=status_color, relief="flat", borderwidth=2)
label1 = Label(status_frame, text="UTF-8", bg=status_color, width=15, anchor=W)
label1.pack(fill=BOTH, side=RIGHT, padx=5)
ttk.Separator(status_frame, orient=VERTICAL).pack(fill=Y, side=RIGHT)
label2 = Label(status_frame, text="Windows (CRLF)", bg=status_color, width=14, anchor=W)
label2.pack(fill=BOTH, side=RIGHT, padx=5)
ttk.Separator(status_frame, orient=VERTICAL).pack(fill=Y, side=RIGHT)
label3 = Label(status_frame, text=f"{Global.zoom}%", bg=status_color, anchor=W)
label3.pack(fill=BOTH, side=RIGHT, padx=5)
ttk.Separator(status_frame, orient=VERTICAL).pack(fill=Y, side=RIGHT)
label4 = Label(
    status_frame, text="Lines 0, Words 0, Chars 0", bg=status_color, width=22, anchor=W
)
label4.pack(fill=BOTH, side=RIGHT, padx=5)
ttk.Separator(status_frame, orient=VERTICAL).pack(fill=Y, side=RIGHT)

status_frame.pack(fill=X, side=BOTTOM, pady=1)
text_frame.pack(fill=BOTH, expand=True, side=TOP)
text_area.pack(fill=BOTH, expand=True, side=TOP, padx=(5, 0))

text_area.bind("<Key>", edit)
text_area.bind("<Control-equal>", lambda _: zoomin())
text_area.bind("<Control-minus>", lambda _: zoomout())
text_area.bind("<Control-0>", lambda _: default_zoom())
text_area.bind("<Control-s>", lambda _: save_file())
text_area.bind("<Control-n>", lambda _: new_file())
text_area.bind("<Control-o>", lambda _: open_file())
root.protocol("WM_DELETE_WINDOW", exit_app)
root.config(menu=menubar)
root.mainloop()
