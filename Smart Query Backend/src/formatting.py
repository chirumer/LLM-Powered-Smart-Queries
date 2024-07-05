def format_query_result(json):
    if not json:
        return '<p>Empty Result Obtained</p>'

    print('format', json)
    if len(json) == 1 and len(json[0]) == 1:
        key = list(json[0].keys())[0]
        return f'<p>{json[0][key]}</p>'
    
    html = '<table>'
    html += '<tr>'
    for key in json[0].keys():
        html += f'<th>{key}</th>'
    html += '</tr>'

    for row in json:
        html += '<tr>'
        for key in row.keys():
            html += f'<td>{row[key]}</td>'
        html += '</tr>'
    html += '</table>'
    return html

def format_schema(schema, relationships=None):
    headings = ["Field", "Type", "Null", "Key", "Default", "Extra"]

    schema_string = ''
    head_str = " | ".join(headings) + "\n"
    head_len = len(head_str)
    schema_string += "-" * head_len + "\n"
    schema_string += head_str
    schema_string += "-" * head_len + "\n"
    schema_string += "\n".join([f"{column[0]} | {column[1]} | {column[2]} | {column[3]} | {column[4]} | {column[5]}" for column in schema])
    schema_string += "\n" + "-" * head_len + "\n"

    if relationships:
        schema_string += "Relationships:\n"
        schema_string += "-" * head_len + "\n"
        rel_headings = ["Constraint Name", "Column", "Referenced Table", "Referenced Column"]
        rel_str = " | ".join(rel_headings) + "\n"
        schema_string += rel_str
        schema_string += "-" * head_len + "\n"
        for rel in relationships['relationships']:
            schema_string += f"{rel['constraint_name']} | {rel['column']} | {rel['referenced_table']} | {rel['referenced_column']}\n"
        schema_string += "-" * head_len + "\n"
    
    return schema_string