import time
import pprint
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval

class hr_payslip(osv.osv):
	'''
	Pay Slip
	'''

	_name = 'hr.payslip'
	_inherit = 'hr.payslip'
	_description = 'Pay Slip'

	def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
		def _sum_salary_rule_category(localdict, category, amount):
			if category.parent_id:
				localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
			localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
			return localdict

		class BrowsableObject(object):
			def __init__(self, pool, cr, uid, employee_id, dict):
				self.pool = pool
				self.cr = cr
				self.uid = uid
				self.employee_id = employee_id
				self.dict = dict

			def __getattr__(self, attr):
				return attr in self.dict and self.dict.__getitem__(attr) or 0.0

		class InputLine(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = datetime.now().strftime('%Y-%m-%d')
				result = 0.0
				self.cr.execute("SELECT sum(amount) as sum\
							FROM hr_payslip as hp, hr_payslip_input as pi \
							WHERE hp.employee_id = %s AND hp.state = 'done' \
							AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
						   (self.employee_id, from_date, to_date, code))
				res = self.cr.fetchone()[0]
				return res or 0.0

		class WorkedDays(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			def _sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = datetime.now().strftime('%Y-%m-%d')
				result = 0.0
				self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
							FROM hr_payslip as hp, hr_payslip_worked_days as pi \
							WHERE hp.employee_id = %s AND hp.state = 'done'\
							AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
						   (self.employee_id, from_date, to_date, code))
				return self.cr.fetchone()

			def sum(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[0] or 0.0

			def sum_hours(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[1] or 0.0

		class Payslips(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""

			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = datetime.now().strftime('%Y-%m-%d')
				self.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
							FROM hr_payslip as hp, hr_payslip_line as pl \
							WHERE hp.employee_id = %s AND hp.state = 'done' \
							AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
							(self.employee_id, from_date, to_date, code))
				res = self.cr.fetchone()
				return res and res[0] or 0.0

		#we keep a dict with the result because a value can be overwritten by another rule with the same code
		result_dict = {}
		rules = {}
		categories_dict = {}
		blacklist = []
		payslip_obj = self.pool.get('hr.payslip')
		inputs_obj = self.pool.get('hr.payslip.worked_days')
		obj_rule = self.pool.get('hr.salary.rule')
		payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
		worked_days = {}
		for worked_days_line in payslip.worked_days_line_ids:
			worked_days[worked_days_line.code] = worked_days_line
		inputs = {}
		for input_line in payslip.input_line_ids:
			inputs[input_line.code] = input_line

		categories_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, categories_dict)
		input_obj = InputLine(self.pool, cr, uid, payslip.employee_id.id, inputs)
		worked_days_obj = WorkedDays(self.pool, cr, uid, payslip.employee_id.id, worked_days)
		payslip_obj = Payslips(self.pool, cr, uid, payslip.employee_id.id, payslip)
		rules_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, rules)

		baselocaldict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj}
		#get the ids of the structures on the contracts and their parent id as well
		#structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
		if datetime.strptime(self.browse(cr,uid,payslip_id).date_to,"%Y-%m-%d").day == 5 :
			structure_id =self.pool.get('hr.payroll.structure').search(cr,uid,[('name','=','DPUDT SEMBAKO')])
			structure_ids = list(set(self.pool.get('hr.payroll.structure')._get_parent_structure(cr, uid, structure_id, context=context)))
		else :
			structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
		#get the rules of the structure and thier children
		rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
		#run the rules by sequence
		sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

		for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
			employee = contract.employee_id
			localdict = dict(baselocaldict, employee=employee, contract=contract)
			for rule in obj_rule.browse(cr, uid, sorted_rule_ids, context=context):
				key = rule.code + '-' + str(contract.id)
				localdict['result'] = None
				localdict['result_qty'] = 1.0
				localdict['result_rate'] = 100
				#check if the rule can be applied
				if obj_rule.satisfy_condition(cr, uid, rule.id, localdict, context=context) and rule.id not in blacklist:
					#compute the amount of the rule
					amount, qty, rate = obj_rule.compute_rule(cr, uid, rule.id, localdict, context=context)
					#check if there is already a rule computed with that code
					previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
					#set/overwrite the amount computed for this rule in the localdict
					tot_rule = amount * qty * rate / 100.0
					localdict[rule.code] = tot_rule
					rules[rule.code] = rule
					#sum the amount for its salary category
					localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
					#create/overwrite the rule in the temporary results
					result_dict[key] = {
						'salary_rule_id': rule.id,
						'contract_id': contract.id,
						'name': rule.name,
						'code': rule.code,
						'category_id': rule.category_id.id,
						'sequence': rule.sequence,
						'appears_on_payslip': rule.appears_on_payslip,
						'condition_select': rule.condition_select,
						'condition_python': rule.condition_python,
						'condition_range': rule.condition_range,
						'condition_range_min': rule.condition_range_min,
						'condition_range_max': rule.condition_range_max,
						'amount_select': rule.amount_select,
						'amount_fix': rule.amount_fix,
						'amount_python_compute': rule.amount_python_compute,
						'amount_percentage': rule.amount_percentage,
						'amount_percentage_base': rule.amount_percentage_base,
						'register_id': rule.register_id.id,
						'amount': amount,
						'employee_id': contract.employee_id.id,
						'quantity': qty,
						'rate': rate,
					}
				else:
					#blacklist this rule and its children
					blacklist += [id for id, seq in self.pool.get('hr.salary.rule')._recursive_search_of_rules(cr, uid, [rule], context=context)]

		result = [value for code, value in result_dict.items()]
		return result

	def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
		empolyee_obj = self.pool.get('hr.employee')
		contract_obj = self.pool.get('hr.contract')
		worked_days_obj = self.pool.get('hr.payslip.worked_days')
		input_obj = self.pool.get('hr.payslip.input')

		if context is None:
			context = {}
		#delete old worked days lines
		old_worked_days_ids = ids and worked_days_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
		if old_worked_days_ids:
			worked_days_obj.unlink(cr, uid, old_worked_days_ids, context=context)

		#delete old input lines
		old_input_ids = ids and input_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
		if old_input_ids:
			input_obj.unlink(cr, uid, old_input_ids, context=context)


		#defaults
		res = {'value':{
					  'line_ids':[],
					  'input_line_ids': [],
					  'worked_days_line_ids': [],
					  #'details_by_salary_head':[], TODO put me back
					  'name':'',
					  'contract_id': False,
					  'struct_id': False,
					  }
			}
		if (not employee_id) or (not date_from) or (not date_to):
			return res
		days = datetime.strptime(date_to,"%Y-%m-%d").day
		ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
		employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
		if days == 5 :
			res['value'].update({
						'name': _('Sembako of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
						'company_id': employee_id.company_id.id
			})
		else :
			res['value'].update({
						'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
						'company_id': employee_id.company_id.id
			})

		if not context.get('contract', False):
			#fill with the first contract of the employee
			contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)
		else:
			if contract_id:
				#set the list of contract for which the input have to be filled
				contract_ids = [contract_id]
			else:
				#if we don't give the contract, then the input to fill should be for all current contracts of the employee
				contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)

		if not contract_ids:
			return res
		contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
		res['value'].update({
					'contract_id': contract_record and contract_record.id or False
		})
		struct_record = contract_record and contract_record.struct_id or False
		if not struct_record:
			return res
		obj_struct = self.pool.get("hr.payroll.structure")
		src_struct = obj_struct.search(cr,uid,[('name','=','DPUDT SEMBAKO')])
		for strc in obj_struct.browse(cr,uid,src_struct):
			strc_rc = strc.id

		if days == 5 :
			res['value'].update({
					'struct_id': strc_rc,
		})
		else:
			res['value'].update({
					'struct_id': struct_record.id,
		})
		#computation of the salary input
		worked_days_line_ids = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
		input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
		res['value'].update({
					'worked_days_line_ids': worked_days_line_ids,
					'input_line_ids': input_line_ids,
		})
		return res
	
	def compute_sheet(self, cr, uid, ids, context=None):
		slip_line_pool = self.pool.get('hr.payslip.line')
		sequence_obj = self.pool.get('ir.sequence')
		beapokok1 = 0

		payslip_date = self.browse(cr,uid,ids).date_from
		contract_date = self.browse(cr,uid,ids).contract_id.date_start
		masa_kerja = (datetime.strptime(payslip_date,"%Y-%m-%d") - datetime.strptime(contract_date,"%Y-%m-%d")).days
		if masa_kerja >= 365 :
			self.write(cr,uid,ids,{'sembako':1})
		else :
			self.write(cr,uid,ids,{'sembako':0})

		if datetime.strptime(self.browse(cr,uid,ids).date_to,"%Y-%m-%d").day == 5 :
			slip_line_pool = self.pool.get('hr.payslip.line')
			sequence_obj = self.pool.get('ir.sequence')
			for payslip in self.browse(cr, uid, ids, context=context):
				number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
				#delete old payslip lines
				old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
	#            old_slipline_ids
				if old_slipline_ids:
					slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
				if payslip.contract_id:
					#set the list of contract for which the rules have to be applied
					contract_ids = [payslip.contract_id.id]
				else:
					#if we don't give the contract, then the rules to apply should be for all current contracts of the employee
					contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
				lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
				self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number,}, context=context)
				# import pdb;pdb.set_trace()
			return True
		else :
			for payslip in self.browse(cr, uid, ids, context=context):
				
				# Mencari Gapok
				tahun_kerja = datetime.now().date() - datetime.strptime(payslip.employee_id.mulai_kerja,"%Y-%m-%d").date()
				tahun = float(tahun_kerja.days)/365
				obj_bea = self.pool.get('hr.beapokok')
				src_bea = obj_bea.search(cr,uid,[])
				for beapokok in obj_bea.browse(cr,uid,src_bea):
					if payslip.employee_id.type_id.id == beapokok.jenjang.id and float(beapokok.kerja_dari) <= tahun and float(beapokok.kerja_sampai) >= tahun :
						beapokok1 = beapokok.nominal
				if tahun >= 5 :
					p_pensiun = 12
				else :
					p_pensiun = 0

				# mencari Tunjangan Kompetensi
				import pdb;pdb.set_trace()
				if tahun >= 5  :
					nilai = (((80.00+90.00)/100.00)/2.00)*payslip.contract_id.jenis_tunjangan.tunj_kompetensi
				elif tahun < 5 :
					nilai = (((((80.00+90.00)/100.00)/2.00)*payslip.contract_id.jenis_tunjangan.tunj_kompetensi)*25.00)/100.00
				else :
					nilai = 0
				self.write(cr,uid,[payslip.id],{'tunj_komp': nilai}) 

				# mencari tunjangan BPJS
				#import pdb;pdb.set_trace()
				if float(tahun_kerja.days) >= 122 and tahun < 5 :
					bpjs = (payslip.contract_id.lokasi_kerja.tunjangan * payslip.contract_id.type_id.bpjskes_perusahaan)/100
					pot_bpjs_kes =  (payslip.contract_id.lokasi_kerja.tunjangan * (payslip.contract_id.type_id.bpjskes_perusahaan+payslip.contract_id.type_id.bpjskes_karyawan))/100
					pot_bpjs_ten = 0 
				elif tahun >= 5 :
					bpjs = ((payslip.contract_id.lokasi_kerja.tunjangan * payslip.contract_id.type_id.bpjskes_perusahaan)/100) + ((payslip.contract_id.lokasi_kerja.tunjangan * payslip.contract_id.type_id.bpjsten_perusahaan)/100)
					pot_bpjs_kes = (payslip.contract_id.lokasi_kerja.tunjangan * (payslip.contract_id.type_id.bpjskes_perusahaan+payslip.contract_id.type_id.bpjskes_karyawan))/100 
					pot_bpjs_ten = (payslip.contract_id.lokasi_kerja.tunjangan * (payslip.contract_id.type_id.bpjsten_perusahaan+payslip.contract_id.type_id.bpjsten_karyawan))/100
				else :
					bpjs = 0
					pot_bpjs_kes = 0
					pot_bpjs_ten = 0
				self.write(cr,uid,[payslip.id],{'tunj_bpjs':bpjs,'iuran_kes':pot_bpjs_kes,'iuran_jams':pot_bpjs_ten})
				# mencari jumlah izin dan sakit
				line_ids = payslip.worked_days_line_ids
				jum = 0.0
				for IS in line_ids :
					codes = IS.code
					if codes == "IZIN" or codes == "SAKIT" :
						jum += IS.number_of_days
				self.write(cr,uid,[payslip.id],{'jum_is': jum}) 
				#################

				#################################
				izin = 0 
				hari_kerja = 0
				for hari in payslip.worked_days_line_ids :
					if hari.code == 'WORK100' :
						hari_kerja = int(hari.number_of_days)
					if hari.code == 'IZIN' :
						izin = int(hari.number_of_days)
					if hari.code == 'TK' :
						tk = int(hari.number_of_days)
				self.write(cr,uid,[payslip.id],{"jum_harikerja": hari_kerja,
												"jum_harikerja1": hari_kerja , 
												"izin":izin,
												"tk":tk})
				#################################

				number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
				#delete old payslip lines
				old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
	#            old_slipline_ids
				if old_slipline_ids:
					slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
				if payslip.contract_id:
					#set the list of contract for which the rules have to be applied
					contract_ids = [payslip.contract_id.id]
				else:
					#if we don't give the contract, then the rules to apply should be for all current contracts of the employee
					contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)    
				tunj_jabatan = 0
				tunj_makan = 0
				tunj_transport = 0
				tunj_istri = 0
				tunj_anak = 0
				tunj_tk = 0
				tunj_sd = 0
				tunj_smp = 0
				tunj_sma = 0
				tunj_pt = 0
				tunj_penye = 0
				tunj_bpjs = 0
				tunj_mahal = 0
				tunj_disiplin = 0
				tunj_pensiun = 0
				tunj_tugas = 0
				voucher = 0
				sembako = 0
				overtime = 0
				iuran_kes = 0
				iuran_jams = 0
				pot_dpu = 0
				terlambat = 0
				pot_pensiun = 0
				pot_ars = 0
				wakaf = 0
				zis = 0
				qurban = 0
				min_bl = 0
				koperasi = 0
				parkir = 0
				pen_ali = 0
				pot_lain = 0   
				lain_lain = 0 
				t_kemahalan = 0
				for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
					cod = line["code"]
					if cod == "TJB" :
						tunj_jabatan = line["amount"]
					if cod == "TJM" :
						tunj_makan = line["amount"]
					if cod == "TJT" :
						tunj_transport = line["amount"]
					if cod == "TBPJS" :
						tunj_bpjs = line["amount"]
					# if cod == "TM" :
					#     tunj_komunikasi = line["amount"]
					if cod == "TI" :
						tunj_istri = line["amount"]
					if cod == "BALITA" :
						tunj_anak = line["amount"]
					if cod == "TK" :
						tunj_tk = line["amount"]
					if cod == "SD" :
						tunj_sd = line["amount"]
					if cod == "SMP" :
						tunj_smp = line["amount"]
					if cod == "SMA" :
						tunj_sma = line["amount"]
					if cod == "PT":
						tunj_pt = line["amount"]
					if cod == "TJP" :
						tunj_penye = line["amount"]
					if cod == "TKM" :
						tunj_mahal = line["amount"]
					if cod == "KBL" :
						min_bl = line["amount"]
					if cod == "TKD" :
						tunj_disiplin = line["amount"]
					if cod == "TPN" :
						tunj_pensiun = line["amount"]
					if cod == "PDPU" :
						pot_dpu = line["amount"]
					if cod == "PIK" :
						iuran_kes = line["amount"]
					if cod == "PIJS" :
						iuran_jams = line["amount"]
					if cod == "PPN" :
						pot_pensiun = line["amount"]
					if cod == "PK" :
						koperasi = line["amount"]
					if cod == "PZ" :
						zis = line["amount"]
					if cod == "PW" :
						wakaf = line["amount"]
					if cod == "PA" :
						pot_ars = line["amount"]
					if cod == "PPA" :
						pen_ali = line["amount"]
					if cod == "PQ" :
						qurban = line["amount"]
					if cod == "PP" :
						parkir = line["amount"]
					if cod == "PLL" :
						pot_lain = line["amount"]
					if cod == "OVERTIME" :
						overtime = line["amount"]
					if cod == "PL2" :
						lain_lain = line["amount"]
					if cod == "PKT" :
						terlambat = line["amount"]
					if cod == "TKM" :
						t_kemahalan = line["amount"]
					if cod == "TV" :
						voucher = line["amount"]
					if cod == "TSK" :
						sembako = line["amount"]
					if cod == "TPU" :
						tunj_tugas = line["amount"]
					# if cod == "THR" :
					#     thr = line["amount"]
					# if cod == "BONUS" :
					#     bonus = line["amount"]    
					# if cod == "PKH" :
					#     ketidakhadiran = line["amount"]
					# if cod == "KSBN" :
					#     kasbon = line["amount"]
					# if cod == "CICILAN" :
					#     cicilan = line["amount"]
					if cod == "GROSS" :
						gross = line["amount"]
					if cod == "NET" :
						net = line["amount"]
				self.write(cr,uid,[payslip.id],{
					"tunj_jabatan"      : int(tunj_jabatan),        
					"tunj_makan"        : int(tunj_makan),   
					"tunj_transport"    : int(tunj_transport),
					#"tunj_bpjs"         : int(tunj_bpjs),
					#"tunj_komunikasi"   : int(tunj_komunikasi),
					"tunj_istri"        : int(tunj_istri),
					"tunj_anak"         : int(tunj_anak),
					"tunj_tk"           : int(tunj_tk),
					"tunj_sd"           : int(tunj_sd),
					"tunj_smp"          : int(tunj_smp),
					"tunj_sma"          : int(tunj_sma),
					"tunj_pt"           : int(tunj_pt),
					"tunj_penye"        : int(tunj_penye),
					"tunj_mahal"        : int(tunj_mahal),
					"voucher"			: int(voucher),
					"sembako"			: int(sembako),
					"tunj_tugas"		: int(tunj_tugas),
					"min_bl"            : int(min_bl),
					"lembur"            : int(overtime),
					"tunj_disiplin"     : int(tunj_disiplin),
					#"tunj_pensiun"      : int(tunj_pensiun),
					"pot_dpu"           : int(pot_dpu),
					#"iuran_kes"         : int(iuran_kes),
					#"iuran_jams"        : int(iuran_jams),
				   # "tidakhadir"        : int(ketidakhadiran),
					#"pot_pensiun"       : int(pot_pensiun),
					"koperasi"          : int(koperasi),
					"zis"               : int(gross+sembako+voucher) * 25 / 1000,
					"wakaf"             : int(wakaf),
					"pot_ars"           : int(pot_ars),
					"pen_ali"           : int(pen_ali),
					"qurban"            : int(qurban),
					"parkir"            : int(parkir),
					"pot_lain"          : int(pot_lain),
					"lain_lain"         : int(lain_lain),
					"terlambat"         : int(terlambat),
					"total_tunjangan"   : int(gross), 
					"total_potongan"    : int(gross-net),   
					"net"               : int(net),
					# "cashbon"           : int(kasbon), 
					# "cicilan"           : int(cicilan),
					# "thr"               : int(thr),
					"bonus"             : beapokok1,  
						 })
				# prhitungsn tunjangan pensiun
				if tahun >= 5 :
					tunj_pensiun = ((payslip.bonus +  payslip.contract_id.jenis_tunjangan.tunj_jabatan + payslip.tunj_transport + payslip.tunj_makan + (payslip.tunj_komp*2) + payslip.tunj_istri + payslip.tunj_anak + payslip.tunj_tk + payslip.tunj_sd + payslip.tunj_smp + payslip.tunj_sma + payslip.tunj_pt + payslip.tunj_bpjs)*12)/100
					self.write(cr,uid,[payslip.id],{'tunj_pensiun': tunj_pensiun,'pot_pensiun': tunj_pensiun})
				lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
				self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number,}, context=context)
		return True

	def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
		days = datetime.strptime(date_to,"%Y-%m-%d").day
		if days == 5 :
			res = self.get_worked_day_sembako(cr, uid, contract_ids, date_from, date_to, context=None)
		else :
			res = self.get_worked_day_gapok(cr, uid, contract_ids, date_from, date_to, context=None)
		return res

	def get_worked_day_sembako(self, cr, uid, contract_ids, date_from, date_to, context=None):
		"""
		@param contract_ids: list of contract id
		@return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
		"""
		def was_on_leave(employee_id, datetime_day, context=None):
			res = False
			day = datetime_day.strftime("%Y-%m-%d")
			holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
			if holiday_ids:
				res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
			return res

		res = []
		jum_is = 0

		for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
			if not contract.working_hours:
				#fill only if the contract as a working schedule linked
				continue
			attendances = {
				 'name': _("Normal Working Days paid at 100%"),
				 'sequence': 1,
				 'code': 'WORK100',
				 'number_of_days': 0.0,
				 'number_of_hours': 0.0,
				 'contract_id': contract.id,
			}
			presences = {
				 'name': _("Presences"),
				 'sequence': 2,
				 'code': 'PRESENCES',
				 'number_of_days': 0.0,
				 'number_of_hours': 0.0,
				 'contract_id': contract.id,            
			}
			# lembur = {
			# 	 'name': _("Lembur"),
			# 	 'sequence': 2,
			# 	 'code': 'LEMBUR',
			# 	 'number_of_days': 0.0,
			# 	 'number_of_hours': 0.0,
			# 	 'contract_id': contract.id,            
			# }
			# tanpa_keterangan = {
			# 	 'name': _("Tanpa keterangan"),
			# 	 'sequence': 2,
			# 	 'code': 'TK',
			# 	 'number_of_days': 0.0,
			# 	 'number_of_hours': 0.0,
			# 	 'contract_id': contract.id,            
			# }
			# terlambat1 = {
			# 'name': _("Terlambat 1-15mnt"),
			# 'sequence' : 3,
			# 'code' : 'KETERLAMBATAN1',
			# 'number_of_days': 0.0,
			# 'number of hours' : 0.0,
			# 'contract_id': contract.id,
			# }
			# terlambat2 = {
			# 'name': _("Terlambat 15-60mnt"),
			# 'sequence' : 4,
			# 'code' : 'KETERLAMBATAN2',
			# 'number_of_days': 0.0,
			# 'number of hours' : 0.0,
			# 'contract_id': contract.id,
			# }
			# terlambat3 = {
			# 'name': _("Terlambat 1-3jam"),
			# 'sequence' : 5,
			# 'code' : 'KETERLAMBATAN3',
			# 'number_of_days': 0.0,
			# 'number of hours' : 0.0,
			# 'contract_id': contract.id,
			# }
			# terlambat4 = {
			# 'name': _("Terlambat > 3jam"),
			# 'sequence' : 6,
			# 'code' : 'KETERLAMBATAN4',
			# 'number_of_days': 0.0,
			# 'number of hours' : 0.0,
			# 'contract_id': contract.id,
			# }            
			day_from = datetime.strptime(str(datetime.strptime(date_from,"%Y-%m-%d").year)+"-"+str((datetime.strptime(date_from,"%Y-%m-%d") -timedelta(days=1)).month)+"-"+"01","%Y-%m-%d")
			day_to = datetime.strptime(date_from,"%Y-%m-%d") - timedelta(days=1)
			nb_of_days = (day_to - day_from).days + 1
			tanpa_keterangan1 = 0.0
			
			for day in range(0, nb_of_days):
				working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
				datas = (day_from + timedelta(days=day)).isoweekday()
				# import pdb;pdb.set_trace()
				if working_hours_on_day:
						
					#kehadiran
					
					real_working_hours_on_day = self.pool.get('hr.attendance').real_working_hours_on_day(cr,uid, contract.employee_id.id, day_from + timedelta(days=day),context)
					# if datas == 3 :
					# 	import pdb;pdb.set_trace()
					# 	x = 0
					if real_working_hours_on_day['time'] >= 0.000000000000000001 and datas == 4 and real_working_hours_on_day['keterlambatan2'] == False and real_working_hours_on_day['keterlambatan3'] == False and real_working_hours_on_day['keterlambatan4'] == False:
						presences['number_of_days'] += 1.0
						presences['number_of_hours'] += working_hours_on_day
					if datas == 4 :
						attendances['number_of_days'] += 1.0
						attendances['number_of_hours'] += working_hours_on_day

			res += [attendances] + [presences]
		return res

	def get_worked_day_gapok(self, cr, uid, contract_ids, date_from, date_to, context=None):
		"""
		@param contract_ids: list of contract id
		@return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
		"""
		def was_on_leave(employee_id, datetime_day, context=None):
			res = False
			day = datetime_day.strftime("%Y-%m-%d")
			holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
			if holiday_ids:
				res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
			return res

		res = []
		jum_is = 0

		for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
			if not contract.working_hours:
				#fill only if the contract as a working schedule linked
				continue
			attendances = {
				 'name': _("Normal Working Days paid at 100%"),
				 'sequence': 1,
				 'code': 'WORK100',
				 'number_of_days': 0.0,
				 'number_of_hours': 0.0,
				 'contract_id': contract.id,
			}
			presences = {
				 'name': _("Presences"),
				 'sequence': 2,
				 'code': 'PRESENCES',
				 'number_of_days': 0.0,
				 'number_of_hours': 0.0,
				 'contract_id': contract.id,            
			}
			lembur = {
				 'name': _("Lembur"),
				 'sequence': 2,
				 'code': 'LEMBUR',
				 'number_of_days': 0.0,
				 'number_of_hours': 0.0,
				 'contract_id': contract.id,            
			}
			tanpa_keterangan = {
				 'name': _("Tanpa keterangan"),
				 'sequence': 2,
				 'code': 'TK',
				 'number_of_days': 0.0,
				 'number_of_hours': 0.0,
				 'contract_id': contract.id,            
			}
			terlambat1 = {
			'name': _("Terlambat 1-15mnt"),
			'sequence' : 3,
			'code' : 'KETERLAMBATAN1',
			'number_of_days': 0.0,
			'number of hours' : 0.0,
			'contract_id': contract.id,
			}
			terlambat2 = {
			'name': _("Terlambat 15-60mnt"),
			'sequence' : 4,
			'code' : 'KETERLAMBATAN2',
			'number_of_days': 0.0,
			'number of hours' : 0.0,
			'contract_id': contract.id,
			}
			terlambat3 = {
			'name': _("Terlambat 1-3jam"),
			'sequence' : 5,
			'code' : 'KETERLAMBATAN3',
			'number_of_days': 0.0,
			'number of hours' : 0.0,
			'contract_id': contract.id,
			}
			terlambat4 = {
			'name': _("Terlambat > 3jam"),
			'sequence' : 6,
			'code' : 'KETERLAMBATAN4',
			'number_of_days': 0.0,
			'number of hours' : 0.0,
			'contract_id': contract.id,
			}
			leaves = {}            
			day_from = datetime.strptime(date_from,"%Y-%m-%d")
			day_to = datetime.strptime(date_to,"%Y-%m-%d")
			nb_of_days = (day_to - day_from).days + 1

			tanpa_keterangan1 = 0.0
			
			for day in range(0, nb_of_days):
				working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
				
				#menghitung lembur
				employee_id = contract.employee_id.id
				datas = day_from + timedelta(days=day)
				tanggal = datas.strftime("%Y-%m-%d")
				obj_over = self.pool.get('hr.overtime')
				src_over = obj_over.search(cr,uid,[('employee_id','=',employee_id),('tanggal','=',tanggal),('state','=','validate')])
				for overt in obj_over.browse(cr,uid,src_over) :
					if overt.overtime_type_id.name == 'Lembur' :
						jumlah = overt.total_jam1
						jumlah_ril = overt.jam_lembur
						lembur['number_of_hours'] += jumlah

				if working_hours_on_day:
					#the employee had to work
					leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
					if leave_type:
						#if he was on leave, fill the leaves dicts
						if leave_type in leaves:
							leaves[leave_type]['number_of_days'] += 1.0
							leaves[leave_type]['number_of_hours'] += working_hours_on_day
						else:
							leaves[leave_type] = {
								'name': leave_type,
								'sequence': 5,
								'code': leave_type,
								'number_of_days': 1.0,
								'number_of_hours': working_hours_on_day,
								'contract_id': contract.id,
							}

						# attendance
						if leave_type == "IZIN" or leave_type == "SAKIT" :
							jum_is += 1

					else:
						
						#kehadiran
						
						real_working_hours_on_day = self.pool.get('hr.attendance').real_working_hours_on_day(cr,uid, contract.employee_id.id, day_from + timedelta(days=day),context)
						if real_working_hours_on_day['time'] >= 0.000000000000000001 and leave_type == False:
							presences['number_of_days'] += 1.0
							presences['number_of_hours'] += working_hours_on_day
						terlambat1['number_of_days'] += real_working_hours_on_day['keterlambatan1']
						terlambat2['number_of_days'] += real_working_hours_on_day['keterlambatan2']
						terlambat3['number_of_days'] += real_working_hours_on_day['keterlambatan3']
						terlambat4['number_of_days'] += real_working_hours_on_day['keterlambatan4']
						#add the input vals to tmp (increment if existing)
						attendances['number_of_days'] += 1.0
						attendances['number_of_hours'] += working_hours_on_day
			tanpa_keterangan['number_of_days'] = attendances['number_of_days'] - presences['number_of_days'] #- tanpa_keterangan1
			leaves = [value for key,value in leaves.items()]
			res += [attendances] + leaves + [presences] + [lembur] + [tanpa_keterangan] + [terlambat1] + [terlambat2] + [terlambat3] + [terlambat4]
		return res
	_columns = {
		'jum_is' : fields.integer("Jumlah"),
		'jum_harikerja' : fields.char("Jumlah hari kerja"),
		'jum_harikerja1': fields.integer("jum hari kerja"),
		'izin' : fields.integer("Izin"),
		"tk" : fields.integer("TK"),
		###### utuk Di Paysip ########
		"tunj_jabatan"          : fields.float("Tunjangan Jabatan"),
		"tunj_istri"            : fields.float("Tunjangan Istri"),
		"tunj_anak"             : fields.float("Tunjangan Anak"),
		"tunj_tk"               : fields.float("Tunjangan TK"),
		"tunj_sd"               : fields.float("Tunjangan Anak SD"),
		"tunj_smp"              : fields.float("Tunjangan Anak SMP"),
		"tunj_sma"              : fields.float("Tunjangan Anak SMA"),
		"tunj_pt"               : fields.float("Tunjangan Anak PT"),
		"tunj_makan"            : fields.float("Tunjangan Makan"),
		"tunj_transport"        : fields.float("Tunjangan Transport"),
		"tunj_bpjs"             : fields.float("Tunjangan BPJS"),
		#"tunj_komunikasi"       : fields.float("Tunjangan Komunikasi"),
		"tunj_komp"             : fields.float("Tunjangan Kompetensi"),
		"tunj_penye"            : fields.float("Tunjangan Penyesuaian"),
		"tunj_mahal"            : fields.float("Tunjangan Kemahalan"),
		"min_bl"                : fields.float("Kekurangan Bulan Lalu"),
		"lembur"                : fields.float("Lembur"),
		"tunj_disiplin"         : fields.float("Tunjangan Kedisiplinan"),
		"tunj_pensiun"          : fields.float("Tunjangan Pensiun"),
		"pot_dpu"               : fields.float("Potongan DPU"),
		"iuran_kes"             : fields.float("Iuran Kesehatan"),
		"iuran_jams"            : fields.float("Iuran Jamsostek"),
		"pot_pensiun"           : fields.float("Potongan Pensiun"),
		"koperasi"              : fields.float("Koperasi"),
		"zis"                   : fields.float("ZIS"),
		"wakaf"                 : fields.float("Wakaf"),
		"pot_ars"               : fields.float("Potongan Arisan"),
		"pen_ali"               : fields.float("Potongan Pensiun dan Alianz"),
		"qurban"                : fields.float("Potongan Qurban"),
		"parkir"                : fields.float("Potongan Parkir"),
		"pot_lain"              : fields.float("Potongan Lain-Lain"),
		"lain_lain"             : fields.float("Potongan Lain-Lain 2"),
		"terlambat"             : fields.float("Keterlambatan"),
		"total_tunjangan"       : fields.float("Total Tunjangan"),
		"total_potongan"        : fields.float("Total Potongan"),
		"net"                   : fields.float("Total"),
		"tidakhadir"            : fields.float("Terlambat"),
		"cashbon"               : fields.float("Kasbon"),
		"cicilan"               : fields.float("cicilan"),
		"thr"                   : fields.float("THR"),
		"bonus"                 : fields.float("Bonus"),
		"sembako"				: fields.float('sembako'),
	}        
		  


