"use strict";

$(function() {
    Translate.init();

    $("#from").chosen();
    $("#to").chosen();

    var from = [];

    for(var idx in Translate.pairs) {
        var pair = Translate.pairs[idx];

        // Make sure we keep only one copy of each source lang
        if(from.indexOf(pair[0]) < 0) {
            from.push(pair[0]);
        }
    }

    from = from.map(function(lang) {
        var name = getLanguageName(lang) || lang;
        return [name, lang];
    }).sort();

    from.map(function(elem) {
        $("#from").append("<option value=" + elem[1] + ">" + elem[0] +
                          "</option>");
    });

    $("#to").trigger("liszt:updated");
    $("#from").trigger("liszt:updated");

    $("#from").chosen().change(function() {
        var selected = $("#from").val();

        $("#to").html("<option value=''></option>");

        var langs = Translate.getToChoices(selected).map(function(code) {
            var name = getLanguageName(code) || code;
            return [name, code];
        }).sort();


        langs.map(function(lang) {
            $("#to").append("<option value=" + lang[1] + ">" + lang[0] +
                            "</option>");
        });

        $("#to").trigger("liszt:updated");
    });

    $("#translate").click(function() {
        var text = $("#from_area").val();
        var from = $("#from").val(), to = $("#to").val();

        if(text == "") {
            // Don't need to be noisy, just exit
            return;
        }

        if(from == "" || to == "") {
            Translate.error("Select a language!");
            return;
        }

        Translate.translateText(text, from, to);
    });

});


var Translate = {};

Translate.init = function() {
    Translate.getPairs();
};

Translate.getPairs = function() {
    $.ajax({
        dataType: 'json',
        url: '/api/v1/pairs',
        async: false,
        success: function(data) {
            Translate.pairs = data.pairs;

            Translate.from_langs = [];
            Translate.to_langs = [];


            for(var idx in data.pairs) {
                var pair = data.pairs[idx];

                if(Translate.from_langs.indexOf(pair[0]) < 0)
                    Translate.from_langs.push(pair[0]);

                if(Translate.to_langs.indexOf(pair[1]) < 0)
                    Translate.to_langs.push(pair[1]);
            }

            Translate.from_langs = Translate.from_langs.sort();
            Translate.to_langs = Translate.to_langs.sort();
        }
    });
};

Translate.getToChoices = function(from_lang) {
    var choices = [];

    for(var idx in Translate.pairs) {
        var pair = Translate.pairs[idx];

        if(pair[0] == from_lang) {
            if(choices.indexOf(pair[1]) < 0) {
                choices.push(pair[1]);
            }
        }
    }

    return choices.sort();
};

Translate.getFromChoices = function(to_lang) {
    var choices = [];

    for(var idx in Translate.pairs) {
        var pair = Translate.pairs[idx];

        if(pair[1] == to_lang) {
            if(choices.indexOf(pair[0]) < 0) {
                choices.push(pair[0]);
            }
        }
    }

    return choices.sort();
};

Translate.translateText = function(text, from_lang, to_lang) {
    $("#to_area").html("...");

    var params = 'from=' + from_lang;
    params += '&to=' + to_lang;
    params += '&text=' + encodeURIComponent(text);

    $.ajax({
        url: '/api/v1/translate?' + params,
        dataType: 'json',
        error: function(xhr) {
            var data = JSON.parse(xhr.responseText);

            Translate.error("<b>" + (data.method || "Malformed response") +
                            "</b> " +
                            (data.message || "Malformed response"));
        },
        success: function(data) {
        // success
        if('result' in data) {
            $("#to_area").html(data.result);
            $('#used-translator').css("visibility: visible;");
            $('#translator').text(data.translator)
        }

        // error
        else {
            Translate.error("<b>" + (data.method || "Malformed response") +
                            "</b> " +
                            (data.message || "Malformed response"));
        }
    }});
};


Translate.error = function(message) {
    $("#flash").html('<div class="notice error">' +
                     '<i class="icon-warning-sign icon-large"></i>' +
                     message +
                     '<a href="#close" class="icon-remove"></a></div>');
};
