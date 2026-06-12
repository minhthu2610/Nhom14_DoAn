import pandas as pd

def style_excel(styler):
    styler = styler.format_index(lambda x: str(x).upper(), axis="columns")
    
    return styler.set_properties(**{
        'font-weight': '600',
        'border-color': 'rgba(128, 128, 128, 0.3)',
        'border-style': 'solid',
        'border-width': '1px',
        'text-align': 'right'
    }).set_table_styles([{
        'selector': 'th',
        'props': [
            ('font-weight', 'bold'),
            ('background-color', 'rgba(128, 128, 128, 0.1)'),
            ('border', '1px solid rgba(128, 128, 128, 0.3)'),
            ('text-align', 'center')
        ]
    }])
