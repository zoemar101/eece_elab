/**
 * Created by user on 12/15/2016.
 */
$(document).ready(function(){
    $("#addAcc").click(function(){
        $.ajax({
    		url: '/manAccount',
    		type:"GET",
    		data: {delid: id},
    		success: function() {



                $("#foraddAcc").show();
                $("#formanAcc").hide();
            }
		});


    });

    $("#manAcc").click(function(){
       $("#formanAcc").show();
        $("#foraddAcc").hide();
    });

});