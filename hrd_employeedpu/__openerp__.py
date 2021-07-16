{
    'name': 'HRD Employee for DPU DT',
    'author'  :'CNT',
    'category': 'Human Resources',
    'description': """
Human Resource Employee Data for Indonesian Companies.
======================================================================================
* Adding fields to Employee data.
* Adding master data.
* Adding Working Schedule Data.
* Adding Indonesian Province Master Data
* Adding Indonesian Kota/ Kabupaten Master Data
""",
    'depends': ['hr','hr_recruitment'],
    'data': [
        'employee_view.xml',
        'action.xml',
        'working_Schedule.xml',
        'data/hr_recruit.prov.csv',
        'data/hr_recruit.kota.csv',
    ],
    'installable':True,
    'application':True,
}
