import asyncio
import tkinter
from sqlalchemy import select
from database import database_engine,Resources
from tkinter import ttk
from extract_backup_copy import extract_backup_copy
from tkinter import filedialog
from async_tkinter_loop import async_mainloop,async_handler
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession
async_session=async_sessionmaker(database_engine,class_=AsyncSession,expire_on_commit=False)
def simple_choice(tree,event):
    clicked_row=tree.identify_row(event.y)
    if clicked_row:
        if clicked_row in tree.selection():
            tree.selection_remove(clicked_row)
        else:
            tree.selection_add(clicked_row)
async def find_selection():
    selected_resources = data_table.selection()
    if not selected_resources:
        return
    askdirectory_title=('Select a directory to restore the resource' if len(selected_resources)==1 else 'Select a directory for restoring resources')
    selected_directory=await asyncio.to_thread(filedialog.askdirectory,title=askdirectory_title)
    if selected_directory:
        await asyncio.gather(*[extract_backup_copy(resource_uuid=resource,directory_unloading=selected_directory) for resource in selected_resources])

async def getting_resource_data():
    async with async_session() as session:
        resource_data = (await session.execute(select(Resources))).scalars().all()
        for data in resource_data:
            data_table.insert('','end',iid=data.uuid,values=(data.name,data.size,data.data_delete))
window = tkinter.Tk()
window.title('OsmiumSmartestBackupper')
window.configure(bg='white')
window.state('zoomed')
bar_menu = tkinter.Menu(window)
bar_menu.add_command(label='Restore',command=async_handler(find_selection))
window.config(menu=bar_menu)
data_table = ttk.Treeview(window,columns=('Name','Size','Data Delete'),show='headings',selectmode='none')
data_table.bind('<ButtonRelease-1>',lambda event:simple_choice(data_table,event))
data_table.column('Name',width=100,stretch=False)
data_table.column('Size',width=50,stretch=False)
data_table.column('Data Delete',width=10)
data_table.heading('Name', text='Name')
data_table.heading('Size', text='Size')
data_table.heading('Data Delete', text='Data Delete')
data_table.pack(fill='both',expand=True,padx=10,pady=10)
if __name__=='__main__':
    window.after(0,lambda:async_handler(getting_resource_data)())
    async_mainloop(window)