hr_payslip()

class hr_attendance(osv.osv):
	_name = "hr.attendance"
	_inherit = "hr.attendance"

	def real_working_hours_on_day(self, cr, uid, employee_id, datetime_day, context=None):
		delta = {}
		day = datetime_day.strftime("%Y-%m-%d 00:00:00")
		day2 = datetime_day.strftime("%Y-%m-%d 24:00:00")


		#employee attendance
		atts_ids = self.search(cr, uid, [('employee_id', '=', employee_id), ('name', '>', day), ('name', '<', day2)], limit=2, order='name asc' )
		
		time1=0
		time2=0
		delta['keterlambatan1'] = 0
		delta['keterlambatan2'] = 0
		delta['keterlambatan3'] = 0
		delta['keterlambatan4'] = 0

		for att in self.browse(cr, uid, atts_ids, context=context):
			if att.action == 'sign_in':
				time1 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")

				#cari keterlambatan
				hari=str(time1.isoweekday() - 1)
				emp_brw = self.pool.get('hr.contract')
				emp_src = emp_brw.search(cr, uid, [('employee_id', '=', employee_id)])
				for contract in emp_brw.browse(cr, uid, emp_src, context=context):
					for schedule in contract.working_hours.attendance_ids :
						if schedule.dayofweek == hari :
							hour_from = schedule.hour_from
				
				time11 = time1 + timedelta(hours = 7)
				jam = time11.hour
				menit = (time11.minute * 100) / 60
				realdate = float(jam + (float(menit) / 100))
				keterlambatan = realdate - hour_from 
				if keterlambatan >= (float(100)/float(60)) / float(100) and keterlambatan <= ((float(100)*float(15)) / float(60)) /float(100) :
					delta['keterlambatan1'] = 1
				elif keterlambatan >= ((float(100)*float(15)) / float(60)) / float(100) and keterlambatan <= ((float(100)*float(60))  / float(60)) / float(100) :
					delta['keterlambatan2'] = 1
				elif keterlambatan >= ((float(100)*float(61)) / float(60)) / float(100) and keterlambatan <= ((float(100)*float(180)) / float(60)) / float(100) :
					delta['keterlambatan3'] = 1
				elif keterlambatan >= ((float(100)*float(181)) / float(60)) / float(100) :
					delta['keterlambatan4'] = 1
			else:
				time2 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
		
		if time2 and time1:
			delta['time'] = (time2 - time1).seconds / 3600.00
		else:
			delta['time'] = 0
      
		return delta

	def _altern_si_so(self, cr, uid, ids, context=None):
		""" Alternance sign_in/sign_out check.
			Previous (if exists) must be of opposite action.
			Next (if exists) must be of opposite action.

			PPI: skip _constraints supaya bisa import dari CSV
		"""
		print "_altern_si_so"
		return True

hr_attendance()

class hr_beapokok(osv.osv):
	_name = "hr.beapokok"

	_columns = {
		"jenjang" : fields.many2one("hr.recruitment.degree", "Jenjang"),
		"kerja_dari" : fields.integer("Dari Tahun"),
		"kerja_sampai" : fields.integer("Sampai Tahun"),
		"nominal" : fields.integer('Bea Pokok'),
	}
