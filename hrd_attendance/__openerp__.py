{
    'name': 'HRD Attendance',
    'author'  :'CNT',
    'category': 'Human Resources',
    'description': """
Import tool untuk kehadiran karyawan dari data fingerprint berdasarkan
Fingerprint ID karyawan
""",    
    'depends': ['hr_attendance','hrd_employeedpu'],
    'update_xml':[
        'hrd_attendance.xml'],
    'data': [],
    'installable':True,
}
