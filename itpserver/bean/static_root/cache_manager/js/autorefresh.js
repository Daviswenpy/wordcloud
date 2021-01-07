

// $('[name="_addanother"]').hide();

setInterval(function (){
    var a=$(".action-checkbox .action-select")
    var se=[]
    a.each(function() { 
    if (this.checked ==true) { 
        se.push(this.value)
    } 
    })
    sessionStorage.myhtml=JSON.stringify(se);
    // $("#result_list tbody").load(location.href+" #result_list tbody>*","")
    $(".results").load(location.href+" .results>*","")


    setTimeout(function(){
        se=JSON.parse(sessionStorage.getItem("myhtml"))

        se.forEach(function(i){
            $('[value="' +i+'"]')[0].checked=true
            $('[value="' +i+'"]')[0].setAttribute("checked", "checked");
            $('[value="' +i+'"]').parent().parent().addClass("selected");
        })
    }, 200);
},10000);
