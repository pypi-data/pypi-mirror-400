#! /usr/bin/env python

import json
import os
import re
from tkinter import filedialog, CENTER, END, LEFT, RIGHT, X, Y, BOTH, YES, HORIZONTAL, TOP, messagebox

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from qmenta.core import platform
from qmenta.core.auth import Needs2FAError
from qmenta.sdk.tool_maker.make_files import raise_if_false

FONT = "Consolas"
FONTSIZE = 10

MIN = 0
MAX_CORES = 10
MAX_RAM = 16

dir_name = None


def gui_tkinter():
    def browse_folder():
        global dir_name
        dir_name = filedialog.askdirectory()
        write_dir.set(dir_name)
        tool_id_entry.delete(0, END)
        tool_id_entry.insert(0, os.path.basename(dir_name))

        # checking version
        version_file = os.path.join(dir_name, "version")
        with open(version_file) as fv:
            version_ = fv.read()
        tool_version_entry.delete(0, END)
        tool_version_entry.insert(0, version_)
        image_name_entry.delete(0, END)
        image_name_entry.insert(0, os.path.basename(dir_name) + f":{version_}")

    def generate_output_object():
        values = {
            "qmenta_user": user_id_entry.get(),
            "qmenta_password": password_entry.get(),
            "code": tool_id_entry.get(),
            "version": tool_version_entry.get(),
            "name": tool_name_entry.get(),
            "cores": num_cores_entry.get(),
            "memory": memory_entry.get(),
            "image_name": image_name_entry.get(),
            "docker_url": docker_url_entry.get(),
            "docker_user": docker_user_entry.get(),
            "docker_password": docker_password_entry.get(),
        }
        return values

    def perform_selection_check(values):
        try:
            raise_if_false(
                isinstance(values["code"], str), "Tool ID must be a string."
            )
            raise_if_false(values["code"] != "", "Tool ID must be defined.")
            raise_if_false(
                " " not in values["code"], "Tool ID can't have spaces."
            )
            values["code"] = values["code"].lower()  # must be lowercase
            values["short_name"] = (
                values["code"].lower().replace(" ", "_")
            )  # must be lowercase

            raise_if_false(
                isinstance(values["name"], str), "Tool name must be a string."
            )
            raise_if_false(values["name"] != "", "Tool name must be defined.")

            raise_if_false(
                values["version"] != "", "Tool version must be defined."
            )
            raise_if_false(
                re.search(r"^(\d+\.)?(\d+\.)?(\*|\d+)$", values["version"]),
                "Version format not valid.",
            )

            raise_if_false(values["cores"], "Number of cores must be defined.")
            raise_if_false(
                values["cores"].isnumeric(),
                "Number of cores must be an integer.",
            )
            raise_if_false(
                MAX_CORES >= int(values["cores"]) > MIN,
                f"Number of cores must be between {MIN} and {MAX_CORES}.",
            )

            raise_if_false(values["memory"], "RAM must be defined.")
            raise_if_false(
                values["memory"].isnumeric(), "RAM must be an integer."
            )
            raise_if_false(
                MAX_RAM >= int(values["memory"]) > MIN,
                f"RAM must be {MIN} and {MAX_RAM}.",
            )
            values["memory"] = int(values["memory"])
            values["image_name"] = (
                values["image_name"]
                or values["code"] + ":" + values["version"]
            )
            return values
        except AssertionError as e:
            messagebox.showerror("Error", f"AN EXCEPTION OCCURRED! {e}")
            return False

    # window
    window = ttk.Window(themename="darkly")
    window.resizable(True, True)
    window.title("Tool Publishing GUI")
    window.geometry("600x800")

    write_dir = ttk.StringVar()

    # --- SCROLLBAR & CANVAS SETUP ---

    # Main container to hold canvas and scrollbar
    main_container = ttk.Frame(window)
    main_container.pack(fill=BOTH, expand=YES)
    # Canvas
    canvas = ttk.Canvas(main_container)
    # Scrollbar linked to canvas
    vbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vbar.set)

    vbar.pack(side=RIGHT, fill=Y)
    canvas.pack(side=LEFT, fill=BOTH, expand=YES)

    # The actual frame that holds the content
    content_frame = ttk.Frame(canvas, padding=20)
    canvas_window_id = canvas.create_window((0, 0), window=content_frame, anchor="nw", tags="inner_frame")

    # --- RESIZE LOGIC ---

    # Update scrollregion when content changes size
    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    content_frame.bind("<Configure>", configure_scroll_region)

    # Force the inner frame to match the canvas width (Horizontal Fill)
    def on_canvas_resize(event):
        canvas.itemconfig(canvas_window_id, width=event.width)

    canvas.bind("<Configure>", on_canvas_resize)

    def _on_mousewheel_windows(event):
        # Windows/macOS: event.delta is usually multiples of 120
        # We divide by 120 to get the number of "steps"
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_linux_scroll_up(event):
        # Linux (X11) often sends Button-4 for scroll up
        canvas.yview_scroll(-1, "units")

    def _on_linux_scroll_down(event):
        # Linux (X11) often sends Button-5 for scroll down
        canvas.yview_scroll(1, "units")

    # Bind Standard MouseWheel (Windows/macOS)
    window.bind_all("<MouseWheel>", _on_mousewheel_windows)
    # Bind Linux specific buttons (X11)
    window.bind_all("<Button-4>", _on_linux_scroll_up)
    window.bind_all("<Button-5>", _on_linux_scroll_down)

    # --- WIDGETS ---

    # Logo Image
    try:
        # Adjusted path logic for safety
        img_path = os.path.join(os.path.dirname(__file__), "templates_tool_maker", "qmenta.png")
        if os.path.exists(img_path):
            logo = Image.open(img_path).resize((500, 110))
            img = ImageTk.PhotoImage(logo)
            image_label = ttk.Label(master=content_frame, image=img, anchor=CENTER)
            image_label.image = img  # Keep reference
            image_label.pack(side=TOP, pady=(0, 20))
    except Exception as e:
        print(f"Image load failed: {e}")

    # Title
    ttk.Label(
        master=content_frame,
        text="QMENTA Platform credentials",
        font="Helvetica 16 bold",
    ).pack(pady=10)

    ttk.Label(
        master=content_frame,
        text="(*) indicates mandatory field.",
        bootstyle="warning"
    ).pack(pady=(0, 20))

    # Helper to create rows easily
    def create_row(parent, label_text, is_password=False, default=None):
        frame = ttk.Frame(master=parent)
        frame.pack(fill=X, pady=5)

        lbl = ttk.Label(master=frame, text=label_text, width=30)
        lbl.pack(side=LEFT)

        entry = ttk.Entry(master=frame, show="*" if is_password else None)
        if default:
            entry.insert(0, str(default))
        entry.pack(side=LEFT, fill=X, expand=YES, padx=10)
        return entry

    # User inputs
    user_id_entry = create_row(content_frame, "Username*")
    password_entry = create_row(content_frame, "Password*", is_password=True)

    # Browse Folder Row
    folder_frame = ttk.Frame(master=content_frame)
    folder_frame.pack(fill=X, pady=10)
    ttk.Label(folder_frame, text="Select tool folder*", width=30).pack(side=LEFT)
    ttk.Button(folder_frame, text="Browse Folder", command=browse_folder).pack(side=LEFT, padx=10)
    ttk.Label(folder_frame, textvariable=write_dir).pack(side=LEFT, padx=10)

    # Tool info
    tool_id_entry = create_row(content_frame, "Specify the tool ID.*")
    tool_version_entry = create_row(content_frame, "Specify the tool version.*")
    tool_name_entry = create_row(content_frame, "Specify the tool name.*")
    num_cores_entry = create_row(content_frame, f"Cores required (integer, max {MAX_CORES})", default="1")
    memory_entry = create_row(content_frame, f"RAM required GB (integer, max {MAX_RAM})", default="1")
    image_name_entry = create_row(content_frame, "Docker image name")

    # Separator
    ttk.Separator(content_frame, orient=HORIZONTAL).pack(fill=X, pady=20)

    # Docker registry
    ttk.Label(
        master=content_frame,
        text="Docker Registry Credentials",
        font="Helvetica 12 bold"
    ).pack(pady=10)
    docker_url_entry = create_row(content_frame, "Docker registry URL", default="hub.docker.com")
    docker_user_entry = create_row(content_frame, "Docker registry user")
    docker_password_entry = create_row(content_frame, "Docker registry password*", is_password=True)

    # --- ACTIONS ---

    gui_content = {}

    def submit_form():
        gui_content.update(generate_output_object())
        gui_content.update(perform_selection_check(gui_content))
        if gui_content:
            window.destroy()

    action_frame = ttk.Frame(master=content_frame)
    action_frame.pack(pady=30)
    ttk.Button(
        master=action_frame,
        text="Publish in QMENTA Platform",
        command=submit_form,
        bootstyle="primary",
    ).pack(side=LEFT, pady=10)

    def quit_tool_creator():
        window.destroy()
        print("GUI closed.")
        exit()

    ttk.Button(
        action_frame,
        text="Quit",
        command=quit_tool_creator,
        bootstyle="danger",
    ).pack(side=LEFT, padx=10)

    # run
    window.mainloop()
    return gui_content


