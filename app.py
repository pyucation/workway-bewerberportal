import streamlit as st
import requests


API_BASE_URL = "http://localhost:5000"

def add_applicant():
    st.header("Add New Applicant")
    with st.form("add_applicant_form"):
        # Text inputs for simple string fields
        name = st.text_input("Name")
        email = st.text_input("Email")
        birthday = st.text_input("Birthday (DD-MM-YYYY)")
        origin = st.text_input("Origin")
        company = st.text_input("Company (optional)", "")
        special_field = st.text_input("Special Field")

        # Text inputs for lists, assuming comma-separated values
        languages = st.text_input("Languages (comma-separated)")
        tools = st.text_input("Tools (comma-separated)")

        # File uploaders for CV and image, optional
        cv_file = st.file_uploader("Upload CV (optional)", type=['pdf', 'doc', 'docx'])
        img_file = st.file_uploader("Upload Image (optional)", type=['jpg', 'png', 'jpeg'])

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            files = {}
            applicant_data = {
                "name": name,
                "email": email,
                "birthday": birthday,
                "origin": origin,
                "company": company or None,  # Treat empty string as None
                "special_field": special_field,
                "languages": languages.split(",") if languages else [],
                "tools": tools.split(",") if tools else []
            }

            # Here you would handle the file uploads separately.
            # This example does not include the process of uploading files to the server.
            if cv_file is not None:
                # Read the file and prepare for upload
                files["cv_file"] = (cv_file.name, cv_file.getvalue(), cv_file.type)
            if img_file is not None:
                # Read the file and prepare for upload
                files["image_file"] = (img_file.name, img_file.getvalue(), img_file.type)
            
            response = requests.post(f"{API_BASE_URL}/applicant", data=applicant_data, files=files)
            if response.status_code == 201:
                st.success("Applicant added successfully!")
            else:
                st.error(f"Failed to add applicant: {response.json().get('error')}")


def search_applicants():
    st.header("Search Applicants")
    search_field = st.selectbox("Select a field to search by:", options=["tools", "name", "languages", "special_field"])
    search_query = st.text_input(f"Enter {search_field} to search for:")

    if st.button("Search"):
        response = requests.get(f"{API_BASE_URL}/applicants/search", params={"query_field": search_field, "query_value": search_query})
        if response.status_code == 200:
            applicants = response.json()
            if applicants:
                for applicant in applicants:
                    tools = ', '.join(applicant.get('tools', []))
                    languages = ', '.join(applicant.get('languages', []))
                    st.write(f"Name: {applicant['name']}, Email: {applicant['email']}, Tools: {tools}, Languages: {languages}, Special Field: {applicant.get('special_field', 'N/A')}")
            else:
                st.write("No applicants found.")
        else:
            st.error(f"Failed to search applicants: {response.json().get('error')}")


def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ("Add New Applicant", "Search Applicants"))

    if page == "Add New Applicant":
        add_applicant()
    elif page == "Search Applicants":
        search_applicants()


if __name__ == "__main__":
    main()
