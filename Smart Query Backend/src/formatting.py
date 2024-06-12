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