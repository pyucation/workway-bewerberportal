import streamlit as st
import requests
import base64
import io


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
    search_query = st.text_input("Enter search query:")
    if st.button("Search"):
        # Example of sending a search query to your backend
        response = requests.get(f"{API_BASE_URL}/applicants/search", params={"query": search_query})
        if response.status_code == 200:
            applicants = response.json()
            for applicant in applicants:
                col1, col2 = st.columns([1, 4])
                with col1:
                    if applicant['img_encoded']:
                        # Decode the base64 image
                        # img_data = base64.b64decode(applicant['img_encoded'])
                        img_data = applicant['img_encoded']
                        st.image(img_data, width=100)
                with col2:
                    # Use a button for each applicant to make it clickable
                    if st.button(applicant['name'], key=applicant['_id']):
                        # Save the selected applicant's ID to session_state
                        st.session_state.selected_applicant_id = applicant['_id']
                        # Redirect to the detailed view
                        st.rerun()
        else:
            st.error("Failed to fetch applicants.")

def display_applicant_details(applicant):
    # Assuming 'applicant' is a dictionary with the applicant's details
    name = applicant.get("name", "N/A")
    email = applicant.get("email", "N/A")
    cv_encoded = applicant.get("cv_encoded")
    img_encoded = applicant.get("img_encoded")

    st.write(f"Name: {name}")
    st.write(f"Email: {email}")

    if img_encoded:
        # Decode the base64 string
        # img_data = base64.b64decode(img_encoded)
        img_data = img_encoded
        # Convert to a format that st.image can display
        img_file = io.BytesIO(img_data)
        st.image(img_file, caption="Applicant Image")

    if cv_encoded:
        # Decode the base64 string
        # cv_data = base64.b64decode(cv_encoded)
        cv_data = cv_encoded
        # Convert to a format suitable for st.download_button
        cv_file = io.BytesIO(cv_data)
        st.download_button(
            label="Download CV",
            data=cv_file,
            file_name=f"{name}_CV.pdf",  # You might want to dynamically determine the file extension
            mime="application/octet-stream"  # Use the appropriate MIME type
        )



def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ("Add New Applicant", "Search Applicants", "Applicant Details"))

    if page == "Add New Applicant":
        add_applicant()
    elif page == "Search Applicants":
        search_applicants()
        if 'selected_applicant_id' in st.session_state:
            # If an applicant has been selected, automatically switch to the details view
            page = "Applicant Details"
            st.sidebar.radio("Go to", ("Add New Applicant", "Search Applicants", "Applicant Details"), index=2)

    if page == "Applicant Details" and 'selected_applicant_id' in st.session_state:
        display_applicant_details(st.session_state.selected_applicant_id)


if __name__ == "__main__":
    main()