def main():
    content_build = gui_tkinter()
    if not content_build:
        exit()
    os.chdir(dir_name)

    user = content_build["qmenta_user"]
    password = content_build["qmenta_password"]
    try:
        auth = platform.Auth.login(
            username=user,
            password=password,
            base_url="https://platform.qmenta.com",
            ask_for_2fa_input=False,
        )
    except Needs2FAError as needs2faerror:
        messagebox.showinfo(
            "Message",
            str(needs2faerror)
            + " Please check the terminal to add the code sent to your phone.",
        )
        auth = platform.Auth.login(
            username=user,
            password=password,
            base_url="https://platform.qmenta.com",
            code_2fa=input("Input 2-FA code:"),
        )

    # Get information from the advanced options file.
    advanced_options = "settings.json"
    raise_if_false(
        os.path.exists(advanced_options),
        "Settings do not exist! Run the local test to create it.",
    )
    with open(advanced_options) as fr:
        content_build["advanced_options"] = fr.read()

    # Get information from the description file.
    with open("description.html") as fr:
        content_build["description"] = fr.read()

    with open("results_configuration.json", "r") as file:
        results_config = json.load(file)
    # The screen value is expected as a string with escaped chars (dict)
    results_config["screen"] = json.dumps(results_config["screen"])
    content_build["results_configuration"] = json.dumps(
        results_config
    ).replace("{}", "")

    content_build.update(
        {
            "start_condition_code": "output={'OK': True, 'code': 1}",
            "entry_point": "/root/entrypoint.sh",
            "tool_path": "tool:run",
        }
    )

    # After creating the workflow, the ID of the workflow must be requested
    # and added to the previous dictionary
    # otherwise it will keep creating new workflows on the platform
    # creating conflicts.
    res = platform.post(
        auth, "analysis_manager/upsert_user_tool", data=content_build
    )

    if res.json()["success"] == 1:
        print("Tool updated successfully!")
        print(
            "Tool name:",
            content_build["name"],
            "(",
            content_build["code"],
            ":",
            content_build["version"],
            ")",
        )
    else:
        print("ERROR setting the tool.")
        print(res.json())


if __name__ == "__main__":
    main()
