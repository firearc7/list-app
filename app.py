import streamlit as st
import database as db

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_list_id' not in st.session_state:
    st.session_state.selected_list_id = None
if 'editing_item_id' not in st.session_state:
    st.session_state.editing_item_id = None
if 'editing_list_id' not in st.session_state: # For editing list title/note
    st.session_state.editing_list_id = None


def show_home_page():
    st.title("My Lists")

    # Search bar
    search_query = st.text_input("Search lists by title or note", key="search_lists_input")
    
    if st.button("Create New List", key="create_new_list_btn_home"):
        st.session_state.page = 'create_list'
        st.session_state.editing_list_id = None # Ensure not in edit mode
        st.rerun()

    st.markdown("---")
    
    if search_query:
        lists = db.search_lists(search_query)
        if not lists:
            st.info(f"No lists found matching '{search_query}'.")
    else:
        lists = db.get_all_lists()
        if not lists:
            st.info("No lists yet. Click 'Create New List' to get started!")

    for lst in lists:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button(f"{lst['title']}", key=f"view_list_{lst['id']}", use_container_width=True):
                    st.session_state.selected_list_id = lst['id']
                    st.session_state.page = 'view_list'
                    st.session_state.editing_item_id = None
                    st.session_state.editing_list_id = None
                    st.rerun()
                if lst['note']:
                    st.caption(f"Note: {lst['note'][:50]}{'...' if len(lst['note']) > 50 else ''}")
            with col2:
                if st.button("Edit Info", key=f"edit_list_info_{lst['id']}", type="secondary"):
                    st.session_state.editing_list_id = lst['id']
                    st.session_state.page = 'create_list' # Reuse create_list page for editing
                    st.rerun()
            with col3:
                if st.button("Delete List", key=f"delete_list_{lst['id']}", type="primary"):
                    db.delete_list(lst['id'])
                    st.success(f"List '{lst['title']}' deleted.")
                    st.rerun()
            st.markdown("---")


def show_create_list_page():
    is_editing = st.session_state.editing_list_id is not None
    page_title = "Edit List Details" if is_editing else "Create New List"
    button_label = "Save Changes" if is_editing else "Create List"
    
    st.header(page_title)

    list_data = None
    if is_editing:
        list_data = db.get_list_by_id(st.session_state.editing_list_id)
        if not list_data:
            st.error("List not found for editing.")
            st.session_state.page = 'home'
            st.rerun()
            return

    default_title = list_data['title'] if list_data else ""
    default_note = list_data['note'] if list_data else ""

    with st.form(key="list_form"):
        title = st.text_input("List Title", value=default_title)
        note = st.text_area("List Note (Optional)", value=default_note)
        submit_button = st.form_submit_button(label=button_label)

        if submit_button:
            if not title:
                st.error("Title is required.")
            else:
                if is_editing:
                    db.update_list_details(st.session_state.editing_list_id, title, note)
                    st.success(f"List '{title}' updated successfully!")
                    st.session_state.selected_list_id = st.session_state.editing_list_id
                    st.session_state.page = 'view_list'
                else:
                    new_list_id = db.create_list(title, note)
                    st.success(f"List '{title}' created successfully!")
                    st.session_state.selected_list_id = new_list_id
                    st.session_state.page = 'view_list' # Go to the new list
                
                st.session_state.editing_list_id = None
                st.rerun()

    if st.button("Back to Home", key="back_home_from_create_list"):
        st.session_state.page = 'home'
        st.session_state.editing_list_id = None
        st.rerun()


def show_list_details_page():
    list_id = st.session_state.selected_list_id
    if list_id is None:
        st.error("No list selected.")
        st.session_state.page = 'home'
        st.rerun()
        return

    current_list = db.get_list_by_id(list_id)
    if not current_list:
        st.error("List not found.")
        st.session_state.page = 'home'
        st.rerun()
        return

    st.header(f"List: {current_list['title']}")
    if current_list['note']:
        st.markdown(f"**Note:** {current_list['note']}")
    
    st.markdown("---")

    # Add new item form
    st.subheader("Add New Item")
    with st.form(key="add_item_form", clear_on_submit=True):
        item_name = st.text_input("Name", key="new_item_name")
        item_address = st.text_input("Address (Optional)", key="new_item_address")
        item_notes = st.text_area("Notes (Optional)", key="new_item_notes")
        add_item_submit = st.form_submit_button("Add Item")

        if add_item_submit:
            if item_name:
                db.add_item_to_list(list_id, item_name, item_address, item_notes)
                st.success(f"Item '{item_name}' added.")
                st.rerun() # Rerun to refresh the list of items
            else:
                st.error("Item name is required.")
    
    st.markdown("---")
    st.subheader("Items in this List")
    items = db.get_items_for_list(list_id)

    if not items:
        st.info("No items in this list yet. Add some using the form above.")
    else:
        for item in items:
            item_id = item['id']
            
            if st.session_state.editing_item_id == item_id:
                with st.form(key=f"edit_item_form_{item_id}"):
                    st.markdown(f"**Editing Item: {item['name']}**")
                    edited_name = st.text_input("Name", value=item['name'], key=f"edit_name_{item_id}")
                    edited_address = st.text_input("Address", value=item['address'], key=f"edit_address_{item_id}")
                    edited_notes = st.text_area("Notes", value=item['notes'], key=f"edit_notes_{item_id}")
                    
                    col_save, col_cancel, _ = st.columns([1,1,3])
                    with col_save:
                        if st.form_submit_button("Save", use_container_width=True):
                            if edited_name:
                                db.update_list_item(item_id, edited_name, edited_address, edited_notes)
                                st.success(f"Item '{edited_name}' updated.")
                                st.session_state.editing_item_id = None
                                st.rerun()
                            else:
                                st.error("Item name cannot be empty.")
                    with col_cancel:
                        if st.form_submit_button("Cancel", type="secondary", use_container_width=True):
                            st.session_state.editing_item_id = None
                            st.rerun()
            else:
                with st.container(border=True):
                    st.markdown(f"**{item['name']}**")
                    if item['address']:
                        st.markdown(f"*Address:* {item['address']}")
                    if item['notes']:
                        st.caption(f"*Notes:* {item['notes']}")
                    
                    col1, col2, _ = st.columns([1, 1, 3])
                    with col1:
                        if st.button("Edit Item", key=f"edit_item_{item_id}", type="secondary", use_container_width=True):
                            st.session_state.editing_item_id = item_id
                            st.rerun()
                    with col2:
                        if st.button("Delete Item", key=f"delete_item_{item_id}", type="primary", use_container_width=True):
                            db.delete_list_item(item_id)
                            st.success(f"Item '{item['name']}' deleted.")
                            st.session_state.editing_item_id = None # Ensure not in edit mode
                            st.rerun()
            st.markdown("---")


    if st.button("Back to All Lists", key="back_home_from_view_list"):
        st.session_state.page = 'home'
        st.session_state.selected_list_id = None
        st.session_state.editing_item_id = None
        st.session_state.editing_list_id = None
        st.rerun()

# Main app logic
def main():
    st.set_page_config(page_title="List App", layout="centered")
    db.init_db() # Ensure DB is initialized

    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'create_list':
        show_create_list_page()
    elif st.session_state.page == 'view_list':
        show_list_details_page()

if __name__ == "__main__":
    main()
