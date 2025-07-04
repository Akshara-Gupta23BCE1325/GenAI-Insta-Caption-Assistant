import streamlit as st
from caption_utils import caption_from_text, caption_from_image, suggest_hashtags

st.set_page_config(
    page_title="✨ Creative Caption Generator",
    page_icon="💫",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stTextInput input, .stFileUploader button {
        border-radius: 10px !important;
        padding: 10px !important;
    }
    .stButton button {
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 25px !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #FF4B4B !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✨ Creative Caption Generator")
st.markdown("Upload an image or describe your post to get **unique, creative captions** and **perfect hashtags** that will make your content stand out!")

# Split into two columns for better layout
col1, col2 = st.columns([1, 1])

with col1:
    option = st.radio(
        "How would you like to generate your caption?",
        ["📷 From Image", "✏️ From Text"],
        horizontal=True
    )

    if option == "📷 From Image":
        image_file = st.file_uploader(
            "Upload your image",
            type=["jpg", "jpeg", "png"],
            help="For best results, use clear, high-quality images"
        )
        if image_file and st.button("✨ Generate Magic!"):
            with st.spinner("Creating something amazing for you..."):
                caption = caption_from_image(image_file)
                hashtags, keywords = suggest_hashtags(caption)
                st.session_state.caption = caption
                st.session_state.hashtags = hashtags
                st.session_state.keywords = keywords
                st.session_state.image = image_file

    elif option == "✏️ From Text":
        user_input = st.text_area(
            "Describe your post or paste some text",
            height=150,
            placeholder="e.g., 'Just had the most amazing sunset dinner at the beach with friends...'"
        )
        if user_input and st.button("✨ Generate Magic!"):
            with st.spinner("Crafting the perfect caption..."):
                caption = caption_from_text(user_input)
                hashtags, keywords = suggest_hashtags(caption)
                st.session_state.caption = caption
                st.session_state.hashtags = hashtags
                st.session_state.keywords = keywords
                st.session_state.image = None

with col2:
    if "caption" in st.session_state:
        st.subheader("🎨 Your Creative Caption")
        st.success(st.session_state.caption)
        
        if st.session_state.image:
            st.image(st.session_state.image, use_column_width=True)
        
        st.subheader("🔍 Keywords Detected")
        st.write(", ".join([f"**{kw}**" for kw in st.session_state.keywords]))
        
        st.subheader("🏷️ Hashtag Suggestions")
        st.info(" ".join(st.session_state.hashtags))
        
        st.subheader("📋 Post Preview")
        st.write(st.session_state.caption)
        st.caption(" ".join(st.session_state.hashtags))
        
        # Copy to clipboard button
        full_post = f"{st.session_state.caption}\n\n{' '.join(st.session_state.hashtags)}"
        st.download_button(
            label="📋 Copy Post to Clipboard",
            data=full_post,
            file_name="instagram_post.txt",
            mime="text/plain"
        )