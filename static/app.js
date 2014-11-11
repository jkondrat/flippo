function commaSeparateNumber(val){
    var g, s, c;
    if(val.length > 4) {
        g = val.substring(0, val.length - 4);
        s = +val.substring(val.length - 4, val.length - 2);
        c = +val.substring(val.length-2, val.length);
    } else if (val.length > 2) {
        s = val.substring(0, val.length - 2);
        c = +val.substring(val.length-2, val.length);
    } else {
        c = val;
    }
    var html = "";
    if (g !== undefined) {
        html += "<span class=\"g\">" + g + "g</span> ";
    }
    if (s !== undefined) {
        html += "<span class=\"s\">" + s + "s</span> ";
    }
    return html + "<span class=\"c\">" + c + "c</span> ";
}

var fetching = false;
function setFetching(f) {
    if (fetching != f) {
        if (f == true) {
            $(".refresh-all").addClass("rotate");
        } else {
            $(".refresh-all").removeClass("rotate");
        }
        fetching = f;
    }
}

var timer;
function updateProgressBar(init) {
$.get("/items/refresh/status/", function (data) {
    console.log(data);
    if(init || data.working && data.working == true) {
        setFetching(true);
        if (init) {
            $("#progress").html("0% (?/?)");
        } else {
            $("#progress").html(data.progress + "% (" + data.curr + "/" + data.total + ")");
        }
        timer = setTimeout(updateProgressBar, 5000);
    } else {
        setFetching(false);
        clearInterval(timer);
        $("#progress").html("");
    }
});
}

function updateAndAnimate(row, value) {
    if(row.html() != value) {
        row.html(value);
        row.animate({
           backgroundColor: 'green'
        }, 400);
        row.animate({
           backgroundColor: 'white'
        }, 1600);
    }
}

function addToWatchlist() {
    var s = $(this);
    $.get("/items/watchlist/add/" + s.attr("data-id") + "/", function (data) {
        s.removeClass("watchlist-add");
        s.removeClass("glyphicon-ok");
        s.addClass("watchlist-remove");
        s.addClass("glyphicon-remove");
        s.unbind('click').click(removeFromWatchlist);
    });
}

function removeFromWatchlist() {
    var s = $(this);
    $.get("/items/watchlist/remove/" + s.attr("data-id") + "/", function (data) {
        s.removeClass("watchlist-remove");
        s.removeClass("glyphicon-remove");
        s.addClass("watchlist-add");
        s.addClass("glyphicon-ok");
        s.unbind('click').click(addToWatchlist);
    });
}

var fetchingWatchlist = false;
$(function() {
    nodes = document.querySelectorAll(".commaSeparated");
    for (var i = 0; i < nodes.length; i++) {
        nodes[i].innerHTML = commaSeparateNumber(nodes[i].innerHTML);
    }
    $( "#clear" ).click(function() {
        $(".form-control").val('');
    });

    updateProgressBar();
    $( "#refresh-prices" ).click(function() {
        if (!fetching) {
            $.get("/items/refresh/all-prices/", function (data) {
                //updateProgressBar();
                if (data.result == "ok") {
                    location.reload();
                }
                else if (data.result == "unauthorized") {
                    window.location.href = "/login/?next=/items/watchlist/";
                }
            });
            updateProgressBar(true);
        }
    });

    $('.pagination').children().each(function() {
        var anchor = $(this).find('a');
        if (anchor) {
            anchor.attr('href', '?q=' + q + '&type=' + type + '&rarity=' + rarity + '&level=' + level +
                '&count=' + count + '&buy_price=' + buy_price + '' +
                '&page=' + anchor.html());
        }
    });

    $(".refresh-item").click(function() {
        var a = $(this);
        var row = a.parent().parent();
        a.addClass("rotate");
        $.get("/items/refresh/price/" + a.attr("data-id") + "/", function (data) {
            //updateProgressBar();
            if (data.result && data.result == "ok") {
                var item = JSON.parse(data.item)[0].fields;
                var market = JSON.parse(data.market)[0].fields;
                a.removeClass("rotate");
                updateAndAnimate(row.find('[data-col="profit"]'), commaSeparateNumber(String(item.profit)));
                updateAndAnimate(row.find('[data-col="profit_percent"]'), String(item.profit_percent));
                updateAndAnimate(row.find('[data-col="sell_price"]'), commaSeparateNumber(String(market.sell_price)));
                updateAndAnimate(row.find('[data-col="buy_price"]'), commaSeparateNumber(String(market.buy_price)));
                updateAndAnimate(row.find('[data-col="sell_quantity"]'), String(market.sell_quantity));
            }
        });
    });

    $( "#refresh-watchlist" ).click(function() {
        if (!fetchingWatchlist) {
            fetchingWatchlist = true;
            $(".refresh-watchlist").addClass("rotate");
            $.get("/items/watchlist/refresh/", function (data) {
                $(".refresh-watchlist").removeClass("rotate");
                fetchingWatchlist = false;
                console.log(data);
                if (data.result == "ok") {
                    location.reload();
                }
            });
        }
    });

    $(".watchlist-add").click(addToWatchlist);

    $(".watchlist-remove").click(removeFromWatchlist);

    $(".back").click(function() {
        window.history.go(-1);
    });

});