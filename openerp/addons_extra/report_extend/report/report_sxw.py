from __future__ import nested_scopes
from lxml import etree
from openerp.report.report_sxw import browse_record_list
from openerp.report.report_sxw import report_sxw
from openerp.report.report_sxw import rml_parse
import new

# def enhance__init__(klass, f):
#     ki = klass.__init__
#     klass.__init__ = new.instancemethod(
#         lambda *args, **kwds: f(ki, *args, **kwds),None,klass)
#     
# def new_report_sxw_init(__init__, self, *args, **kwargs):
#         __init__(self, *args, **kwargs)
#         self.internal_header=False
# 
# enhance__init__(report_sxw, new_report_sxw_init)

class report_sxw(report_sxw):
    """
    The register=True kwarg has been added to help remove the
    openerp.netsvc.LocalService() indirection and the related
    openerp.report.interface.report_int._reports dictionary:
    report_sxw registered in XML with auto=False are also registered in Python.
    In that case, they are registered in the above dictionary. Since
    registration is automatically done upon instanciation, and that
    instanciation is needed before rendering, a way was needed to
    instanciate-without-register a report. In the future, no report
    should be registered in the above dictionary and it will be dropped.
    """
        
    def __init__(self, *args, **kwargs):
        super(report_sxw, self).__init__(*args, **kwargs)
        self.internal_header=False
        #if header=='internal' or header=='internal landscape':
            #self.internal_header=True

#
# Context: {'node': node.dom}
#
class browse_record_list(browse_record_list):
    
    def setCompany(self, company_id):
        if company_id:
            self.localcontext['company'] = company_id
            self.localcontext['logo'] = company_id.logo
            self.rml_header = company_id.rml_header
            self.rml_header2 = company_id.rml_header2
            self.rml_header3 = company_id.rml_header3
            self.rml_header4 = company_id.rml_header4
            self.logo = company_id.logo
    
    def _add_header(self, rml_dom, header='external'):
        
        if header=='internal':
            rml_head =  self.rml_header2
        elif header=='internal landscape':
            rml_head =  self.rml_header3
        elif header=='shipping':
            rml_head =  self.rml_header4
        else:
            rml_head =  self.rml_header
        
        head_dom = etree.XML(rml_head)
        for tag in head_dom:
            found = rml_dom.find('.//'+tag.tag)
            if found is not None and len(found):
                if tag.get('position'):
                    found.append(tag)
                else :
                    found.getparent().replace(found,tag)
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
