# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools


class hr_mutabaah_detail(models.Model):
    _name = 'hr.mutabaah.detail'

    hr_mutabaah_id = fields.Many2one('hr.mutabaah')
    name = fields.Date(required=True, string="Tanggal")
    ashar = fields.Boolean(string="Sholat Ashar Berjamaah", default=False)
    maghrib = fields.Boolean(string="Sholat Maghrib Berjamaah", default=False)
    isya = fields.Boolean(string="Sholat Isya Berjamaah", default=False)
    tahajjud = fields.Boolean(string="Sholat Tahajjud", default=False)
    dzikirpagi = fields.Boolean(string="Dzikir Pagi", default=False)
    dzikirsore = fields.Boolean(string="Dzikir Sore", default=False)
    infaq = fields.Boolean(string="Infaq/Shadaqah", default=False)
    kajianpagi = fields.Boolean(string="Kajian Kamis Pagi", default=False)
    bina = fields.Boolean(string="Bina Ruhiyah", default=False)
    MQ = fields.Boolean(string="Kajian MQ Kamis", default=False)
    dhuha = fields.Boolean(string="Sholat Dhuha", default=False)
    tilawah = fields.Char()
    shaum = fields.Boolean(string="Shaum Sunnah Senin-Kamis", default=False)
    itikaf = fields.Boolean(string="I'tikaf", default=False)
    zuhur = fields.Boolean(string="Sholat Zuhur Berjamaah", default=False)
    shubuh = fields.Boolean(string="Sholat Shubuh Berjamaah", default=False)


class hr_mutabaah(models.Model):
    _name = 'hr.mutabaah'

    name = fields.Many2one('hr.employee')
    description = fields.Text()
    mutabaah_detail_ids = fields.One2many('hr.mutabaah.detail', 'hr_mutabaah_id', string="Detail")
    subuh_count = fields.Integer('Jum Sholat Shubuh', compute='_get_jum_sholat_subuh', store=True)
    zuhur_count = fields.Integer('Jum Sholat Zuhur', compute='_get_jum_sholat_zuhur', store=True)
    ashar_count = fields.Integer('Jum Sholat Ashar', compute='_get_jum_sholat_ashar', store=True)
    maghrib_count = fields.Integer('Jum Sholat Magrib', compute='_get_jum_sholat_maghrib', store=True)
    isya_count = fields.Integer('Jum Sholat Isya', compute='_get_jum_sholat_isya', store=True)
    tilawah_count = fields.Integer('Jum Tilawah', compute='_get_jum_tilawah', store=True)

    @api.depends('mutabaah_detail_ids')
    def _get_jum_sholat_subuh(self):
        mutabaahs = self.mutabaah_detail_ids
        countSubuh = 0
        for mutabaah in mutabaahs:
            if mutabaah.shubuh:
                countSubuh += 1
        self.subuh_count = countSubuh

    @api.depends('mutabaah_detail_ids')
    def _get_jum_sholat_zuhur(self):
        mutabaahs = self.mutabaah_detail_ids
        countZuhur = 0
        for mutabaah in mutabaahs:
            if mutabaah.zuhur:
                countZuhur += 1
        self.zuhur_count = countZuhur

    @api.depends('mutabaah_detail_ids')
    def _get_jum_sholat_ashar(self):
        mutabaahs = self.mutabaah_detail_ids
        countAshar = 0
        for mutabaah in mutabaahs:
            if mutabaah.ashar:
                countAshar += 1
        self.ashar_count = countAshar

    @api.depends('mutabaah_detail_ids')
    def _get_jum_sholat_maghrib(self):
        mutabaahs = self.mutabaah_detail_ids
        countMaghrib = 0
        for mutabaah in mutabaahs:
            if mutabaah.maghrib:
                countMaghrib += 1
        self.maghrib_count = countMaghrib

    @api.depends('mutabaah_detail_ids')
    def _get_jum_sholat_isya(self):
        mutabaahs = self.mutabaah_detail_ids
        countIsya = 0
        for mutabaah in mutabaahs:
            if mutabaah.isya:
                countIsya += 1
        self.isya_count = countIsya

    @api.depends('mutabaah_detail_ids')
    def _get_jum_tilawah(self):
        mutabaahs = self.mutabaah_detail_ids
        countTilawah = 0
        for mutabaah in mutabaahs:
            if mutabaah.tilawah:
                countTilawah += 1
        self.tilawah_count = countTilawah

class mutabaah_activity_report(models.Model):
    _name = "hr.mutabaah.report"
    _auto = False

    hr_mutabaah_id = fields.Many2one('hr.mutabaah')
    name = fields.Date(string="Tanggal", readonly=True)
    subuh_count = fields.Integer('Jum Sholat Shubuh', readonly=True)
    zuhur_count = fields.Integer('Jum Sholat Zuhur', readonly=True)
    ashar_count = fields.Integer('Jum Sholat Ashar', readonly=True)
    maghrib_count = fields.Integer('Jum Sholat Magrib', readonly=True)
    isya_count = fields.Integer('Jum Sholat Isya', readonly=True)
    tilawah = fields.Integer('Jum Tilawah', readonly=True)
    total = fields.Integer('Total', readonly=True)

    def init(self,cr):
        #cr = self.env.cr
        tools.drop_view_if_exists(cr, 'hr_mutabaah_report')
        cr.execute("""
            CREATE OR REPLACE VIEW hr_mutabaah_report AS (
                select
                    max(m.id) id,
                    m.name,
                    m.hr_mutabaah_id,
                    sum(case when shubuh=True then 1 else 0 end) subuh_count,
                    sum(case when zuhur=True then 1 else 0 end) zuhur_count,
                    sum(case when ashar=True then 1 else 0 end) ashar_count,
                    sum(case when maghrib=True then 1 else 0 end) maghrib_count,
                    sum(case when isya=True then 1 else 0 end) isya_count
                from
                    "hr_mutabaah_detail" m
                group by
                    m.name,
                    m.hr_mutabaah_id

            )""")