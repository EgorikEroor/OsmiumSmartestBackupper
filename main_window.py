"""Tkinter window for browsing and restoring backed-up resources."""

import asyncio
import tkinter
from tkinter import filedialog, ttk

from async_tkinter_loop import async_handler, async_mainloop
from sqlalchemy import select

from backup_restorer import restore_backup
from database import BackedUpResource, session_factory


def toggle_row_selection(tree: ttk.Treeview, event: tkinter.Event) -> None:
    """Toggle the selection of the row under the mouse cursor."""
    clicked_row = tree.identify_row(event.y)

    if not clicked_row:
        return

    if clicked_row in tree.selection():
        tree.selection_remove(clicked_row)
    else:
        tree.selection_add(clicked_row)


async def restore_selected_resources(resources_table: ttk.Treeview) -> None:
    """Restore all selected resources into a user-chosen directory."""
    selected_uuids = resources_table.selection()

    if not selected_uuids:
        return

    if len(selected_uuids) == 1:
        dialog_title = "Select a directory to restore the resource"
    else:
        dialog_title = "Select a directory for restoring resources"

    destination_directory = filedialog.askdirectory(title=dialog_title)

    if not destination_directory:
        return

    await asyncio.gather(
        *(
            restore_backup(
                resource_uuid=resource_uuid,
                destination_directory=destination_directory,
            )
            for resource_uuid in selected_uuids
        )
    )

    resources_table.delete(*selected_uuids)


async def load_resources_into_table(resources_table: ttk.Treeview) -> None:
    """Fill the table with all backed-up resources from the database."""
    async with session_factory() as session:
        result = await session.execute(select(BackedUpResource))
        backed_up_resources = result.scalars().all()

    for backed_up_resource in backed_up_resources:
        resources_table.insert(
            "",
            "end",
            iid=backed_up_resource.backup_uuid,
            values=(
                backed_up_resource.resource_name,
                backed_up_resource.formatted_size,
                backed_up_resource.deleted_at,
            ),
        )


def run_main_window() -> None:
    """Create and run the main application window."""
    window = tkinter.Tk()
    window.title("OsmiumSmartestBackupper")
    window.configure(bg="white")
    window.state("zoomed")

    resources_table = ttk.Treeview(
        window,
        columns=("Name", "Size", "Deleted At"),
        show="headings",
        selectmode="none",
    )
    resources_table.bind(
        "<ButtonRelease-1>",
        lambda event: toggle_row_selection(resources_table, event),
    )

    resources_table.column("Name", width=100, stretch=True)
    resources_table.column("Size", width=50, stretch=False)
    resources_table.column("Deleted At", width=150)

    resources_table.heading("Name", text="Name")
    resources_table.heading("Size", text="Size")
    resources_table.heading("Deleted At", text="Deleted At")

    resources_table.pack(fill="both", expand=True, padx=10, pady=10)

    menu_bar = tkinter.Menu(window)
    menu_bar.add_command(
        label="Restore",
        command=async_handler(restore_selected_resources, resources_table),
    )
    window.config(menu=menu_bar)

    window.after(
        0,
        async_handler(load_resources_into_table, resources_table),
    )

    async_mainloop(window)