(function() {
	var socket = io.connect('http://' + document.domain + ':' + location.port);
    $.getScript("https://cdnjs.cloudflare.com/ajax/libs/bootbox.js/5.4.0/bootbox.min.js");
    
    var x = $(location).attr('href');
    x = x.split('/');
    var author_id = x[x.length - 1];
    author_id = author_id.replace('#', '');

    console.log(author_id)

    $(document).on('click', '#logout', function(){
        console.log("logout request");
        socket.emit('logout_request');
    });

    socket.on('logged_out', function(){
        bootbox.alert("Logged out successfully!");
        setTimeout(function(){
            window.location = 'http://' + document.domain + ':' + location.port + '/';
        }, 3000);
    });

    socket.emit('get_author_details', author_id);

    socket.on('author_details', function(rows){
        var text = $('#author_name').text();
        text += rows[0];
        $('#author_name').text(text);

        var text = $('#rating').text();
        text += rows[1];
        $('#rating').text(text);

        var text = $('#books_written').text();
        text += rows[2];
        $('#books_written').text(text);

        var text = $('#review_count').text();
        text += rows[3];
        $('#review_count').text(text);

        var html = ''
        for (e of rows[4]) {
            html += '<div class="col-lg-2 col-md-3 col-4"> <a href="#" class="d-block mb-3 h-100"> <img class="img-fluid img-thumbnail" height = "300px" width = "300px" src="' + e[1] + '" alt=""><p>' + e[0] + '</p><p> Readers: ' + e[2] + '</p></a></div>'
        }
        
        document.getElementById('books').innerHTML = html;
    });



})(jQuery);