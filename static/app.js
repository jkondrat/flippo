
function commaSeparateNumber(val){
    var i = 0;
    while (/(\d+)(\d{2})/.test(val.toString()) && i < 2){
        val = val.toString().replace(/(\d+)(\d{2})/, '$1'+','+'$2');
        i++;
    }
    return val;
}

function updateProgressBar() {
$.get("items/refresh/status/", function (data) {
    $("#progress").html(data.progress + "% (" + data.curr + "/" + data.total + ")");
});
}

var fetching = false;
$(function() {
    nodes = document.querySelectorAll(".commaSeparated");
    for (var i = 0; i < nodes.length; i++) {
        nodes[i].innerHTML = commaSeparateNumber(nodes[i].innerHTML);
    }
    $( "#clear" ).click(function(e) {
        $(".form-control").val('');
    });
    $( "#refresh-prices" ).click(function() {
        if (!fetching) {
            fetching = true;
            var timer = setInterval(updateProgressBar, 5000);
            $(".glyphicon-refresh").addClass("rotate");
            $.get("items/refresh/all-prices/", function (data) {
                $(".glyphicon-refresh").removeClass("rotate");
                clearInterval(timer);
                console.log(data);
                fetching = false;
                $("#progress").html("");
            });
        }
    });
    $('.pagination').children().each(function(){
        var anchor = $(this).find('a');
        if (anchor) {
            anchor.attr('href', '?q=' + q + '&type=' + type + '&count=' + count + '&buy_price=' + buy_price + '' +
                '&page=' + anchor.html());
        }
    });
});