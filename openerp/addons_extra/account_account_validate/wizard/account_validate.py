from openerp.osv import fields, osv

class account_account_validate(osv.osv):
    _name = 'account.account.validate'
    
    def validate(self,cr, uid, ids, context=None):
        obj = self.pool.get('account.account')
        ids_accounts = obj.search(cr,uid,[],0, None)
        account_model = {}
        ids_to_verify = []
        
        for line in obj.browse(cr, uid, ids_accounts):
            code = line.code
            digits = len(code)
            if digits == 9:
                if code[8]=='0':
                    account_model[line.code]={'user_type': line.user_type.id,
                                              'level':line.level,
                                              'parent_id':line.parent_id.id,
                                              'type': line.type,
                                              }
                else:
                    ids_to_verify.append([line.id,line.code])
        # the method write is slowly than cr.execute but cr.execute don't recalculate the parent_left and right
        cr.execute('ALTER TABLE account_account DROP COLUMN parent_left;')
        cr.execute('ALTER TABLE account_account DROP COLUMN parent_right;')
        for line in ids_to_verify:
            for digits in range(4,0,-1):
                zeros = '0'*(9 - digits)
                account_parent = line[1][:digits] + zeros
                model = account_model.get(account_parent)
                if model:
                    cr.execute('update account_account set user_type=%s, level=%s, type=%s, parent_id=%s where id=%s;',(model.get('user_type'), model.get('level'), model.get('type'),model.get('parent_id'), line[0]))   
                    #obj.write(cr, uid,line[0],{'parent_id': model.get('parent_id')})
                    break
        
        return {
                'type': 'ir.actions.act_window_close',
         }
    
    
    