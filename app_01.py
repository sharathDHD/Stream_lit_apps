import streamlit as st
import io
import zipfile
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileManager:
    def __init__(self, data=None, uploaded_file=None):
        """
        Initialize the FileManager with data or an uploaded file.
        """
        self.data = data
        self.uploaded_file = uploaded_file
        self.files = {}
        self.in_memory_zip = None

    def read_data(self):
        """
        Read the data from either the uploaded file or the provided data.
        """
        try:
            if self.uploaded_file:
                data = self.uploaded_file.read().decode('utf-8')
                logging.info("Data read from uploaded file.")
                return data
            logging.info("Data read from text area.")
            return self.data
        except Exception as e:
            logging.error(f"Error reading data: {e}")
            st.error("Error reading data")
            return ""

    def parse_data(self, raw_data):
        """
        Parse the raw data into individual files.
        """
        lines = raw_data.splitlines()
        current_file_name = ""
        current_file_content = ""

        for line in lines:
            if line.startswith("### File:"):
                if current_file_name:
                    self.files[current_file_name] = current_file_content
                current_file_name = line.split("`")[1]
                current_file_content = ""
            else:
                current_file_content += line + "\n"
        
        if current_file_name:
            self.files[current_file_name] = current_file_content
        logging.info("Data parsed into files.")

    def get_file_list(self):
        """
        Get the list of file names parsed from the data.
        """
        return list(self.files.keys())

    def get_file_types(self):
        """
        Get the list of unique file types from the parsed files.
        """
        return list(set([file_name.split('.')[-1] for file_name in self.files]))

    def create_zip_in_memory(self, selected_files):
        """
        Create a zip file in memory containing the selected files.
        """
        try:
            self.in_memory_zip = io.BytesIO()
            with zipfile.ZipFile(self.in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_name in selected_files:
                    zipf.writestr(file_name, self.files[file_name])
            self.in_memory_zip.seek(0)
            logging.info("Zip file created in memory.")
        except Exception as e:
            logging.error(f"Error creating zip file: {e}")
            st.error("Error creating zip file")

def display_file_options(file_manager):
    """
    Display options for selecting files to include in the zip.
    """
    file_types = file_manager.get_file_types()
    file_list = file_manager.get_file_list()
    st.write(f"Files that can be created: {file_list}")

    # Select all files checkbox
    selected_files = file_list if st.checkbox('Select All Files') else []

    # Select files by type checkboxes
    for file_type in file_types:
        if st.checkbox(f'Select all .{file_type} files'):
            selected_files.extend([file_name for file_name in file_list if file_name.endswith(f'.{file_type}')])

    selected_files = list(set(selected_files))  # Remove duplicates
    selected_files_display = st.multiselect('Or select individual files:', file_list, default=selected_files)
    return selected_files_display
def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("File Creator from Data")

    # User inputs: text area for data and file uploader
    data = st.text_area("Paste your data here:", height=300)
    uploaded_file = st.file_uploader("...or choose a file to upload", type=['txt', 'md'])

    if data or uploaded_file:
        # Initialize FileManager and process the data
        file_manager = FileManager(data, uploaded_file)
        raw_data = file_manager.read_data()
        if raw_data:
            file_manager.parse_data(raw_data)
            selected_files_display = display_file_options(file_manager)

            # Input for custom zip file name
            zip_file_name = st.text_input('Enter a name for the zip file (optional):')
            if zip_file_name:
                if not zip_file_name.lower().endswith('.zip'):
                    zip_file_name += '.zip'
            else:
                zip_file_name = f'generated_zip_{int(time.time())}.zip'

            if selected_files_display:
                file_manager.create_zip_in_memory(selected_files_display)
                st.download_button(
                    label="Download Zip File",
                    data=file_manager.in_memory_zip,
                    file_name=zip_file_name,
                    mime="application/zip"
                )

if __name__ == "__main__":
    main()
