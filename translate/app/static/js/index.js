"use strict";

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

    return choices;
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

    return choices;
};

Translate.translateText = function(text, from_lang, to_lang) {
};
