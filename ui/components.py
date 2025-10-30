def barra_html(porcentaje):
    return f"""
    <div style='width:100%;background-color:#ddd;border-radius:5px'>
        <div style='width:{porcentaje}%;background-color:#4caf50;height:24px;border-radius:5px'></div>
    </div>
    <p style='margin-top:4px'>{porcentaje:.2f}%</p>
    """