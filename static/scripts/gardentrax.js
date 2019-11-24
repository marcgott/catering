$(document).ready(function() {
            $(".logform").submit(function(event){
               event.preventDefault();
               //alert( "Default behavior is disabled!" );
               form_row_action = $(this).closest("form").attr('action')
               form_row_id = $(this).closest("form").attr('id')
               $.post(form_row_action,$("#"+form_row_id).serialize(),function(data){
                 $("#"+form_row_id).html("<div><ul><li class='info'>Log Submitted for "+$("#"+form_row_id).find("h3").text()+"</li></ul></div>")

               }).then(function(){
                 if( $('.logform').length == 1){
                   location.href='/logs'
                 }
               })
               //
            });
            $( function() {
              if( $('.environmentfield').val() == 0){
                $('.environmentfield').addClass('missing')
              }
              if( $('.stagefield').val() == 'None'){
                $('.stagefield').addClass('missing')
              }
              $( ".datefield" ).datepicker({dateFormat: 'yy-mm-dd'});
            } );
            $('#globaldate').click(function(){
              $('#globaldatefield').datepicker('show');
            });
            $('#globaldatefield').datepicker({dateFormat: 'yy-mm-dd', onSelect:
              function(dateText, inst) {
                $('.datefield').val(dateText);
              }
            });
            $('#globalwater').click(function(){
              $('.watercheck').prop('checked',true);
            });
            $('#global_environment_ID').on('change',function(){
              $('.environmentfield').removeClass('missing')
              $('.environmentfield').val($(this).val());
            });
            $('#global_nutrient_ID').on('change',function(){
              $('.nutrientfield').val($(this).val());
            });
            $('#global_repellent_ID').on('change',function(){
              $('.repellentfield').val($(this).val());
            });
            $('#global_stage').on('change',function(){
              $('.stagefield').removeClass('missing')
              $('.stagefield').val($(this).val());
            });
            $('#global_lux').on('keyup',function(){
              $('.luxfield').val($(this).val());
            });

    $(".reportlink").click(function(){
      $(".report.chart").hide()
      $("#chart_"+$(this).attr('id')).show()
    })
    //Autosets logdate in /log/new, ignored in /log/edit/# and other
    if(typeof $('.datefield').val() != 'undefined' && $('.datefield').val() =='' ){
      date = new Date()
      isodate = date.toISOString().split('T')
      $('.datefield').val(isodate[0]);
    }
    if($("#plant_strain").length){
      $.get("/api/list/strain",function(data){
        data.sort(function(a,b){
          return a.name.localeCompare( b.name );
        })
        $("#plant_strain select").empty()
          $.each(data, function(idx,obj){
            $("#plant_strain select").append('<option value="'+obj.id+'">'+obj.name+'</option>')
            })

      })
    }
    if($("#plant_cycle").length){
      $.get("/api/list/cycle",function(data){
        data.sort(function(a,b){
          return a.name.localeCompare( b.name );
        })
        $("#plant_cycle select").empty()
          $.each(data, function(idx,obj){
            $("#plant_cycle select").append('<option value="'+obj.id+'">'+obj.name+'</option>')
            })

      })
    }


});
