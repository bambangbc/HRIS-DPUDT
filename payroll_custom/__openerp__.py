{
	"name": "payroll DPUDT", 
	"version": "1.0", 
	"depends": ["base","board"], 
	"author": "Cinte", 
	"category": "HRD", 
	"description": """\
this is payroll system module
""",
	"depends" : ['hr_contract','hr_payroll'],
	"update_xml": ["contract_view.xml",
					"salary_structure1.xml",
					"salary_structure_sembako.xml",
					"payslip_report.xml",
					"payroll_view.xml",
		],
	"installable": True,
	"auto_install": False,
}