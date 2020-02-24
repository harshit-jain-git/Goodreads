
(function () {
    "use strict";

    var socket = io.connect('http://' + document.domain + ':' + location.port);
	var filesendbutton = document.getElementById('file-send-button');
    var input = document.getElementById('file-1'),
    file;

    $('#file-1').change(function() {
        file = input.files[0];
        $('#file-desc').text(file.name);
    });


})(jQuery);
