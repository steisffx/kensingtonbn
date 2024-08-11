$(document).ready(function () {
    suggested();
    bestvalue();
    recommended();
});

var suggested = function() {
    let me = this;
    frappe.call({
        method: 'kensingtonbn.www.pages.recommended.get_suggested_items_html',
        callback: function(r) {
            if (!r.exc) {
                jQuery('#placeholdersuggested').html('');
    
                if(typeof r.message != 'undefined'){             
                $(r.message).appendTo('#placeholdersuggested');
                
                }
            }
        }
    });
}

var bestvalue = function(){
    
    frappe.call({
       method: 'kensingtonbn.www.pages.recommended.get_bestvalue_items_html',
       callback: function(r) {
           if (!r.exc) {
               jQuery('#placeholderbestvalue').html('');
   
               if(typeof r.message != 'undefined'){              
   
                   $(r.message).appendTo('#placeholderbestvalue');
   
               }
           }
       }
   });

}

var recommended = function(){
    
    frappe.call({
       method: 'kensingtonbn.www.pages.recommended.get_recommended_items_html',
       callback: function(r) {
           if (!r.exc) {
               jQuery('#placeholderrecommended').html('');
   
               if(typeof r.message != 'undefined'){              
   
                   $(r.message).appendTo('#placeholderrecommended');
   
               }
           }
       }
   });

}