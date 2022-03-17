import tkinter
from tkinter import Tk, Button, Label, Entry, constants
from tkinter import filedialog as fd
import bundletool_bridge
from threading import Thread

build_btn = None
unSignedAPKRadio = None
signedAPKRadio = None
isSignedAPK = None
alias_btn = None
keystore_alias_input = None
keystore_pass_input = None
keystore_path_input = None
keystore_file_btn = None
aab_path_input = None
output_label = None
build_install_btn = None
aab_file_btn = None
root = None


def try_fetch_alias():
    alias = bundletool_bridge.get_alias_name(keystore_path_input.get(), keystore_pass_input.get())
    if alias is not None:
        print('Alias found: ' + alias)
        keystore_alias_input.delete(0, constants.END)
        keystore_alias_input.insert(0, alias)
    else:
        print('Alias not found!! Please verify keystore path and password or enter alias manually')


def select_aab_file():
    filetypes = (
        ('aab', '*.aab'),
        ('All files', '*.*')
    )

    aab_path = fd.askopenfilename(
        title='Select .aab file',
        initialdir='/',
        filetypes=filetypes)
    if aab_path and len(aab_path) != 0:
        aab_path_input.delete(0, constants.END)
        aab_path_input.insert(0, aab_path)
        print(f'AAB path: {aab_path}')


def select_keystore_file():
    filetypes = (
        ('Keystore', '*.keystore *.jks'),
        ('All files', '*.*')
    )

    keystore_path = fd.askopenfilename(
        title='Select keystore file',
        initialdir='/',
        filetypes=filetypes)
    if keystore_path and len(keystore_path) != 0:
        keystore_path_input.delete(0, constants.END)
        keystore_path_input.insert(0, keystore_path)
        print(f'Keystore path: {keystore_path}')


def toggle_inputs_state(state):
    if state:
        build_install_btn["state"] = "normal"
        build_btn["state"] = "normal"
        aab_file_btn["state"] = "normal"
        aab_path_input["state"] = "normal"
    else:
        build_install_btn["state"] = "disabled"
        build_btn["state"] = "disabled"
        aab_file_btn["state"] = "disabled"
        aab_path_input["state"] = "disabled"

    toggle_keystore_options_state(state)


def signed_apk_radio_changed():
    if isSignedAPK.get():
        print("Custom keystore is selected")
    else:
        print("Debug keystore is selected")
    toggle_keystore_options_state(isSignedAPK.get())


def toggle_keystore_options_state(state):
    if isSignedAPK.get():
        if state:
            keystore_file_btn["state"] = "normal"
            alias_btn["state"] = "normal"
            keystore_path_input["state"] = "normal"
            keystore_alias_input["state"] = "normal"
            keystore_pass_input["state"] = "normal"
        else:
            keystore_file_btn["state"] = "disabled"
            alias_btn["state"] = "disabled"
            keystore_path_input["state"] = "disabled"
            keystore_pass_input["state"] = "disabled"
            keystore_alias_input["state"] = "disabled"
    else:
        keystore_file_btn["state"] = "disabled"
        alias_btn["state"] = "disabled"
        keystore_path_input["state"] = "disabled"
        keystore_pass_input["state"] = "disabled"
        keystore_alias_input["state"] = "disabled"


def schedule_check(t):
    root.after(1000, check_if_done, t)


def check_if_done(t):
    if not t.is_alive():
        toggle_inputs_state(True)
        signedAPKRadio["state"] = "normal"
        unSignedAPKRadio["state"] = "normal"

    else:
        schedule_check(t)


def build_pressed(install):
    if aab_path_input.get().strip() == "":
        print("Please select AAB file to be converted.")
        return

    toggle_inputs_state(False)
    signedAPKRadio["state"] = "disabled"
    unSignedAPKRadio["state"] = "disabled"

    if isSignedAPK.get():
        t = Thread(
            target=lambda: bundletool_bridge.convert_and_install(aab_path=aab_path_input.get().strip(),
                                                                 keystore_path=keystore_path_input.get().strip(),
                                                                 keystore_pass=keystore_pass_input.get().strip(),
                                                                 keystore_alias=keystore_alias_input.get().strip(),
                                                                 install=install,
                                                                 open_in_explorer=open_in_explorer.get()))
    else:
        t = Thread(
            target=lambda: bundletool_bridge.convert_and_install(aab_path=aab_path_input.get().strip(),
                                                                 install=install, open_in_explorer=open_in_explorer.get()))
    t.start()
    schedule_check(t)


# ====================================
# EXECUTION STARTS HERE
# ====================================


