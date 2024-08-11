// Sync Load Repeater Result
var ScrollTimeOut = null, WindowHeight, ScrollTop;
// var Block01, Block01length = 0, Block01Loaded = false;

$(document).ready(function () {

    getproducts(1);

    // Block01length = $("#Block01").length;

    $(window).scroll(function () {
        if (ScrollTimeOut == null) {
            ScrollTimeOut = setTimeout(function () {
                WindowHeight = $(window).height();
                ScrollTop = $(this).scrollTop();

                $('.navbar').toggleClass('applybgdark', ScrollTop > 50);              

                // if (Block01length > 0) {
                //     Block01 = $("#AccountsBlock").offset().top;
                //     if (!Block01Loaded && (ScrollTop > (Block01 - WindowHeight))) {
                //         $("#BuLoadAccounts").click();
                //     }
                    
                // }


                clearTimeout(ScrollTimeOut);
                ScrollTimeOut = null;
            }, 200);
        }
    });
    $(window).scroll();


});


var getproducts = function(sectionnum){
    
    frappe.call({
       method: 'kensingtonbn.www.pages.index.get_productlist_html',
       args: {
           sn: sectionnum
       },
       callback: function(r) {
           if (!r.exc) {
               jQuery('#placeholdersection' + sectionnum).html('');
   
               if(typeof r.message != 'undefined'){              
   
                   $(r.message).appendTo('#placeholdersection' + sectionnum);
   
               }
   
               if (sectionnum < 4)
               {
                   setTimeout(() => {
                       getproducts(sectionnum + 1);    
                   }, 500);
                   
               }
           }
       }
   });

}