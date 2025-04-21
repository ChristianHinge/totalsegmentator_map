# Import necessary libraries
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import datetime

def generate_pdf_report(data: dict) -> bytes:
    """
    Generates a PDF report displaying organ volumes from a dictionary.

    Args:
        data: A dictionary where keys are organ names and values are
              dictionaries containing at least a 'volume' key (in mm³).
              Example:
              {
                  "spleen": {"volume": 377109.0, "intensity": 92.77547},
                  "liver": {"volume": 1500000.0, "intensity": 105.0}
              }

    Returns:
        bytes: The generated PDF report as bytes.
               Returns None if the input data is invalid or empty.
    """
    if not isinstance(data, dict) or not data:
        print("Error: Input data must be a non-empty dictionary.")
        return None

    # Create a buffer to hold the PDF data
    buffer = BytesIO()

    # Create the PDF document
    # Using letter page size and setting margins
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            leftMargin=1*inch, rightMargin=1*inch,
                            topMargin=1*inch, bottomMargin=1*inch)

    # Styles for paragraphs and table
    styles = getSampleStyleSheet()
    title_style = styles['h1']
    normal_style = styles['Normal']
    normal_style.alignment = 1 # Center alignment for table content

    # Story list to hold the elements of the PDF
    story = []

    # --- Title ---
    report_title = "Organ Volume Report"
    story.append(Paragraph(report_title, title_style))
    story.append(Spacer(1, 0.2*inch)) # Add space after title

    # --- Date ---
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    story.append(Paragraph(f"Report generated on: {current_date}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch)) # Add space after date

    # --- Table Data ---
    # Prepare table data header
    table_data = [['Organ', 'Volume (cm³)']]

    # Populate table data from the input dictionary
    valid_entries = 0
    for organ, details in data.items():
        if isinstance(details, dict) and 'volume' in details:
            try:
                # Convert volume from mm³ to cm³ and format
                volume_mm3 = float(details['volume'])
                volume_cm3 = volume_mm3 / 1000.0
                # Format to 2 decimal places
                formatted_volume = f"{volume_cm3:.2f}"
                table_data.append([organ.capitalize(), formatted_volume])
                valid_entries += 1
            except (ValueError, TypeError):
                print(f"Warning: Invalid volume data for organ '{organ}'. Skipping.")
                table_data.append([organ.capitalize(), "Invalid Data"])
        else:
             print(f"Warning: Missing or invalid volume data for organ '{organ}'. Skipping.")
             table_data.append([organ.capitalize(), "Missing Data"])

    if valid_entries == 0 and len(data) > 0:
         print("Error: No valid volume data found in the input dictionary.")
         # Add a message to the PDF instead of an empty table
         story.append(Paragraph("No valid organ volume data available to display.", normal_style))
         doc.build(story)
         buffer.seek(0)
         return buffer.getvalue()
    elif valid_entries == 0:
        # Handle case where input dictionary was empty initially
         story.append(Paragraph("Input data was empty.", normal_style))
         doc.build(story)
         buffer.seek(0)
         return buffer.getvalue()


    # --- Create Table ---
    # Calculate available width for the table
    page_width, page_height = letter
    available_width = page_width - doc.leftMargin - doc.rightMargin

    # Set column widths (adjust as needed)
    col_widths = [available_width * 0.4, available_width * 0.6] # 40% for organ, 60% for volume

    # Create the table object
    organ_table = Table(table_data, colWidths=col_widths)

    # --- Table Style ---
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey), # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), # Center alignment for all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), # Header font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12), # Header padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige), # Body background
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black), # Body text color
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'), # Body font
        ('GRID', (0, 0), (-1, -1), 1, colors.black), # Grid lines
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])
    organ_table.setStyle(table_style)

    # Add table to the story
    story.append(organ_table)
    story.append(Spacer(1, 0.5*inch)) # Add space after table

    # --- Footer (Optional) ---
    # You could add a footer here if needed
    # story.append(Paragraph("--- End of Report ---", normal_style))

    # --- Build the PDF ---
    try:
        doc.build(story)
    except Exception as e:
        print(f"Error building PDF: {e}")
        return None

    # Get the PDF data from the buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes

# --- Example Usage ---
if __name__ == "__main__":
    # Sample input data (similar to TotalSegmentator output structure)
    segmentation_data = {
        "spleen": {"volume": 377109.0, "intensity": 92.77547},
        "kidney_right": {"volume": 185342.5, "intensity": 101.5},
        "kidney_left": {"volume": 192588.1, "intensity": 100.8},
        "gallbladder": {"volume": 45012.3, "intensity": 75.2},
        "liver": {"volume": 1650234.7, "intensity": 110.1},
        "stomach": {"volume": 210455.0, "intensity": 60.9},
        "pancreas": {"volume": 98765.4, "intensity": 105.3},
        "adrenal_gland_right": {"volume": 5123.4, "intensity": 120.0},
        "adrenal_gland_left": {"volume": 5589.1, "intensity": 118.5},
        "lung_upper_lobe_left": {"volume": 450123.6, "intensity": -600.0},
        "lung_lower_lobe_left": {"volume": 510345.8, "intensity": -610.5},
        "lung_upper_lobe_right": {"volume": 480789.2, "intensity": -595.0},
        "lung_middle_lobe_right": {"volume": 210567.1, "intensity": -580.3},
        "lung_lower_lobe_right": {"volume": 530987.4, "intensity": -615.2},
        "invalid_organ": {"intensity": 100.0}, # Missing volume
        "another_invalid": "not a dictionary", # Invalid structure
        "empty_details": {} # Empty details dictionary
    }

    # Generate the PDF report
    pdf_output = generate_pdf_report(segmentation_data)

    # Save the generated PDF to a file (optional)
    if pdf_output:
        output_filename = "organ_volume_report.pdf"
        try:
            with open(output_filename, "wb") as f:
                f.write(pdf_output)
            print(f"Successfully generated report and saved as '{output_filename}'")
        except IOError as e:
            print(f"Error saving PDF file: {e}")
    else:
        print("Failed to generate PDF report.")

    # Example with empty data
    print("\nTesting with empty data:")
    pdf_output_empty = generate_pdf_report({})
    if not pdf_output_empty:
         print("Correctly handled empty input data.")

    # Example with only invalid data
    print("\nTesting with only invalid data:")
    invalid_data_only = {
        "invalid_organ_1": {"intensity": 100.0},
        "invalid_organ_2": "string data"
    }
    pdf_output_invalid = generate_pdf_report(invalid_data_only)
    if pdf_output_invalid:
        output_filename_invalid = "invalid_data_report.pdf"
        try:
            with open(output_filename_invalid, "wb") as f:
                f.write(pdf_output_invalid)
            print(f"Generated report for invalid data (check '{output_filename_invalid}')")
        except IOError as e:
            print(f"Error saving PDF file for invalid data: {e}")

