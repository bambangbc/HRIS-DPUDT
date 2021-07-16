# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.web.controllers.main import ExcelExport
import openerp.addons.web.http as openerpweb
from openerp.http import request
try:
    import xlwt
except ImportError:
    xlwt = None
try:
    import json
except ImportError:
    import simplejson as json
from cStringIO import StringIO

class XportXcel(ExcelExport):
    _cp_path = '/xport_xcel/xport_xcel'

    def create_xls(self, fields, rows):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        Payslip = pool['hr.payslip']
        style0 = xlwt.easyxf('font: name Times New Roman, color-index black, bold on',num_format_str='#,##0.00')
        style1 = xlwt.easyxf(num_format_str='D-MMM-YY')
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Sheet 1')
        heads = fields[0]['data'] #['Acc. No.','Trans. Amount','emp.Number','emp.Name','Dept','Trans. Date']
        x=0
        data=''
        for head in heads:
            ws.write(0,x,head,style0)
            x+=1
        for row in rows:
            slip_ids = Payslip.search(cr,uid,[('date_from','>=',row['datefrom']),('date_to','<=',row['dateto'])], context=context)
            payslips = Payslip.browse(cr, uid, slip_ids, context=context)
            payslip=[]
            for p in payslips:
                paid = 0.0;x=0;data=''
                payslip.append(p.id)
                kehadiran = [line[0].number_of_days for line in p.worked_days_line_ids if line.code == 'PRESENCES']
                if kehadiran:
                    H = kehadiran[0]
                else:
                    H = 0.0
                gross=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'GROSS']
                if gross:
                    gross=gross[0]
                else:
                    gross=0.0
                net=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'NET']
                if net:
                    net=net[0]
                else:
                    net=0.0
                basic=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'BASIC']
                if basic:
                    basic=basic[0]
                else:
                    basic=0.0
                TI=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TI']
                if TI:
                    TI=TI[0]
                else:
                    TI=0.0
                BALITA=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'BALITA']
                if BALITA:
                    BALITA=BALITA[0]
                else:
                    BALITA=0.0
                TK=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TK']
                if TK:
                    TK=TK[0]
                else:
                    TK=0.0
                SD=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'SD']
                if SD:
                    SD=SD[0]
                else:
                    SD=0.0
                SMP=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'SMP']
                if SMP:
                    SMP=SMP[0]
                else:
                    SMP=0.0
                SMA=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'SMA']
                if SMA:
                    SMA=SMA[0]
                else:
                    SMA=0.0
                PT=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PT']
                if PT:
                    PT=PT[0]
                else:
                    PT=0.0
                TJM=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TJM']
                if TJM:
                    TJM=TJM[0]
                else:
                    TJM=0.0
                TJT=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TJT']
                if TJT:
                    TJT=TJT[0]
                else:
                    TJT=0.0
                TBPJS=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TBPJS']
                if TBPJS:
                    TBPJS=TBPJS[0]
                else:
                    TBPJS=0.0
                TKO=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TKO']
                if TKO:
                    TKO=TKO[0]
                else:
                    TKO=0.0
                TJP=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TJP']
                if TJP:
                    TJP=TJP[0]
                else:
                    TJP=0.0
                TKM=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TKM']
                if TKM:
                    TKM=TKM[0]
                else:
                    TKM=0.0
                KBL=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'KBL']
                if KBL:
                    KBL=KBL[0]
                else:
                    KBL=0.0
                OVERTIME=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'OVERTIME']
                if OVERTIME:
                    OVERTIME=OVERTIME[0]
                else:
                    OVERTIME=0.0
                TKD=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TKD']
                if TKD:
                    TKD=TKD[0]
                else:
                    TKD=0.0
                TPN=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'TPN']
                if TPN:
                    TPN=TPN[0]
                else:
                    TPN=0.0
                PDPU=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PDPU']
                if PDPU:
                    PDPU=PDPU[0]
                else:
                    PDPU=0.0
                IK=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'IK']
                if IK:
                    IK=IK[0]
                else:
                    IK=0.0
                PIJ=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PIJ']
                if PIJ:
                    PIJ=PIJ[0]
                else:
                    PIJ=0.0
                PK1=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PK1']
                if PK1:
                    PK1=PK1[0]
                else:
                    PK1=0.0
                PK2=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PK2']
                if PK2:
                    PK2=PK2[0]
                else:
                    PK2=0.0
                PK3=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PK3']
                if PK3:
                    PK3=PK3[0]
                else:
                    PK3=0.0
                PK4=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PK4']
                if PK4:
                    PK4=PK4[0]
                else:
                    PK4=0.0
                TOT_POT = PK1+PK2+PK3+PK4
                PIK=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PIK']
                if PIK:
                    PIK=PIK[0]
                else:
                    PIK=0.0
                PZ=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PZ']
                if PZ:
                    PZ=PZ[0]
                else:
                    PZ=0.0
                PW=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PW']
                if PW:
                    PW=PW[0]
                else:
                    PW=0.0
                PA=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PA']
                if PA:
                    PA=PA[0]
                else:
                    PA=0.0
                PPA=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PPA']
                if PPA:
                    PPA=PPA[0]
                else:
                    PPA=0.0
                PQ=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PQ']
                if PQ:
                    PQ=PQ[0]
                else:
                    PQ=0.0
                PP=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PP']
                if PP:
                    PP=PP[0]
                else:
                    PP=0.0
                PLL=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PLL']
                if PLL:
                    PLL=PLL[0]
                else:
                    PLL=0.0
                PL2=[line[0].total for line in p.details_by_salary_rule_category if line.code == 'PL2']
                if PL2:
                    PL2=PL2[0]
                else:
                    PL2=0.0
                ws.write(len(payslip),0,p.employee_id.name)
                ws.write(len(payslip),1,p.employee_id.address_id2.name)
                ws.write(len(payslip),2,p.employee_id.job_id.name)
                ws.write(len(payslip),3,p.employee_id.type_id.name)
                ws.write(len(payslip),4,p.contract_id.type_id.name)
                ws.write(len(payslip),5,p.employee_id.mulai_kerja)
                ws.write(len(payslip),6,p.employee_id.marital)
                ws.write(len(payslip),7,p.employee_id.jml_istri)
                ws.write(len(payslip),8,p.employee_id.children)
                ws.write(len(payslip),9,p.employee_id.jml_tk)
                ws.write(len(payslip),10,p.employee_id.jml_sd)
                ws.write(len(payslip),11,p.employee_id.jml_smp)
                ws.write(len(payslip),12,p.employee_id.jml_sma)
                ws.write(len(payslip),13,p.employee_id.jml_pt)
                ws.write(len(payslip),14,H)
                ws.write(len(payslip),15,p.employee_id.bank_account_id.acc_number)
                ws.write(len(payslip),16,gross)
                ws.write(len(payslip),17,net)
                ws.write(len(payslip),18,basic)
                ws.write(len(payslip),19,p.contract_id.jenis_tunjangan.name)
                ws.write(len(payslip),20,p.contract_id.jenis_tunjangan.tunj_jabatan)
                ws.write(len(payslip),21,TI)
                ws.write(len(payslip),22,BALITA)
                ws.write(len(payslip),23,TK)
                ws.write(len(payslip),24,SD)
                ws.write(len(payslip),25,SMP)
                ws.write(len(payslip),26,SMA)
                ws.write(len(payslip),27,PT)
                ws.write(len(payslip),28,TJM)
                ws.write(len(payslip),29,TJT)
                ws.write(len(payslip),30,TBPJS)
                ws.write(len(payslip),31,TKO)
                ws.write(len(payslip),32,TJP)
                ws.write(len(payslip),33,TKM)
                ws.write(len(payslip),34,KBL)
                ws.write(len(payslip),35,OVERTIME)
                ws.write(len(payslip),36,TKD)
                ws.write(len(payslip),37,TPN)
                ws.write(len(payslip),38,PDPU)
                ws.write(len(payslip),39,IK)
                ws.write(len(payslip),40,PIJ)
                ws.write(len(payslip),41,PK1)
                ws.write(len(payslip),42,PK2)
                ws.write(len(payslip),43,PK3)
                ws.write(len(payslip),44,PK4)
                ws.write(len(payslip),45,TOT_POT)
                ws.write(len(payslip),46,TPN)
                ws.write(len(payslip),47,PIK)
                ws.write(len(payslip),48,PZ)
                ws.write(len(payslip),49,PW)
                ws.write(len(payslip),50,PA)
                ws.write(len(payslip),51,PPA)
                ws.write(len(payslip),52,PLL)
                ws.write(len(payslip),53,PQ)
                ws.write(len(payslip),54,PP)
                ws.write(len(payslip),55,PL2)
        fp = StringIO()
        wb.save(fp)
        fp.seek(0)
        xlsdata = fp.read()
        fp.close()
        return xlsdata
        
    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        return req.make_response(
            self.create_xls(data.get('headers', []), data.get('rows', [])),
                           headers=[
                                    ('Content-Disposition', 'attachment; filename="%s"'
                                        % data.get('model', 'export.xls')),
                                    ('Content-Type', self.content_type)
                                    ],
                                 cookies={'fileToken': token}
                                 )