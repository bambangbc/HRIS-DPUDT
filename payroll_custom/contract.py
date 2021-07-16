from openerp.osv import fields, osv
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    _columns = {
        'jenis_tunjangan'       : fields.many2one('hr.contract_tunjangan', 'Grade'),
        "tunj_jabatan"          : fields.float("Tunjangan Jabatan"),
        "tunj_makan"            : fields.float("Tunjangan Makan"),
        "tunj_transport"        : fields.float("Tunjangan Transport"),
        "tunj_istri"            : fields.float("Tunjangan Istri"),
        "tunj_balita"           : fields.float("Tunjangan Balita"),
        "tunj_tk"               : fields.float("Tunjangan TK"),
        "tunj_sd"               : fields.float("Tunjangan SD"),
        "tunj_smp"              : fields.float("Tunjangan SMP"),
        "tunj_sma"              : fields.float("Tunjangan SMU"),
        "tunj_pt"               : fields.float("Tunjangan PT"),
        "tunj_bpjs"             : fields.float("Tunjangan BPJS"),
        "tunj_cabang"           : fields.float("Tunjangan Cabang"),
        "tunj_penugasan"        : fields.float("Tunjangan Penugasan"),
        "tunj_v_belanja"        : fields.float("Tunjangan Voucher Belanja"),
        "lokasi_kerja"          : fields.many2one('hr.lokasi','Lokasi Kerja'),           
        "pot_kesehatan"         : fields.float("Iuran Kesehatan"),
        "pot_jamsostek"         : fields.float("Iuran Jamsostek"),
        "pot_koperasi"          : fields.float("Iuran Koperasi"),
        "pot_arisan"            : fields.float("Iuran Arisan"),
        "pot_parkir"            : fields.float("Iuran Parkir"),
        "pot_wakaf"             : fields.float("Potongan Wakaf"),
        "pot_pensiun"           : fields.float("Potongan Pensiun"),
        "pot_alianz"            : fields.float("Potongan Pensiun Alianz"),
    }
    
hr_contract()

class hr_lokasi(osv.osv):
    _name = 'hr.lokasi'

    _columns = {
        "name" : fields.char('Nama'),
        "tunjangan" : fields.float('Tunjangan'),
    }
hr_lokasi()

class hr_contract_tunjangan(osv.osv):
    _name = 'hr.contract_tunjangan'

    _columns = {
        "name"              : fields.char("Golongan"),
        "tunj_jabatan"      : fields.float("Bea Pokok"),
        "tunj_kompetensi"   : fields.float("Tunjangan Kompetensi"),
        "tunj_makan"        : fields.float("Tunjangan Makan"),
        "tunj_transport"    : fields.float("Tunjangan Transport"),
        "tunj_istri"        : fields.float("Tunjangan Istri"),
        }

hr_contract_tunjangan()


class hr_contract_tunjangan(osv.osv):
    _name = 'hr.contract_tunjangan'

    _columns = {
    	"name"              : fields.char("Golongan"),
        "tunj_jabatan"      : fields.float("Bea Pokok"),
        "tunj_kompetensi"   : fields.float("Tunjangan Kompetensi"),
        "tunj_makan"        : fields.float("Tunjangan Makan"),
        "tunj_transport"    : fields.float("Tunjangan Transport"),
        "tunj_istri"        : fields.float("Tunjangan Istri"),
        }

hr_contract_tunjangan()

class hr_bpjs(osv.osv):
    _name = 'hr.contract.type'
    _inherit = 'hr.contract.type'

    _columns = {
        "bpjskes_karyawan" : fields.float('BPJS Kesehatan di bayar oleh Karyawan dalam %'),
        "bpjskes_perusahaan" : fields.float("BPJS Kesehatan di bayar oleh perusahaan dalam %"),
        "bpjsten_karyawan" : fields.float('BPJS Tenagakerja di bayar oleh Karyawan dalam %'),
        "bpjsten_perusahaan" : fields.float("BPJS Tenagakerja di bayar oleh perusahaan dalam %"),
        }
hr_bpjs()