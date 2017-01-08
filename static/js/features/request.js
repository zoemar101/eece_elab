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
                $("#reqrID").text("")
                $("#reqrID").text(recs.res[0].id)

                for (i = 0; i < recs.count; i++){
                        itmQuan = recs.res[i].itemquan
                        itmCode = recs.res[i].itemcode
                        itmName = recs.res[i].itemname

                        var x = document.getElementById("reqItems").rows.length;
                        var table = document.getElementById("reqItems");

                            var row = table.insertRow(x);
                            var cell1 = row.insertCell(0);
                            var cell2 = row.insertCell(1);
                            var cell3 = row.insertCell(2);
                            var cell4 = row.insertCell(3);
                            cell1.innerHTML = itmQuan;
                            cell2.innerHTML = itmCode;
                            cell3.innerHTML = itmName;
                            cell4.innerHTML = '<button class="btn btn-default" > Release </button>'

                }

                console.log(recs.res[0])
            }
		});
}