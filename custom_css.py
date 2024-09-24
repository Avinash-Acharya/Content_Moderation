# Custom CSS to enforce dark theme with white text
DARK_THEME_CSS = """
* {
    color: #ffffff !important;
    background-color: #0B0F19 !important;
}
img {
    filter: brightness(0.8) !important;  /* Ensure images are not too bright */
}
a {
    color: #bb86fc !important;
}
"""