root = Tk()

root.title("")
root.geometry('550x290')
root.resizable(False, False)

col = 0
row = 0

# Title
# col+=1
title = Label(root, text="AAB 2 APK Converter", font=("Arial", 15))
title.grid(row=row, column=col, columnspan=6, sticky=constants.NSEW, pady=(15, 20))

row += 1
col = 0
# AAB Filepath
aab_path_label = Label(root, text="AAB Path")
aab_path_label.grid(row=row, column=col, sticky=constants.W, padx=5)
col += 1

aab_path_input = Entry(root)
aab_path_input.grid(row=row, column=col, columnspan=4, sticky=constants.EW)
col += 4

aab_file_btn = Button(
    root,
    text='Select .AAB File',
    command=select_aab_file
)
aab_file_btn.grid(row=row, column=col, sticky=constants.NSEW, padx=10)

row += 1
col = 0
# Radio buttons for Signed Apk

isSignedAPK = tkinter.BooleanVar(root)
isSignedAPK.set(False)

unSignedAPKRadio = tkinter.Radiobutton(root, text="Debug keystore", variable=isSignedAPK,
                                       value=False, command=signed_apk_radio_changed)
unSignedAPKRadio.grid(row=row, column=col, sticky=constants.W, pady=5, padx=(5, 0))
col += 1
signedAPKRadio = tkinter.Radiobutton(root, text="Custom keystore", variable=isSignedAPK,
                                     value=True,
                                     command=signed_apk_radio_changed)
signedAPKRadio.grid(row=row, column=col, sticky=constants.W)
if isSignedAPK.get():
    signedAPKRadio.select()
else:
    unSignedAPKRadio.select()

row += 1
col = 0
# Keystore Filepath
keystore_path_label = Label(root, text="Keystore Path")
keystore_path_label.grid(row=row, column=col, sticky=constants.W, padx=5)
col += 1

keystore_path_input = Entry(root)
keystore_path_input.grid(row=row, column=col, columnspan=4, sticky=constants.EW)
col += 4

keystore_file_btn = Button(
    root,
    text='Select Keystore File',
    command=select_keystore_file
)
keystore_file_btn.grid(row=row, column=col, sticky=constants.NSEW, padx=10)

row += 1
col = 0
# Keystore password
keystore_pass_label = Label(root, text="Keystore Password")
keystore_pass_label.grid(row=row, column=col, sticky=constants.W, padx=5)
col += 1
keystore_pass_input = Entry(root)
keystore_pass_input.grid(row=row, column=col, columnspan=4, sticky=constants.EW)

row += 1
col = 0
# Keystore alias entry
keystore_alias_label = Label(root, text="Keystore Alias")
keystore_alias_label.grid(row=row, column=col, sticky=constants.W, padx=5)
col += 1

keystore_alias_input = Entry(root)
keystore_alias_input.grid(row=row, column=col, columnspan=4, sticky=constants.EW)
col += 4

# Fetch alias name Button
alias_btn = Button(
    root,
    text='Try Fetch Alias',
    command=lambda: try_fetch_alias()
)
alias_btn.grid(row=row, column=col, sticky=constants.NSEW, padx=10)

row += 1
col = 0
# Build Button
col += 1
build_btn = Button(
    root,
    text='Convert',
    command=lambda: build_pressed(False)
)
build_btn.grid(row=row, column=col, pady=(15, 5), columnspan=2, padx=10, sticky=constants.NSEW)
col += 2

build_install_btn = Button(
    root,
    text='Convert and Install',
    command=lambda: build_pressed(True)
)

build_install_btn.grid(row=row, column=col, pady=(15, 5), columnspan=2, padx=10, sticky=constants.NSEW)

row += 1
col = 0
note_label = Label(root, text="Note:", font='Arial 8 bold')
note_label.grid(row=row, column=col, sticky=constants.W, padx=5)

col += 5
open_in_explorer = tkinter.BooleanVar(value=True)
open_in_explorer_CB = tkinter.Checkbutton(root, text="Open in Explorer", variable=open_in_explorer, onvalue=True,
                                          offvalue=False)
open_in_explorer_CB.grid(row=row, column=col, sticky=constants.NSEW)

row += 1
col = 0
note_label = Label(root,
                   text="• Check console for logs and errors.",
                   font='Arial 8')
note_label.grid(row=row, column=col, sticky=constants.W, padx=5, columnspan=4)

toggle_keystore_options_state(isSignedAPK.get())

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)
root.columnconfigure(4, weight=1)
root.columnconfigure(5, weight=1)
root.mainloop()
