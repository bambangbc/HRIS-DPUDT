{
    'name': 'HRD Scheduled Warning',
    'author'  :'macmour house',
    'category': 'Human Resources',
    'description': """
Module untuk memberikan warning jika ada kontrak yang mau habis
""",    
    'depends': ['hr','hrd_employee'],
    'update_xml':[
            "schedule_view.xml",
            ],
    'data': [],
    'installable':True,
}
