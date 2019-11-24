$(document).ready(function() {
  $("#database_credentials").submit(function(event){
     event.preventDefault();
     valid=true
     $("li.error").remove()

     $("#database_credentials input[type=text]").each(function( idx ){
       if( $(this).val()=="" ){
         form_row_id = $(this).closest("div").attr('id')
         $("#"+form_row_id).append("<li class='error'>Fill in this field.</li>")
         valid=false
       }
     })
     if(valid){
       $.post("/install/check_db",$("#database_credentials").serialize(),function(data){
          if(data.success){
            $('#installform').hide()
            $('#settingsform').show()
          }else{
            console.log(data)
            $('#database_credentials').prepend("<li class='error'>Something did not go according to plan. Check your information for typos.<br>"+data[1])
          }
       })
     }
  })

  $("#settingsform").submit(function(event){
     event.preventDefault();
     valid=true
     $("li.error").remove()

     $("#settings input[type=text]").each(function( idx ){
       if( $(this).val()=="" ){
         form_row_id = $(this).closest("div").attr('id')
         $("#"+form_row_id).append("<li class='error'>Fill in this field.</li>")
         valid=false
       }
     })
     if(valid){
       creds = $("#database_credentials").serialize()
       settings = $("#settings").serialize()
       data = creds+"&"+settings
       $.post("/install/settings",data,function(data){
          if(data.success){
            $('#settingsform').hide()
            $('#finalform').show()
          }else{
            $('#settingsform form').prepend("<li class='error'>Something did not go according to plan. Check your information for typos.")
          }
       })
     }
  })

})
