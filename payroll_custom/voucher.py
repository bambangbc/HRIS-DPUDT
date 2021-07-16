from openerp import models, fields, api, tools

class hr_voucher(models.Model):
	_name = "hr.vouchers"

	@api.multi
	def _get_totals(self):
		tot_hasil_kerja = 0
		tot_hasil_kepribadian = 0
		tot_hasil_keterampilan = 0
		for move in self:
			move.tot_hasil_kerja = (move.mutu_kerja + move.pengetahuan_teknis + move.produktivitas_kerja + move.tanggung_jawab)/4
			move.tot_hasil_keterampilan = (move.kepemimpinan + move.plan + move.pemecah_masalah + move.pendelegasian)/4
			if move.status == "8" :
				move.tot_hasil_kepribadian = (move.disiplin + move.kerjasama + move.sikap_kerja + move.sikap_proaktif
			 + move.tanggungjawab + move.adaptasi + move.kestabilan + move.sikapthd + move.kekuatan)/8
			else :
				move.tot_hasil_kepribadian = (move.disiplin + move.kerjasama + move.sikap_kerja + move.sikap_proaktif
			 + move.tanggungjawab + move.adaptasi + move.kestabilan + move.sikapthd + move.kekuatan)/9


	penilai = fields.Many2one('hr.employee',string='Nama Penilai')
	employee_id = fields.Many2one('hr.employee','Nama Karyawan')
	bagian = fields.Many2one('hr.department','Bagian')
	status = fields.Selection([('8','Pemimpin'),('9','Staff')])
	tgl_penilaian = fields.Date("Tanggal Penilaian")
	periode = fields.Date("Periode")

	##### Hasil Kerja ####
	mutu_kerja = fields.Float('Mutu Kerja')
	pengetahuan_teknis = fields.Float('Pengetahuan Teknis')
	produktivitas_kerja = fields.Float('Produktivitas Kerja')
	tanggung_jawab = fields.Float('Rasa Tanggung Jawab Yang Dimiliki')
	tot_hasil_kerja = fields.Float('Total Hasil Kerja', readonly=True, compute="_get_totals")

	##### Kepribadian #####
	disiplin = fields.Float('Disiplin')
	kerjasama = fields.Float('Kerjasama dan Komunikasi')
	sikap_kerja = fields.Float('Sikap Kerja')
	sikap_proaktif = fields.Float('Sikap proaktiv, inovatif dan inisiatif ')
	tanggungjawab = fields.Float('Tanggungjawab dan rasa memiliki')
	adaptasi = fields.Float('Adaptasi Dengan Lingkungan Kerja')
	kestabilan = fields.Float('kestabilan mental dan fisik')
	sikapthd = fields.Float('sikap terhadap atasan dan rekan kerja')
	kekuatan = fields.Float('kekuatan ruhiyah')
	tot_hasil_kepribadian =  fields.Float('Total Hasil Kepribadian', readonly=True, compute="_get_totals")
	
	##### Keterampilan Management #####
	kepemimpinan =fields.Float('Kepemimpinan')
	plan = fields.Float('Plan, Do. Check dan Action')
	pemecah_masalah = fields.Float('Pemecahan masalah dan pengambilan keputusan')
	pendelegasian = fields.Float('Pendelegasian atau penugasan')
	tot_hasil_keterampilan = fields.Float('Total Hasil Keterampilan', readonly=True, compute="_get_totals")
