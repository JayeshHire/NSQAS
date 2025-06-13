import streamlit as st


if st.button("sign in"):

    if not st.user.is_logged_in:
        st.login("google")
    else:
        st.write(f"Hello, {st.user.name}")
        
if st.user is None:
    st.write("user not logged in")

st.write(f"login status: {st.user.is_logged_in}")
# if st.button("logout"):
#     st.logout()
#     st.write("logging out the user")

# if st.user:
#     st.write(f"{st.user.to_dict()}")

