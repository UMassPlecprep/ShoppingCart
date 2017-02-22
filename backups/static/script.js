var ip = "54.146.133.213";
var to_remove = {}

function edit_prof_list(){
    $(".edit_professor_list").toggle();
    $(".edit_schedule").css("display","none");
    $(".edit_utils").css("display","none");
    $(document).scrollTop( 800 );
}

function edit_schedule(){
    $(".edit_schedule").toggle();
    $(".edit_professor_list").css("display","none");
    $(".edit_utils").css("display","none");
    $(document).scrollTop( 800 );
}

function edit_util(){
    $(".edit_utils").toggle();
    $(".edit_schedule").css("display","none");
    $(".edit_professor_list").css("display","none");
    $(document).scrollTop( 800 );
}

function remove_class(l){
    if(to_remove[l[0]] == undefined){
        to_remove[l[0]] = [l[1]];
        $("."+l[1]).css("background-color","red");
        return
    }
    else{
        c = to_remove[l[0]];
        i = c.indexOf(l[1]);
        if(i > -1){
            delete c[i]
            $("."+l[1]).css("background-color","white");
            return;
        }
        to_remove[l[0]].push(l[1]);
        $("."+l[1]).css("background-color","red");
    }
}

function purge(){
    data = JSON.stringify(to_remove);
    $.post("/removeSchedule",{"data":data});
}

function onLoad(){
    var cal_start, cal_end, d1, d2;
    cal_start = new dhtmlXCalendarObject("starting_cal");
    cal_end   = new dhtmlXCalendarObject("ending_cal");
    cal_start.hideTime(); cal_end.hideTime();
    d1 = cal_start.getDate(); d2 = cal_end.getDate();
    cal_start.attachEvent("onClick", function(date){ d1 = date; });
    cal_end.attachEvent("onClick", function(date){ d2 = date; });
}

$(".option-button").hover(function(){
    $(this).siblings().css('opacity','1');
});

$(".option-button").mouseout(function(){
    $(this).siblings().css('opacity','0');
});

/*function edit_form_append(){
    var splitted, c, prof, time, days, room
    splitted = $("#edit_schedule_selection").value;
    c = splitted[0];
    prof = splitted[1];
    time = splitted[2];
    days = splitted[3];
    room = splitted[4];
    html = "";
    $("#editForm").innerHTML();
}
*/
$(document).ready(function(){
    onLoad();
});
