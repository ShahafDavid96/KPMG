# app.py
import streamlit as st
import json
from form_extractor import process_form
from validator import validate_extracted_data
import logging

st.set_page_config(layout="wide")

st.title("National Insurance Institute forms extraction and validation")
st.markdown("""
This application uses a configuration-driven approach for data extraction and performs both **completeness** and **rule-based accuracy** validation.
""")

# --- Enhanced File Upload Interface ---
st.sidebar.header("📁 File Upload")
st.markdown("""
<style>
.upload-area {
    border: 2px dashed #ccc;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    background-color: #f9f9f9;
    transition: all 0.3s ease;
}
.upload-area:hover {
    border-color: #007bff;
    background-color: #f0f8ff;
}
.upload-area.dragover {
    border-color: #28a745;
    background-color: #d4edda;
}
</style>
""", unsafe_allow_html=True)

# Drag and drop area
upload_area = st.container()
with upload_area:
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "📤 Drag & Drop or Click to Upload",
        type=["pdf", "jpg", "jpeg", "png"],
        help="Upload a PDF or image of the Bituach Leumi form",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main Logic ---
if uploaded_file is not None:
    st.success(f"✅ File uploaded: `{uploaded_file.name}`")
    
    # File preview
    if uploaded_file.type in ["image/jpeg", "image/png"]:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    elif uploaded_file.type == "application/pdf":
        st.info("📄 PDF file uploaded - processing will begin automatically")

    # Processing with enhanced error handling
    try:
        with st.spinner("🔍 Analyzing document, detecting language, and extracting data..."):
            detected_language, extracted_json_str = process_form(uploaded_file)
        
        st.success("✅ Analysis complete!")
        st.info(f"**Detected Language:** {detected_language.capitalize()}")

        # Display results in columns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📝 Extracted JSON Data")
            try:
                # Get validation results first to apply fixes
                with st.spinner("🔍 Validating and correcting data..."):
                    validation_results = validate_extracted_data(extracted_json_str)
                
                # Apply language mapping for Hebrew forms after validation
                if detected_language.lower() == "hebrew":
                    # **FIXED: No need for language mapping - keys are always in English**
                    # Just check if we need to apply validation fixes
                    if validation_results.get("corrected_data"):
                        st.json(validation_results["corrected_data"])
                        st.info("✅ **Data has been automatically corrected and validated**")
                    else:
                        parsed_json = json.loads(extracted_json_str)
                        st.json(parsed_json)
                        st.info("✅ **Data extracted successfully**")
                else:
                    # English form - show as is
                    if validation_results.get("corrected_data"):
                        st.json(validation_results["corrected_data"])
                        st.info("✅ **Data has been automatically corrected and validated**")
                    else:
                        parsed_json = json.loads(extracted_json_str)
                        st.json(parsed_json)
                    
            except json.JSONDecodeError as e:
                st.error("❌ Failed to parse the response from OpenAI as JSON.")
                st.text(extracted_json_str[:500] + "..." if len(extracted_json_str) > 500 else extracted_json_str)

        with col2:
            st.subheader("📊 Validation Results")
            
            if not validation_results["is_valid_schema"]:
                st.error("❌ Validation failed: The data does not conform to the required schema.")
                st.error("Schema validation failed.")
            else:
                st.success("✅ Data schema is valid.")
                
                # Display Metrics
                metric1, metric2 = st.columns(2)
                metric1.metric(
                    label="Completeness Score",
                    value=f"{validation_results['completeness_score']:.1f}%",
                    help="The percentage of fields that contain a value."
                )
                metric2.metric(
                    label="Accuracy Score",
                    value=f"{validation_results['accuracy_score']:.1f}%",
                    help="The percentage of specific format rules that passed."
                )
                
                # Display Accuracy Details
                st.write("---")
                st.write("**Accuracy Rule Details:**")
                
                details = validation_results.get("accuracy_details", {})
                detailed_results = validation_results.get("accuracy_details_detailed", {})
                
                if not details:
                    st.warning("⚠️ No accuracy checks were performed.")
                else:
                    for check_name, is_passed in details.items():
                        if check_name in detailed_results:
                            detailed = detailed_results[check_name]
                            
                            if is_passed:
                                # Show passed validation - just "Passed" with no extra details
                                st.success(f"✅ **{check_name}** - Passed")
                            else:
                                # Show failed validation with specific violations
                                st.error(f"❌ **{check_name}** - Failed")
                                
                                # Show the specific violations
                                violations = detailed.get("violations", [])
                                if violations:
                                    st.write("**Violations:**")
                                    for violation in violations:
                                        st.write(f"• {violation}")
                                
                                # Show additional details if available
                                if detailed.get("details"):
                                    st.info(f"Details: {detailed['details']}")
                        else:
                            # Fallback for old format
                            icon = "✅" if is_passed else "❌"
                            color = "green" if is_passed else "red"
                            st.markdown(f"- {icon} **{check_name}:** <span style='color: {color}'>{'Passed' if is_passed else 'Failed'}</span>", unsafe_allow_html=True)

    except Exception as e:
        st.error("❌ An error occurred during processing!")
        st.error("Please check your configuration and try again.")
        st.info("💡 **Common Solutions:**\n"
               "• Check if your Azure services are running\n"
               "• Verify your API keys are correct\n"
               "• Ensure the uploaded file is readable\n"
               "• Try with a different file format")

else:
    st.info("📁 Please upload a file using the drag & drop area above to begin.")
    
    # Show sample form structure
    with st.expander("📋 Expected Form Structure"):
        st.markdown("""
        **Bituach Leumi Form 283** should contain:
        - Personal Information (Name, ID, Gender, Birth Date)
        - Contact Details (Address, Phone Numbers)
        - Accident Information (Date, Time, Location, Description)
        - Medical Details (Injured Body Part, Medical Diagnoses)
        """)
        
        st.info("💡 **Tips for Better Results:**\n"
               "• Use clear, high-quality scans\n"
               "• Ensure all text is readable\n"
               "• Avoid shadows or glare on the document\n"
               "• PDF format generally works best")