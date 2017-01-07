/**
 * Created by user on 12/26/2016.
 */
function getReq(id){
    $.ajax({
    		url: '/getReq',
    		type:"GET",
    		dataType: "JSON",
            data: {getid: id},
    		success: function(recs) {
                console.log(recs.res[0])
            }
		});
}