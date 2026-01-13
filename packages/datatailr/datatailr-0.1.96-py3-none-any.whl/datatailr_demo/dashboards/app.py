##########################################################################
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
##########################################################################

import streamlit as st


def main():
    # Title of the app
    st.title("Minimal Streamlit App")

    # Input from the user
    name = st.text_input("Enter your name:")

    # Display a message
    if name:
        st.write(f"Hello, {name}!")


if __name__ == "__main__":
    main()
