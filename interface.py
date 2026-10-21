import asyncio
import tkinter
from tkinter import filedialog
from tkinter import ttk

from async_tkinter_loop import async_handler
from async_tkinter_loop import async_mainloop
from sqlalchemy import select

from database import Resource
from restore import restore_backup
from config import async_session


def toggle_selection(
    tree: ttk.Treeview,
    event: tkinter.Event,
) -> None:
    clicked_row = tree.identify_row(event.y)

    if not clicked_row:
        return

    if clicked_row in tree.selection():
        tree.selection_remove(clicked_row)
    else:
        tree.selection_add(clicked_row)

async def restore_selected_resources(treeview):
    selected_resources = treeview.selection()

    if not selected_resources:
        return

    if len(selected_resources) == 1:
        dialog_title = (
            "Select a directory to restore the resource"
        )
    else:
        dialog_title = (
            "Select a directory for restoring resources"
        )

    selected_directory = filedialog.askdirectory(title=dialog_title)

    if not selected_directory:
        return

    await asyncio.gather(
        *(
            restore_backup(
                resource_uuid=resource_uuid,
                destination_directory=selected_directory,
            )
            for resource_uuid in selected_resources
        )
    )

    treeview.delete(*selected_resources)



async def load_resource_data(treeview):
    async with async_session() as session:
        result = await session.execute(
            select(Resource)
        )

        resources = result.scalars().all()

        for resource in resources:
            treeview.insert(
                "",
                "end",
                iid=resource.uuid,
                values=(
                    resource.name,
                    resource.size,
                    resource.deleted_at,
                ),
            )

def run_interface():
    window = tkinter.Tk()

    window.title("OsmiumSmartestBackupper")
    window.configure(bg="white")
    window.state("zoomed")

    data_table = ttk.Treeview(
        window,
        columns=("Name", "Size", "Deleted At"),
        show="headings",
        selectmode="none",
    )

    data_table.bind(
        "<ButtonRelease-1>",
        lambda event: toggle_selection(
            data_table,
            event,
        ),
    )

    data_table.column(
        "Name",
        width=100,
        stretch=True,
    )

    data_table.column(
        "Size",
        width=50,
        stretch=False,
    )

    data_table.column(
        "Deleted At",
        width=150,
    )

    data_table.heading(
        "Name",
        text="Name",
    )

    data_table.heading(
        "Size",
        text="Size",
    )

    data_table.heading(
        "Deleted At",
        text="Deleted At",
    )

    data_table.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10,
    )

    menu_bar = tkinter.Menu(window)

    menu_bar.add_command(
        label="Restore",
        command=async_handler(
            restore_selected_resources,data_table
        )
    )


    window.config(menu=menu_bar)

    window.after(
        0,
        async_handler(
            load_resource_data,treeview=data_table
            ),
    )


    async_mainloop(window)