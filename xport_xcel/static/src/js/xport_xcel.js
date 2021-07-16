openerp.xport_xcel = function(instance, m) {
    
    var _t = instance.web._t,
    QWeb = instance.web.qweb;
    
    instance.web.FormView.include({
        load_form: function(data) {
            var self = this;
            this._super.apply(this, arguments);
            self.$el.find('.oe_xdates').append(QWeb.render('xportxcel', {widget: self}));
            self.$el.find('.oe_xport').unbind('click').click(function(event){self.on_xport_excel("excel")})
        },

        on_xport_excel: function (export_type) {
            var self = this
            var view = this.getParent()
            dates=[]
            header_list=[]
        	datefrom 	= self.$el.find('.oe_dt_from > span > input')
            $from = $(datefrom).datepicker( "getDate" )
            datefrom = $from.getFullYear() + "-" + ($from.getMonth()+1) + "-" + $from.getDate()
        	
        	dateto 		= self.$el.find('.oe_dt_to > span > input')
            $to = $(dateto).datepicker( "getDate" )
            dateto = $to.getFullYear() + "-" + ($to.getMonth()+1) + "-" + $to.getDate()
        	
        	/*datetrf 	= self.$el.find('.oe_dt_trf > span > input')
            $trf = $(datetrf).datepicker( "getDate" )
            datetrf = $trf.getFullYear() + "-" + ($trf.getMonth()+1) + "-" + $trf.getDate()*/

            dates.push({'datefrom':datefrom,'dateto':dateto})
        	header_list.push({'data': ['Nama','Unit Kerja','Jabatan/Amanah','PDDK','Status Kerja','Mulai Kerja','Status','Istri','Balita','TK','SD','SMP','SMA','PT',"Hari Kerja",'No Rekening','Gaji Kotor','Gaji Bersih','Gaji Pokok','Grade','Bea Pokok','Tunjangan Istri','Tunjangan Balita','Tunjangan TK','Tunjangan SD','Tunjangan SMP','Tunjangan SMA','Tunjangan PT','Tunjangan Transport','Tunjangan Makan','Tunjangan BPJS','Tunjangan Kompetensi','Tunjangan Penyesuaian','Tunjangan Kemahalan','Kekurangan Bulan Lalu','Lembur','Tj.Kedisiplinan','Tunjangan Pensiun','Pot DPU','Iuran Kesehatan','Iuran Jamsostek','Pot Terlambat 1-15mnt','Pot Terlambat 15-60mnt','Pot Terlambat 60-3jam','Pot Terlambat >3jam','Tot Pot Terlambar','Potongan Pensiun','Koperasi','Ziswa DPU','Wakaf','Potongan Arisan','Potongan Pensiun & Alianz','Potongan Lain2','Potongan Kurban','Pot Parkir','Pot Lain2']})
            var str2 = new Date().toJSON().slice(0,10)
            var models = 'Transfer_per_'.concat(str2).concat('.xls')

        	//Export to excel
            $.blockUI();
            //if (export_type === 'excel'){
                view.session.get_file({
                    url: '/xport_xcel/xport_xcel',
                    data: {data: JSON.stringify({
                            model :models,
                            headers : header_list,
                            rows : dates,
                    })},
                    complete: $.unblockUI
                });
            //}
        },
    });
};