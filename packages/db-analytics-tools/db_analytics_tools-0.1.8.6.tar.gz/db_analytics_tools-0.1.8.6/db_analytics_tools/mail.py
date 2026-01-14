""""
Module for generating HTML email content for ETL job status updates.
"""



##################################################################################################
## CONSTANTS
##################################################################################################
MAIL_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <style>
        table {{
            font-family: Arial, sans-serif;
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
Bonjour à tous,<br>
<br>
L'exécution du job <strong>{etl_name}</strong> est terminée.<br>
<br>
Ci-dessous le statut de mise à jour des tables:
<br>
<table>
    <tr>
        <th>Check Date</th>
        <th>Table ID</th>
        <th>Table Name</th>
        <th>Last Date</th>
        <th>Load Date</th>
        <th>Status</th>
        <th>Missing Dates</th>
    </tr>
    {html_table}
</table>

<br>
Bonne réception.<br>
Big Data & Customer Analytics
<hr>
<i>Attention : Ce mail a été généré automatiquement.</i>
</body>
</html>
"""
##################################################################################################

def generate_mail(etl_name, html_table, html_template=MAIL_CONTENT):
    """
    Generate the HTML content for the email.
    
    Args:
        html_template (str): The HTML template for the email.
        etl_name (str): The name of the ETL process.
        
    Returns:
        str: The generated HTML content.
    """
    return html_template.format(etl_name=etl_name, html_table=open(html_table, "r").read())
