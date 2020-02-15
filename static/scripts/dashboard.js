$(document).ready(function(){
$('input:radio[]').change(
    function(){
        console.log('inside function')
        if ($(this).is(':checked')) {
            console.log('inside checked',$(this).is(':checked'))
            $.ajax({
                method: "POST",   // we are using a post request here, but this could also be done with a get
                url: "/interest",
                data: {"value": $(this).val()}
            }).done(function(res){
                      console.log(res)
             })
        }
    });
    // $('#username').keyup(function(){
    //     var data = $("#regForm").serialize()   // capture all the data in the form in the variable data
    //     $.ajax({
    //         method: "POST",   // we are using a post request here, but this could also be done with a get
    //         url: "/username",
    //         data: data
    //     })
    //     .done(function(res){
    //          $('#usernameMsg').html(res)  // manipulate the dom when the response comes back
    //     })
    // })
})