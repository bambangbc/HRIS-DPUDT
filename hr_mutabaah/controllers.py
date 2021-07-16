# -*- coding: utf-8 -*-
from openerp import http

# class HrMutabaah(http.Controller):
#     @http.route('/hr_mutabaah/hr_mutabaah/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_mutabaah/hr_mutabaah/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_mutabaah.listing', {
#             'root': '/hr_mutabaah/hr_mutabaah',
#             'objects': http.request.env['hr_mutabaah.hr_mutabaah'].search([]),
#         })

#     @http.route('/hr_mutabaah/hr_mutabaah/objects/<model("hr_mutabaah.hr_mutabaah"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_mutabaah.object', {
#             'object': obj
#         })