if st.session_state.page == 'welcome':
    # This creates a layout where the middle column is wide (6 units) for a BIG logo
    col1, col2, col3 = st.columns([0.5, 3, 0.5]) 
    
    with col2:
        if os.path.exists('logo.png'):
            # use_container_width=True makes it fill the large middle column
            st.image('logo.png', use_container_width=True)
        else:
            # Fallback if file is missing - helps you debug!
            st.markdown("<h1 style='text-align:center; font-size:100px;'>🎮</h1>", unsafe_allow_html=True)
            st.warning("Logo file 'logo.png' not found in the directory.")
    
    st.markdown("<h1 style='text-align: center; color: white; font-size: 3em;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: white; font-size: 22px; font-weight: bold; opacity: 0.9;'>Win to get to leadership board</p>", unsafe_allow_html=True)
    
    # Extra space before the button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("GET STARTED"): 
        st.session_state.page = 'register'
        st.rerun()
