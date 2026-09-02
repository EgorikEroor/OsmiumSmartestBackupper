import tkinter
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from database import database_engine,Resources
from tkinter import ttk
from extract_backup_copy import extract_backup_copy
from tkinter import filedialog
def simple_choice(tree,event):
    clicked_row=tree.identify_row(event.y)
    if clicked_row:
        if clicked_row in tree.selection():
            tree.selection_remove(clicked_row)
        else:
            tree.selection_add(clicked_row)
def find_selection():
    selected_resources = data_table.selection()
    if len(selected_resources) != 0:
        if len(selected_resources)==1:
            selected_directory=filedialog.askdirectory(title='Select a directory to restore the resource')
        else:
            selected_directory=filedialog.askdirectory(title='Select a directory for restoring resources')
        if selected_directory:
            for resource in selected_resources:
                extract_backup_copy(resource_uuid=resource,resource_unloading=selected_directory)
        else:
            return
window = tkinter.Tk()
window.title('OsmiumSmartestBackupper')
window.configure(bg='white')
window.state('zoomed')
bar_menu = tkinter.Menu(window)
bar_menu.add_command(label='Restore', command=find_selection)
window.config(menu=bar_menu)
data_table = ttk.Treeview(window,columns=('Name','Size','Data Delete'),show='headings',selectmode='none')
data_table.bind('<ButtonRelease-1>',lambda event:simple_choice(tree=data_table,event=event))
data_table.column('Name',width=100,stretch=False)
data_table.column('Size',width=50,stretch=False)
data_table.column('Data Delete',width=10)
data_table.heading('Name', text='Name')
data_table.heading('Size', text='Size')
data_table.heading('Data Delete', text='Data Delete')
data_table.pack(fill='both',expand=True,padx=10,pady=10)
with sessionmaker(bind=database_engine)() as session:
    database_data = session.execute(select(Resources)).scalars().all()
    for data in database_data:
        data_table.insert('','end',iid=data.uuid,values=(data.name,data.size,data.data_delete))
window.mainloop()