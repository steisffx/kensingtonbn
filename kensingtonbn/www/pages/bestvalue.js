$(document).ready(function () {

    getproducts();
});


var getproducts = function(){
    
    frappe.call({
       method: 'kensingtonbn.www.pages.bestvalue.get_items_html',
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