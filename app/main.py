import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.components import render_header
from backend.services.memory_service import MemoryService
import os

# Initialize session state for memory service
@st.cache_resource
def init_memory_service():
    """Initialize unified memory service"""
    return MemoryService(
        text_persist_dir='data/chroma_text',
        image_persist_dir='data/chroma_image'
    )

def render_home():
    """Render home page"""
    st.title("Memory Map")
    st.write("Welcome to your personal memory mapping application!")

    st.markdown("""
    ### Features
    - **Add Memories**: Store text and image memories with metadata
    - **Search Memories**: Find memories using natural language queries
    - **View All Memories**: Browse all your stored memories

    Use the sidebar to navigate between different features.
    """)

    # Show statistics
    service = init_memory_service()
    stats = service.get_memory_stats()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Memories", stats.total_count)
    with col2:
        st.metric("Text Memories", stats.text_count)
    with col3:
        st.metric("Image Memories", stats.image_count)

def render_add_text_memory():
    """Render page to add text memories"""
    st.header("Add Text Memory")

    service = init_memory_service()

    # Text input
    memory_text = st.text_area("Enter your memory:", height=150)

    # Metadata inputs
    with st.expander("Add Metadata (Optional)"):
        title = st.text_input("Title")
        tags = st.text_input("Tags (comma-separated)")
        description = st.text_area("Description")

    if st.button("Save Text Memory"):
        if memory_text:
            try:
                service.add_text_memory(
                    text=memory_text,
                    title=title or None,
                    tags=tags or None,
                    description=description or None
                )
                st.success("Text memory saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving memory: {str(e)}")
        else:
            st.warning("Please enter some text for your memory.")

def render_add_image_memory():
    """Render page to add image memories"""
    st.header("Add Image Memory")

    service = init_memory_service()

    # File upload
    uploaded_file = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg', 'webp'])

    # Metadata inputs
    with st.expander("Add Metadata (Optional)"):
        title = st.text_input("Title")
        tags = st.text_input("Tags (comma-separated)")
        description = st.text_area("Description")

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Preview", use_container_width=True)

        if st.button("Save Image Memory"):
            # Save uploaded file temporarily
            temp_dir = "data/temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, uploaded_file.name)

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                service.add_image_memory(
                    image_path=temp_path,
                    title=title or None,
                    tags=tags or None,
                    description=description or None
                )
                st.success("Image memory saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving memory: {str(e)}")

def render_search_memories():
    """Render page to search memories"""
    st.header("Search Memories")

    service = init_memory_service()

    query = st.text_input("Enter your search query:")
    n_results = st.slider("Number of results", min_value=1, max_value=10, value=5)

    if st.button("Search") and query:
        try:
            with st.spinner("Searching..."):
                search_result = service.search_memories(query, n_results=n_results)

            if search_result.count > 0:
                st.success(f"Found {search_result.count} results")

                for i, result in enumerate(search_result.memories, 1):
                    with st.expander(f"Result {i} - Distance: {result.get('distance', 'N/A'):.4f}"):
                        metadata = result.get('metadata', {})

                        # Display type
                        memory_type = metadata.get('type', 'unknown')
                        st.write(f"**Type:** {memory_type}")

                        # Display metadata
                        if metadata.get('title'):
                            st.write(f"**Title:** {metadata['title']}")
                        if metadata.get('tags'):
                            st.write(f"**Tags:** {metadata['tags']}")
                        if metadata.get('description'):
                            st.write(f"**Description:** {metadata['description']}")

                        # Display content
                        if memory_type == 'text':
                            st.text_area("Text:", value=metadata.get('text', ''), height=100, key=f"text_{i}")
                        elif memory_type == 'image':
                            image_path = metadata.get('source', '')
                            if os.path.exists(image_path):
                                st.image(image_path, use_container_width=True)
                            else:
                                st.warning(f"Image not found: {image_path}")
            else:
                st.info("No results found.")
        except Exception as e:
            st.error(f"Error searching: {str(e)}")

def render_view_all_memories():
    """Render page to view all memories"""
    st.header("All Memories")

    service = init_memory_service()

    tab1, tab2 = st.tabs(["Text Memories", "Image Memories"])

    with tab1:
        try:
            text_memories = service.get_text_memories()
            if text_memories:
                for i, memory in enumerate(text_memories, 1):
                    metadata = memory.get('metadata', {})
                    with st.expander(f"Text Memory {i} - {metadata.get('title', 'Untitled')}"):
                        if metadata.get('title'):
                            st.write(f"**Title:** {metadata['title']}")
                        if metadata.get('tags'):
                            st.write(f"**Tags:** {metadata['tags']}")
                        if metadata.get('description'):
                            st.write(f"**Description:** {metadata['description']}")
                        st.text_area("Content:", value=metadata.get('text', ''), height=100, key=f"all_text_{i}")
            else:
                st.info("No text memories found.")
        except Exception as e:
            st.error(f"Error loading text memories: {str(e)}")

    with tab2:
        try:
            image_memories = service.get_image_memories()
            if image_memories:
                cols = st.columns(2)
                for i, memory in enumerate(image_memories):
                    metadata = memory.get('metadata', {})
                    col = cols[i % 2]
                    with col:
                        with st.container():
                            image_path = metadata.get('source', '')
                            if os.path.exists(image_path):
                                st.image(image_path, use_container_width=True)
                            if metadata.get('title'):
                                st.write(f"**{metadata['title']}**")
                            if metadata.get('description'):
                                st.write(metadata['description'])
                            if metadata.get('tags'):
                                st.caption(f"Tags: {metadata['tags']}")
                            st.divider()
            else:
                st.info("No image memories found.")
        except Exception as e:
            st.error(f"Error loading image memories: {str(e)}")

def main():
    st.set_page_config(
        page_title="Memory Map",
        page_icon="🗺️",
        layout="wide"
    )

    render_header()

    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        if st.button("Home", use_container_width=True):
            st.session_state.page = 'Home'
        if st.button("Add Text Memory", use_container_width=True):
            st.session_state.page = 'Add Text Memory'
        if st.button("Add Image Memory", use_container_width=True):
            st.session_state.page = 'Add Image Memory'
        if st.button("Search Memories", use_container_width=True):
            st.session_state.page = 'Search Memories'
        if st.button("View All Memories", use_container_width=True):
            st.session_state.page = 'View All Memories'

    # Render selected page
    if st.session_state.page == 'Home':
        render_home()
    elif st.session_state.page == 'Add Text Memory':
        render_add_text_memory()
    elif st.session_state.page == 'Add Image Memory':
        render_add_image_memory()
    elif st.session_state.page == 'Search Memories':
        render_search_memories()
    elif st.session_state.page == 'View All Memories':
        render_view_all_memories()

if __name__ == "__main__":
    main()
