import re

# This function reads the .ass file and separates its content into headers, format information, and dialogue events.
def parse_ass_file(filename):
    # Open the file for reading with UTF-8 encoding
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Initialize empty lists to store headers, format information, and dialogue events
    headers, events_format, events_dialogue = [], [], []
    section = None

    # Process each line in the file
    for line in lines:
        stripped = line.strip()
        # Check if the line indicates the start of a new section (e.g., [Script Info], [V4+ Styles], [Events])
        if stripped.startswith("["):
            section = stripped
        # If the line is part of the headers (Script Info or Styles), add it to the headers list
        if section in ["[Script Info]", "[V4+ Styles]"]:
            headers.append(line)
        # If the line is a dialogue event, add it to the events_dialogue list
        elif section == "[Events]" and stripped.startswith("Dialogue"):
            events_dialogue.append(line)
        # Otherwise, add it to the events_format list
        else:
            if section is not None:
                events_format.append(line)
    
    return headers, events_format, events_dialogue

# This function removes formatting tags from the subtitle text for easier comparison
def normalize_text(text):
    # Remove anything inside curly braces {} and strip leading/trailing whitespace
    return re.sub(r'{[^}]*}', '', text).strip()

# This function generates the output events, including previous and next lines for each dialogue event
def generate_output_events(events_dialogue):
    unique_lines = []
    line_map = {}
    output_events = []

    # Map each unique line to its occurrences
    for event in events_dialogue:
        parts = event.split(',', 9)
        start, end, style, name, margin_l, margin_r, margin_v, effect, text = parts[1:]
        normalized_text = normalize_text(text)
        if normalized_text not in line_map:
            line_map[normalized_text] = {
                "times": [],
                "text": normalized_text
            }
        line_map[normalized_text]["times"].append((start, end, text))

    # Generate the output events
    normalized_lines = list(line_map.keys())
    for i, line in enumerate(normalized_lines):
        times = line_map[line]["times"]
        for start, end, original_text in times:
            prev_text = normalize_text(line_map[normalized_lines[i - 1]]["text"]) if i > 0 else "..."
            next_text = normalize_text(line_map[normalized_lines[i + 1]]["text"]) if i < len(normalized_lines) - 1 else "..."

            # Create the previous, current, and next line events
            prev_line_event = f"Dialogue: 0,{start},{end},P,,0,0,0,,{prev_text}\n"
            current_line_event = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{original_text}"
            next_line_event = f"Dialogue: 0,{start},{end},F,,0,0,0,,{next_text}\n\n"

            # Add the events to the output list
            output_events.extend([prev_line_event, current_line_event, next_line_event])
    
    return output_events

# This function writes the output .ass file
def write_ass_file(filename, headers, events_format, events_dialogue):
    with open(filename, 'w', encoding='utf-8') as file:
        # Write headers and format information
        file.writelines(headers)
        file.writelines(events_format)
        file.write("\n")
        # Write the dialogue events with newlines every three lines for readability
        for i, event in enumerate(events_dialogue):
            file.write(event)
            if (i + 1) % 3 == 0:
                file.write("\n")

# Main function to convert the input .ass file to the desired output .ass file
def convert_ass_file(input_filename, output_filename):
    # Parse the input file to get headers, format information, and dialogue events
    headers, events_format, events_dialogue = parse_ass_file(input_filename)
    # Generate the output events with previous and next lines
    output_events = generate_output_events(events_dialogue)
    # Write the output file
    write_ass_file(output_filename, headers, events_format, output_events)

# Usage: Specify the input and output filenames
input_filename = 'input_subtitles.ass'
output_filename = 'output.ass'
convert_ass_file(input_filename, output_filename)
