// Sync Load Repeater Result

var ScrollTimeOut = null, WindowHeight, ScrollTop;
// var Block01, Block01length = 0, Block01Loaded = false;

$(document).ready(function () {

    getproducts(1);
    getslideshow(1); 



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
       method: 'kensingtonbn.www.pages.main.get_productlist_html',
       args: {
           sn: sectionnum
       },
       callback: function(r) {
           if (!r.exc) {
               jQuery('#placeholdersection' + sectionnum).html('');
   
               if(typeof r.message != 'undefined'){              
   
                   $(r.message).appendTo('#placeholdersection' + sectionnum);
                   BindHorizontalScroll("#placeholdersection" + sectionnum, 1, true);
   
               }
   
               if (sectionnum < 6)
               {
                    getproducts(sectionnum + 1);  
                   
               }
                              
                

           }
       }
   });

}

// my update 
var getslideshow = function(sectionnum){
    
    frappe.call({
       method: 'kensingtonbn.www.pages.main.get_slideshow_html',
       args: {
           sn: sectionnum
       },
       callback: function(r) {
           if (!r.exc) {
               jQuery('#advertisingsection' + sectionnum).html('');
   
               if(typeof r.message != 'undefined'){              
   
                   $(r.message).appendTo('#advertisingsection' + sectionnum);
                //    BindHorizontalScroll("#advertisingsection" + sectionnum, 1, true);
   
               }
   
               if (sectionnum < 2)
               {
                    getslideshow(sectionnum + 1);  
                   
               }
           }
       }
   });

}

// get discount price info
// $(document).ready(function(){

//     frappe.call({
//         method: "kensingtonbn.www.pages.discount_test.get_productinfo_html" ,
//         callback: function(r) {
//            console.log('test');
//         }
//     })
// });
// ---------------------------------------------------------------------
