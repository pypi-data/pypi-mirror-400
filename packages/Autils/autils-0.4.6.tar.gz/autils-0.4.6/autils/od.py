import traceback

def run():
    try:
        import odoo
        from odoo.http import request

        print('++++++++++')
        print(request.env['ir.config_parameter'].get_param("web.base.url"))
        
    except Exception as err:
        print('+++exception++')
        traceback.print_exception(err) 
        pass